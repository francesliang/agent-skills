"""Offline checks: speaker assignment, audio decoding and resumable assembly."""
import base64
import argparse
import array
import io
import json
from pathlib import Path
import tempfile
import unittest
import urllib.error
from unittest.mock import patch

import gemini_tts as tts


class TtsTests(unittest.TestCase):
    def test_intro_has_music_lead_ducks_and_preserves_speech_tail(self):
        speech = array.array('h', [10000]) * (12 * tts.RATE)
        music = array.array('h', [10000]) * (9 * tts.RATE)
        with patch.object(tts.sys, 'byteorder', 'little'):
            mixed = array.array('h', tts.mix_intro(speech.tobytes(), music.tobytes()))
        self.assertEqual(len(mixed), 14 * tts.RATE)
        self.assertAlmostEqual(mixed[tts.RATE], 4500, delta=1)
        self.assertAlmostEqual(mixed[3 * tts.RATE], 9700, delta=1)
        self.assertEqual(mixed[10 * tts.RATE:], speech[8 * tts.RATE:])
        loud = array.array('h', [32767]) * (9 * tts.RATE)
        with patch.object(tts.sys, 'byteorder', 'little'):
            mixed = array.array('h', tts.mix_intro(loud.tobytes(), loud.tobytes()))
        self.assertLessEqual(max(mixed), 32767)
        self.assertLess(mixed[3 * tts.RATE], 32767)

    def test_duration_limit_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'script.md'
            output = Path(folder) / 'podcast.m4a'
            source.write_text('Hello.')
            output.write_bytes(b'previous episode')
            argv = ['gemini_tts.py', str(source), '--no-intro-music', '--overwrite']
            with patch('sys.argv', argv), patch.dict('os.environ', {'GEMINI_API_KEY': 'test'}), \
                    patch.object(tts, 'find_encoder', return_value='afconvert'), \
                    patch.object(tts, 'RATE', 10), patch.object(tts, 'MAX_SECONDS', 900), \
                    patch.object(tts, 'generate', return_value=b'\0\0' * 9001), \
                    patch.object(tts, 'save_m4a') as encode:
                with self.assertRaisesRegex(ValueError, 'exceeding'):
                    tts.main()
                encode.assert_not_called()
                self.assertEqual(output.read_bytes(), b'previous episode')

    def test_host_voices_preserve_labels_and_verbatim_transcript(self):
        transcript = "Speaker1: I'm Maya.\n\nSpeaker2: And I'm Jax."
        args = argparse.Namespace(two_speakers=True, voice=tts.DEFAULT_VOICE, voice2=tts.DEFAULT_VOICE2)
        body = tts.request_body(transcript, args)
        voices = body['generationConfig']['speechConfig']['multiSpeakerVoiceConfig']['speakerVoiceConfigs']
        self.assertEqual([(v['speaker'], v['voiceConfig']['prebuiltVoiceConfig']['voiceName']) for v in voices],
                         [('Speaker1', 'Callirrhoe'), ('Speaker2', 'Puck')])
        self.assertEqual(body['contents'][0]['parts'][0]['text'].split('TRANSCRIPT:\n', 1)[1], transcript)
        args.voice, args.voice2 = 'Kore', 'Charon'
        voices = tts.request_body(transcript, args)['generationConfig']['speechConfig']['multiSpeakerVoiceConfig']['speakerVoiceConfigs']
        self.assertEqual([v['voiceConfig']['prebuiltVoiceConfig']['voiceName'] for v in voices], ['Kore', 'Charon'])
        args.two_speakers = False
        single = tts.request_body('A single narrator.', args)
        self.assertEqual(single['generationConfig']['speechConfig'],
                         {'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': 'Kore'}}})

    @staticmethod
    def http_error(code=429, details=None, headers=None):
        body = {'error': {'message': 'private server message', 'details': details or []}}
        return urllib.error.HTTPError('https://example.invalid', code, 'error', headers or {},
                                      io.BytesIO(json.dumps(body).encode()))

    def test_retry_respects_server_hint_then_succeeds(self):
        error = self.http_error(details=[{'@type': 'type.googleapis.com/google.rpc.RetryInfo',
                                          'retryDelay': '45.5s'}], headers={'Retry-After': '40'})
        result = {'candidates': [{'finishReason': 'STOP', 'content': {'parts': [
            {'inlineData': {'mimeType': 'audio/L16;rate=24000', 'data': 'AQA='}}]}}]}
        with patch('urllib.request.urlopen', side_effect=[error, io.BytesIO(json.dumps(result).encode())]), \
                patch.object(tts.time, 'sleep') as sleep:
            self.assertEqual(tts.generate({}, 'secret', 1, 1), b'\x01\x00')
        sleep.assert_called_once_with(45.5)

    def test_exhausted_retries_report_quota_without_secrets(self):
        details = [{'@type': 'type.googleapis.com/google.rpc.QuotaFailure', 'violations': [
            {'quotaMetric': 'requests', 'quotaId': 'RequestsPerDay-secret', 'quotaValue': '15'}]}]
        errors = [self.http_error(details=details) for _ in range(3)]
        with patch('urllib.request.urlopen', side_effect=errors) as request, \
                patch.object(tts.time, 'sleep') as sleep, patch('sys.stderr', new_callable=io.StringIO) as stderr:
            with self.assertRaises(RuntimeError) as raised:
                tts.generate({}, 'secret', 2, 1, retry_delay=10, max_retry_delay=15)
        self.assertEqual(request.call_count, 3)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [10, 15])
        output = str(raised.exception) + stderr.getvalue()
        self.assertIn('quotaValue=15', output)
        self.assertIn('RequestsPerDay-[redacted]', output)
        self.assertNotIn('secret', output)
        self.assertNotIn('private server message', output)

    def test_long_server_wait_and_nonretryable_error_stop(self):
        for error in [self.http_error(headers={'Retry-After': '3600'}), self.http_error(code=403)]:
            with self.subTest(code=error.code), patch('urllib.request.urlopen', side_effect=error) as request, \
                    patch.object(tts.time, 'sleep') as sleep:
                with self.assertRaises(RuntimeError):
                    tts.generate({}, 'secret', 6, 1)
                request.assert_called_once()
                sleep.assert_not_called()

    def test_split_preserves_dialogue_voice_and_words(self):
        text = 'Speaker1: ' + 'Hello world. ' * 50 + '\nSpeaker2: Goodbye.'
        chunks = tts.make_chunks(text, True, 100)
        self.assertTrue(all(len(c) <= 100 for c in chunks))
        joined = '\n'.join(chunks)
        self.assertEqual(joined.count('Hello world.'), 50)
        self.assertTrue(all(c.startswith('Speaker1:') for c in chunks[:-1]))
        self.assertIn('Speaker2: Goodbye.', chunks[-1])

    def test_audio_response_and_reject_truncation(self):
        pcm = b'\x01\x00' * 100
        result = {'candidates': [{'finishReason': 'STOP', 'content': {'parts': [
            {'inlineData': {'mimeType': 'audio/L16;codec=pcm;rate=24000',
                            'data': base64.b64encode(pcm).decode()}}]}}]}
        with patch('urllib.request.urlopen', return_value=io.BytesIO(json.dumps(result).encode())):
            self.assertEqual(tts.generate({}, 'test-not-a-key', 0, 1), pcm)
        result['candidates'][0]['finishReason'] = 'MAX_TOKENS'
        with patch('urllib.request.urlopen', return_value=io.BytesIO(json.dumps(result).encode())):
            with self.assertRaises(RuntimeError):
                tts.generate({}, 'test-not-a-key', 0, 1)

    def test_cli_cache_resumes_without_requests(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'script.md'
            output = Path(folder) / 'podcast.m4a'
            source.write_text('Hello world. ' * 40)
            argv = ['gemini_tts.py', str(source), '--chunk-chars', '100', '--pause', '0', '--no-intro-music']
            pcm = b'\x01\x00' * 100
            with patch('sys.argv', argv), patch.dict('os.environ', {'GEMINI_API_KEY': 'test'}), \
                    patch.object(tts, 'find_encoder', return_value='afconvert'), \
                    patch.object(tts, 'save_m4a', side_effect=lambda p, pcm, encoder: p.write_bytes(pcm)):
                with patch.object(tts, 'generate', return_value=pcm) as generate:
                    tts.main()
                    self.assertGreater(generate.call_count, 0)
                original = output.read_bytes()
                output.unlink()
                with patch.object(tts, 'generate', side_effect=AssertionError('Cache missed')):
                    tts.main()
                self.assertEqual(output.read_bytes(), original)
                self.assertGreater(output.stat().st_size, 0)
                self.assertEqual(list(Path(folder).rglob('*.wav')), [])

    def test_encoding_failure_leaves_no_wav_or_final_file(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'podcast.m4a'
            with patch('subprocess.run') as run:
                run.return_value.returncode = 1
                run.return_value.stderr = 'encoder failed'
                with self.assertRaisesRegex(RuntimeError, 'encoder failed'):
                    tts.save_m4a(output, b'\x00\x00' * 100, 'afconvert')
            self.assertEqual(list(Path(folder).iterdir()), [])


if __name__ == '__main__':
    unittest.main()
