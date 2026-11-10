# Gemini Markdown to audio

`gemini_tts.py` requires Python 3.10+ and no third-party packages. It sends cleaned text to Gemini's GenerateContent TTS endpoint and encodes the returned audio as mono AAC in `podcast.m4a` (24 kHz, 64 kbps). M4A encoding uses the built-in `afconvert` on macOS, or `ffmpeg` on other systems. No browser, file-upload service, or separate download step is needed.

## Setup

Create a key in [Google AI Studio](https://aistudio.google.com/apikey) for a **free-tier project**. Keep the key out of scripts and Git. The default model is `gemini-2.5-flash-preview-tts`, which Google's [pricing page](https://ai.google.dev/gemini-api/docs/pricing) currently lists with free input/output on the free tier. Quotas, availability and pricing can change. A billing-enabled project's key can incur charges: the API has no per-request “free only” switch. This script never falls back to another model. Free-tier content may be used to improve Google's products; consult the linked terms before sending private content.

On macOS/zsh, enter your key without putting it in shell history:

```zsh
read -s 'GEMINI_API_KEY?Gemini API key: '
export GEMINI_API_KEY
```

From this project directory:

```sh
# Inspect splitting without a key or network access.
python3 scripts/gemini_tts.py 2026-11-09/script.md --dry-run

# Read the existing monologue with a single voice.
python3 scripts/gemini_tts.py 2026-11-09/script.md

# Use Maya (Callirrhoe) and Jax (Puck), preserving the prose.
python3 scripts/gemini_tts.py 2026-11-09/script.md --two-speakers
```

The default output is `podcast.m4a` next to the input file. For an actual two-host conversation, write speaker-labelled text:

```text
Speaker1: Welcome to Morning Discovery. I'm Maya.
Speaker2: And I'm Jax. Big ideas, useful context, and a fighting chance of closing a browser tab.
Speaker1: Let's begin with the first story.
```

Then use `--two-speakers`. Labels must be exactly `Speaker1:` and `Speaker2:`, at the start of a line. In labelled mode all prose must follow a speaker label; the script preserves the assigned voice across section boundaries. Defaults are **Maya / Speaker1 / Callirrhoe** (easy-going, warm and curious) and **Jax / Speaker2 / Puck** (funny, playful and quick-witted). The TTS prompt reinforces their delivery while reading the dialogue verbatim; write their personalities and the recurring intro into the script using `SKILL.md`. In unlabelled mode it alternates at blank-line paragraph breaks. It does not rewrite a monologue into a dialogue. `--voice Callirrhoe --voice2 Puck` explicitly selects the defaults; these flags also accept other voices. See Google's [voice list and samples](https://firebase.google.com/docs/ai-logic/generate-speech?api=vertex#response-voices-list).

## Intro music

By default, the final mix uses `intro-music.m4a` in the command's working directory. Run from the publication checkout root where this track is stored. Music plays alone for five seconds, ducks beneath the first spoken words, and fades out by nine seconds. The speech keeps its natural pace. The final `podcast.m4a` includes the music; the 15-minute limit includes the five-second lead-in. Overlong output stops before replacing an existing episode.

Use `--intro-music /absolute/path/to/music.m4a` to choose a different track, or `--no-intro-music` for speech only. Music is decoded and checked before Gemini requests using the existing macOS `afconvert` or FFmpeg dependency, then mixed locally with Python's standard library. An absent or invalid configured track stops the run. Dry runs show the mixing settings without decoding music or calling Gemini.

Music is applied after assembling speech, so changing the track or remixing it reuses the same speech caches. Temporary decoded audio is removed automatically. Keep the source music outside the episode folder; publish only the finished `podcast.m4a`.

## Long scripts and retries

The script groups prose into sections of at most 2,500 characters by default (`--chunk-chars`). It waits 15 seconds between new requests (`--pause`) and retries HTTP 429 and transient server errors up to six times per section (`--retries`). Backoff starts at 30 seconds (`--retry-delay`) and doubles up to 120 seconds (`--max-retry-delay`). It respects numeric `Retry-After` and Google `RetryInfo` hints; if a server-requested wait exceeds the maximum, it stops so you can resume later instead of retrying too early. Quota metric, ID and limit value are reported when present, without logging raw error bodies or credentials. A 429 without those details does not establish daily quota exhaustion. Daily limits may require waiting until the project quota resets. Network errors stop the run; rerun to resume.

To resume with a longer bounded retry window, for example:

```sh
python3 scripts/gemini_tts.py 2026-11-09/script.md --two-speakers --retries 8 --retry-delay 30 --max-retry-delay 300
```

Completed sections are stored in `.gemini-tts-cache/` beside the output. Rerunning the same text, voices and delivery instructions reuses them without another API request. Cache filenames include a hash of the model and request configuration, so changing voices or the delivery prompt generates new sections rather than mixing different host performances. Previous caches remain intact. Keep the cache until generation succeeds. Audio files/cache can be large and are not automatically published to GitHub. Existing output files are protected unless `--overwrite` is supplied.

Generation is prompted to read the text verbatim. Generative TTS can still mispronounce, omit, or vary speech; listen to the result before publishing. Independent sections may vary in cadence. Fenced code and images are omitted; links retain their visible label. Use prose rather than Markdown tables for spoken input. The only final audio file is `podcast.m4a`, next to the input. Use `-o /another/folder/podcast.m4a` to choose a different directory; the filename is fixed. Temporary WAV data is removed after encoding, including on conversion errors. Resumable cache entries use raw `.pcm` files. Legacy WAV cache entries are no longer used. Previously generated WAV files are not deleted automatically.

Run offline checks:

```sh
python3 -m unittest discover -s scripts -p 'test_*.py'
```
