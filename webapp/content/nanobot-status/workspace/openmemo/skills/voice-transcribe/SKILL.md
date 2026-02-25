---
name: voice-transcribe
description: Transcribe audio files (ogg, mp3, wav, m4a, opus, webm) to text using local Whisper model. Use when receiving voice memos, audio messages, or any audio file that needs speech-to-text transcription. Works fully offline with no API keys required.
---

# Voice Transcribe

Transcribe audio files locally using OpenAI Whisper. No API keys needed — runs entirely on-device.

## When to use

When a user sends a voice memo or audio file, transcribe it:

```bash
python scripts/transcribe.py <audio-file>
```

Then respond based on the transcribed content.

## Supported formats

ogg, opus, mp3, mp4, m4a, wav, webm, mpeg, mpga, flac

## Usage examples

```bash
# Basic transcription (prints text to stdout)
python scripts/transcribe.py /tmp/voice-memo.ogg

# Use a larger model for better accuracy (tiny, base, small, medium, large)
python scripts/transcribe.py /tmp/voice-memo.ogg --model small

# Specify language hint
python scripts/transcribe.py /tmp/voice-memo.ogg --language zh

# Output as JSON with timestamps
python scripts/transcribe.py /tmp/voice-memo.ogg --json

# Save to file
python scripts/transcribe.py /tmp/voice-memo.ogg --output /tmp/transcript.txt
```

## Model sizes

| Model | Size | Speed | Quality |
|-------|------|-------|---------|
| `tiny` | 39M | Fastest | Basic |
| `base` | 74M | Fast | Good (default) |
| `small` | 244M | Medium | Better |
| `medium` | 769M | Slow | Great |
| `large` | 1550M | Slowest | Best |

Default is `base` — good balance of speed and accuracy.

## Prerequisites

Install dependencies (one-time):

```bash
pip install openai-whisper
```

Requires `ffmpeg` on the system:

```bash
brew install ffmpeg   # macOS
```

## Custom vocabulary

Create a `vocab.txt` file next to the script (one word per line) to improve recognition of names/jargon. These are passed as Whisper's `initial_prompt`.

## Notes

- Fully offline — no API keys or network needed
- First run downloads the model (~74MB for base)
- Caches transcription results by file hash to avoid re-processing
- Handles Telegram voice messages (.ogg/.opus) natively
