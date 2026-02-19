# Memory

## Key Facts

- User workspace: `/Users/kentchiu/.nanobot/workspace`
- System: macOS arm64, Python 3.13.5
- Chat channel: Telegram (Chat ID: 6291416524)
- Audio file location (Telegram voice note): `/Users/kentchiu/.nanobot/media/AwACAgUAAxkBAAMt.ogg`
- Skill location: `/Users/kentchiu/.nanobot/workspace/skills/voice-transcribe`
- OpenAI API key is configured in `/Users/kentchiu/.nanobot/workspace/skills/voice-transcribe/.env`
- `uv` is installed (user confirmed environment ready for testing)

## Recent Session Goals

- Test voice understanding capability using nanobot skills  
- Run `open_memo-git-update.sh` (repo already up to date)  
- Verify `voice-transcribe` skill readiness and dependencies  
- Prepare to execute `transcribe.py` on Telegram audio file

## Long Term Goals

- Help main user (KentChiu) from High Net Worth Individual (HNWI) to Ultra High Net Worth Individual (UHNWI)

## Known Issues

- Web search tools require API keys (Brave Search / Google Custom Search)
- Some skill manifests missing `SKILL.md` files (e.g., `tmux` disabled due to missing `tmux` CLI)
- Voice transcription pending successful execution of `transcribe.py` on test audio

## Key Knowledge

- when user asking to git update the open_memo repo, always use the skill and run the script.
- voice-transcribe skill uses local Whisper model by default but may fall back to OpenAI API if configured
