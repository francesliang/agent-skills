#!/usr/bin/env python3
"""Read Markdown aloud with Gemini TTS and save podcast.m4a. Python 3.10+, no packages."""
import argparse
import base64
import binascii
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import wave

MODEL = 'gemini-2.5-flash-preview-tts'
RATE = 24000
audio_file_name = "podcast.m4a"


def clean_markdown(text):
    """Conservative prose cleanup; fenced code and images are not narrated."""
    text = re.sub(r'^```[^\n]*\n.*?^```[^\n]*$', '', text, flags=re.M | re.S)
    text = re.sub(r'!\[[^\]]*\]\([^\n]*?\)', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^\n]*?\)', r'\1', text)
    text = re.sub(r'^\s{0,3}#{1,6}\s+', '', text, flags=re.M)
    text = re.sub(r'^\s*>\s?', '', text, flags=re.M)
    text = re.sub(r'^\s*(?:[-+*]|\d+[.)])\s+', '', text, flags=re.M)
    text = re.sub(r'^\s*(?:---+|\*\*\*+|___+)\s*$', '', text, flags=re.M)
    text = re.sub(r'\*\*(.*?)\*\*|__(.*?)__', lambda m: m[1] or m[2], text)
    text = text.replace('`', '')
    return text.strip()


def split_text(text, limit):
    """Split at sentence/word boundaries, never dropping input characters."""
    result = []
    while len(text) > limit:
        candidates = [m.end() for m in re.finditer(r'[.!?][\s]+', text[:limit])]
        cut = candidates[-1] if candidates else text.rfind(' ', 0, limit)
        if cut <= 0:
            cut = limit
        result.append(text[:cut].strip())
        text = text[cut:].strip()
    if text:
        result.append(text)
    return result


def make_chunks(text, two_speakers, limit):
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    turns = []
    if two_speakers:
        labelled = bool(re.search(r'^Speaker[12]:', text, re.M))
        if labelled:
            current, lines = None, []
            for line in text.splitlines():
                match = re.match(r'^Speaker([12]):\s*(.*)', line)
                if match:
                    if current is not None:
                        turns.append((current, '\n'.join(lines).strip()))
                    current, lines = match[1], [match[2]]
                elif line.strip() or lines:
                    if current is None and line.strip():
                        raise ValueError('In labelled dialogue, start with Speaker1: or Speaker2:.')
                    lines.append(line)
            if current is not None:
                turns.append((current, '\n'.join(lines).strip()))
        else:
            turns = [(str(i % 2 + 1), p) for i, p in enumerate(paragraphs)]
    else:
        turns = [(None, p) for p in paragraphs]
    units = []
    for speaker, body in turns:
        prefix = f'Speaker{speaker}: ' if speaker else ''
        for part in split_text(body, limit - len(prefix)):
            units.append(prefix + part)
    chunks, current = [], ''
    for unit in units:
        if current and len(current) + 2 + len(unit) > limit:
            chunks.append(current)
            current = ''
        current = current + '\n\n' + unit if current else unit
    if current:
        chunks.append(current)
    return chunks


def request_body(text, args):
    def voice(name):
        return {'prebuiltVoiceConfig': {'voiceName': name}}
    speech = {'voiceConfig': voice(args.voice)}
    if args.two_speakers:
        speech = {'multiSpeakerVoiceConfig': {'speakerVoiceConfigs': [
            {'speaker': 'Speaker1', 'voiceConfig': voice(args.voice)},
            {'speaker': 'Speaker2', 'voiceConfig': voice(args.voice2)},
        ]}}
    prompt = ('Read the following transcript aloud exactly as written, in English. '
              'Do not summarise, add commentary, introduce the transcript, or omit sentences. '
              'Speaker labels identify voices and must not be spoken. '
              'Use a natural, clear news-podcast delivery.\n\nTRANSCRIPT:\n' + text)
    return {'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {
        'responseModalities': ['AUDIO'], 'speechConfig': speech}}


def generate(body, key, retries, timeout):
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent'
    for attempt in range(retries + 1):
        request = urllib.request.Request(url, data=json.dumps(body).encode(), headers={
            'Content-Type': 'application/json', 'x-goog-api-key': key})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                result = json.load(response)
            break
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == retries:
                # Avoid printing server bodies or request details containing credentials.
                detail = {400: 'Invalid request or voice configuration.',
                          403: 'Check your API key, project access and region.',
                          404: 'The configured TTS model is unavailable.',
                          429: 'Quota exhausted. Wait and resume; daily quotas may need a later retry.'}
                raise RuntimeError(f'Gemini HTTP {exc.code}. ' + detail.get(exc.code, 'Request failed.')) from None
            delay = min(120, 15 * 2 ** attempt)
            print(f'HTTP {exc.code}; retrying in {delay}s...', file=sys.stderr)
            time.sleep(delay)
    candidates = result.get('candidates', [])
    if not candidates or candidates[0].get('finishReason') != 'STOP':
        raise RuntimeError('Gemini did not finish normally. No partial audio was saved; retry this section.')
    audio = []
    for part in candidates[0].get('content', {}).get('parts', []):
        inline = part.get('inlineData', {})
        if not inline.get('data'):
            continue
        mime = inline.get('mimeType', '')
        if not mime.startswith('audio/L16') or not re.search(r'rate=24000(?:;|$)', mime):
            raise RuntimeError(f'Unexpected audio format: {mime!r}; expected 24 kHz PCM.')
        audio.append(base64.b64decode(inline['data'], validate=True))
    pcm = b''.join(audio)
    if not pcm or len(pcm) % 2:
        raise RuntimeError('Missing or invalid PCM audio in the response.')
    return pcm


def find_encoder():
    if sys.platform == 'darwin' and shutil.which('afconvert'):
        return 'afconvert'
    if shutil.which('ffmpeg'):
        return 'ffmpeg'
    raise RuntimeError('M4A encoding requires afconvert on macOS or ffmpeg on PATH.')


def save_m4a(path, pcm, encoder):
    # Only the final M4A persists; intermediate audio is removed on success or error.
    with tempfile.TemporaryDirectory(dir=path.parent) as folder:
        source = Path(folder) / 'input.wav'
        encoded = Path(folder) / audio_file_name
        with wave.open(str(source), 'wb') as wav:
            wav.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
            wav.writeframes(pcm)
        if encoder == 'afconvert':
            command = ['afconvert', '-f', 'm4af', '-d', 'aac', '-b', '64000',
                       str(source), str(encoded)]
        else:
            command = ['ffmpeg', '-nostdin', '-v', 'error', '-i', str(source),
                       '-c:a', 'aac', '-b:a', '64k', '-movflags', '+faststart', str(encoded)]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode or not encoded.is_file() or not encoded.stat().st_size:
            raise RuntimeError('M4A encoding failed: ' + result.stderr.strip())
        encoded.replace(path)


def save_pcm(path, pcm):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as tmp:
        temporary = Path(tmp.name)
        try:
            tmp.write(pcm)
            tmp.close()
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('script', type=Path)
    parser.add_argument('-o', '--output', type=Path, help=f'Output path named {audio_file_name} (default: next to input)')
    parser.add_argument('--two-speakers', action='store_true', help='Use Speaker1:/Speaker2: labels, or alternate paragraphs')
    parser.add_argument('--voice', default='Kore', help='Narrator / Speaker1 voice (default: Kore)')
    parser.add_argument('--voice2', default='Puck', help='Speaker2 voice (default: Puck)')
    parser.add_argument('--chunk-chars', type=int, default=2500)
    parser.add_argument('--pause', type=float, default=15, help='Seconds between uncached requests')
    parser.add_argument('--retries', type=int, default=3)
    parser.add_argument('--timeout', type=float, default=240)
    parser.add_argument('--dry-run', action='store_true', help='Prepare and report sections without API calls')
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()
    if args.chunk_chars < 100 or args.pause < 0 or args.retries < 0 or args.timeout <= 0:
        parser.error('Use chunk-chars >= 100, pause/retries >= 0 and timeout > 0.')
    output = args.output or args.script.with_name(audio_file_name)
    if output.name != audio_file_name:
        parser.error(f'Output filename must be {audio_file_name}.')
    if output.resolve() == args.script.resolve():
        parser.error('Output must differ from input.')
    text = clean_markdown(args.script.read_text(encoding='utf-8'))
    chunks = make_chunks(text, args.two_speakers, args.chunk_chars)
    if not chunks:
        parser.error('No spoken text found.')
    print(f'{len(text.split())} words; {len(chunks)} sections; model: {MODEL}')
    if args.dry_run:
        for i, chunk in enumerate(chunks, 1):
            print(f'  Section {i}: {len(chunk)} characters')
        return
    if output.exists() and not args.overwrite:
        parser.error(f'Output exists: {output}. Use --overwrite to replace it.')
    encoder = find_encoder()
    key = os.environ.get('GEMINI_API_KEY')
    if not key:
        parser.error('Set GEMINI_API_KEY using a Google AI Studio free-tier project key.')
    print('Billing follows your Google project tier; this script cannot enforce free-tier billing.')
    output.parent.mkdir(parents=True, exist_ok=True)
    cache = output.parent / '.gemini-tts-cache'
    cache.mkdir(exist_ok=True)
    all_pcm, requested = [], False
    for i, chunk in enumerate(chunks, 1):
        body = request_body(chunk, args)
        digest = hashlib.sha256((MODEL + json.dumps(body, sort_keys=True)).encode()).hexdigest()
        cached = cache / f'{digest}.pcm'
        if cached.exists():
            print(f'Section {i}/{len(chunks)}: using cache')
            pcm = cached.read_bytes()
            if not pcm or len(pcm) % 2:
                raise ValueError(f'Invalid cached PCM: {cached}')
        else:
            if requested:
                time.sleep(args.pause)
            print(f'Section {i}/{len(chunks)}: generating...', flush=True)
            pcm = generate(body, key, args.retries, args.timeout)
            save_pcm(cached, pcm)
            requested = True
        all_pcm.append(pcm)
    save_m4a(output, b''.join(all_pcm), encoder)
    seconds = sum(map(len, all_pcm)) / (RATE * 2)
    print(f'Saved {output.resolve()} ({seconds / 60:.1f} minutes)')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError, binascii.Error) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print('\nInterrupted. Completed sections are cached; rerun to resume.', file=sys.stderr)
        sys.exit(130)
