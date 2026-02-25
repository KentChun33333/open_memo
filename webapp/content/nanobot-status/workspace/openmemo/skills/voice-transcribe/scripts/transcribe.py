#!/usr/bin/env python3
"""
Voice transcription using OpenAI Whisper (local, offline).
Supports: ogg, opus, mp3, mp4, m4a, wav, webm, mpeg, mpga, flac

Usage:
    python transcribe.py <audio-file> [--model base] [--language en] [--json] [--output file.txt]
"""

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

# Cache directory for transcription results
CACHE_DIR = Path(__file__).parent / ".cache"
VOCAB_FILE = Path(__file__).parent / "vocab.txt"

SUPPORTED_FORMATS = {
    ".ogg", ".opus", ".mp3", ".mp4", ".m4a",
    ".wav", ".webm", ".mpeg", ".mpga", ".flac",
}


def get_file_hash(filepath: str) -> str:
    """SHA256 hash of audio file for caching."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def get_cached(file_hash: str, model_name: str) -> dict | None:
    """Check if transcription is cached."""
    cache_file = CACHE_DIR / f"{file_hash}_{model_name}.json"
    if cache_file.exists():
        with open(cache_file) as f:
            return json.load(f)
    return None


def save_cache(file_hash: str, model_name: str, result: dict) -> None:
    """Save transcription result to cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{file_hash}_{model_name}.json"
    with open(cache_file, "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def load_vocab() -> str:
    """Load custom vocabulary hints from vocab.txt."""
    if VOCAB_FILE.exists():
        words = VOCAB_FILE.read_text().strip().splitlines()
        words = [w.strip() for w in words if w.strip()]
        if words:
            return ", ".join(words)
    return ""


def transcribe(
    audio_path: str,
    model_name: str = "base",
    language: str | None = None,
    use_cache: bool = True,
) -> dict:
    """
    Transcribe an audio file using Whisper.

    Args:
        audio_path: Path to the audio file
        model_name: Whisper model size (tiny/base/small/medium/large)
        language: Language hint (e.g., 'en', 'zh', 'ja')
        use_cache: Whether to use cached results

    Returns:
        dict with 'text', 'segments', 'language', 'duration'
    """
    audio_path = os.path.abspath(audio_path)

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    ext = Path(audio_path).suffix.lower()
    if ext not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format: {ext}. Supported: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )

    # Check cache
    file_hash = get_file_hash(audio_path)
    if use_cache:
        cached = get_cached(file_hash, model_name)
        if cached:
            print("(using cached transcription)", file=sys.stderr)
            return cached

    # Import whisper (lazy — only when needed)
    try:
        import whisper
    except ImportError:
        print(
            "Error: openai-whisper not installed.\n"
            "Install with: pip install openai-whisper\n"
            "Also requires ffmpeg: brew install ffmpeg",
            file=sys.stderr,
        )
        sys.exit(1)

    # Load model
    print(f"Loading Whisper model '{model_name}'...", file=sys.stderr)
    start = time.time()
    model = whisper.load_model(model_name)
    print(f"Model loaded in {time.time() - start:.1f}s", file=sys.stderr)

    # Build transcription options
    options = {}
    if language:
        options["language"] = language

    vocab = load_vocab()
    if vocab:
        options["initial_prompt"] = vocab
        print(f"Using vocabulary hints: {vocab[:80]}...", file=sys.stderr)

    # Transcribe
    print(f"Transcribing: {os.path.basename(audio_path)}", file=sys.stderr)
    start = time.time()
    result = model.transcribe(audio_path, **options)
    elapsed = time.time() - start

    # Build output
    output = {
        "text": result["text"].strip(),
        "language": result.get("language", language or "unknown"),
        "duration": elapsed,
        "model": model_name,
        "file": os.path.basename(audio_path),
        "segments": [
            {
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip(),
            }
            for seg in result.get("segments", [])
        ],
    }

    # Cache result
    if use_cache:
        save_cache(file_hash, model_name, output)

    print(f"Transcribed in {elapsed:.1f}s", file=sys.stderr)
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe audio files using Whisper (local, offline)"
    )
    parser.add_argument("audio_file", help="Path to the audio file")
    parser.add_argument(
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: base)",
    )
    parser.add_argument(
        "--language",
        default=None,
        help="Language hint (e.g., en, zh, ja). Auto-detected if omitted.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output full result as JSON (with timestamps)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Save transcription to file",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Skip cache, always re-transcribe",
    )

    args = parser.parse_args()

    try:
        result = transcribe(
            args.audio_file,
            model_name=args.model,
            language=args.language,
            use_cache=not args.no_cache,
        )
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Output
    if args.json:
        text = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        text = result["text"]

    if args.output:
        Path(args.output).write_text(text + "\n")
        print(f"Saved to {args.output}", file=sys.stderr)
    else:
        print(text)


if __name__ == "__main__":
    main()
