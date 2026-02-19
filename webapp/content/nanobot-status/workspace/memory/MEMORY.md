# Memory

## Key Facts

- User workspace: `/Users/kentchiu/.nanobot/workspace`
- System: macOS arm64, Python 3.13.5
- Chat channel: Telegram (Chat ID: 6291416524)
- Audio file location (Telegram voice note): `/Users/kentchiu/.nanobot/media/AwACAgUAAxkBAANB.ogg`
- Skill location: `/Users/kentchiu/.nanobot/workspace/skills/voice-transcribe`
- OpenAI API key is configured in `/Users/kentchiu/.nanobot/workspace/skills/voice-transcribe/.env`
- `uv` is installed (user confirmed environment ready for testing)
- Missing `SKILL.md` files detected across multiple nanobot skills, including `tmux` (disabled) and `voice-transcribe`
- `voice-transcribe` skill requires manual `transcribe.py` implementation pending script creation

## Recent Session Goals

- Identify root cause of missing `SKILL.md` files and propose recovery path
- Prepare to manually write `transcribe.py` script for `voice-transcribe` skill
- Test manual transcription script on latest Telegram voice note (`AwACAgUAAxkBAANB.ogg`)

## Long Term Goals

- Help main user (KentChiu) from High Net Worth Individual (HNWI) to Ultra High Net Worth Individual (UHNWI)

## Known Issues

- Web search tools require API keys (Brave Search / Google Custom Search)
- Some skill manifests missing `SKILL.md` files (e.g., `tmux`, `voice-transcribe`)
- Manual `transcribe.py` script pending creation for `voice-transcribe` skill
- Voice transcription not yet executed due to incomplete skill setup

## Key Knowledge

- when user asking to git update the open_memo repo, always use the skill and run the script.
- voice-transcribe skill uses local Whisper model by default but may fall back to OpenAI API if configured
- when SKILL.md files are missing and CLI reinstall is blocked, manually implement missing scripts using standard patterns and `uv` runtime
- user prefers direct execution over waiting for external fixes unless explicitly requested