"""Offline checks: speaker assignment, audio decoding and resumable assembly."""
import base64
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import gemini_tts as tts


class TtsTests(unittest.TestCase):
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
            argv = ['gemini_tts.py', str(source), '--chunk-chars', '100', '--pause', '0']
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
