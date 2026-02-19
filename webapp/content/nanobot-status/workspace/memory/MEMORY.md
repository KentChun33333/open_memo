# Memory

## Key Facts

- User workspace: `/Users/kentchiu/.nanobot/workspace`
- System: macOS arm64, Python 3.13.5
- Chat channel: Telegram (Chat ID: 6291416524)
- `uv` is installed (user confirmed environment ready for testing)
- Missing `SKILL.md` files detected across multiple nanobot skills, including `tmux` (disabled)
- Voice transcription using Whisper `base` model confirmed working locally (~3.9s load and inference time), no API keys required
- User requested cron job for daily 8:30 AM Reuters AI news summary (to be implemented)

## Recent Session Goals

- Successfully commit and push architecture documentation (`nanobot_architecture_analysis.md`, `nanobot-architecture.json`) to `open_memo` repo
- Test local Whisper voice transcription pipeline
- Plan daily news summarization cron job for Reuters AI section

## Long Term Goals

- Help main user (KentChiu) from High Net Worth Individual (HNWI) to Ultra High Net Worth Individual (UHNWI)

## Known Issues

- Web search tools require API keys (Brave Search / Google Custom Search) — blocking Reuters AI scraping without workaround
- Some skill manifests missing `SKILL.md` files (e.g., `tmux`)
- Whisper transcription accuracy may benefit from preprocessing (noise reduction, silence trimming)

## Key Knowledge

- when user asking to git update the open_memo repo, always use the skill and run the script.
- when SKILL.md files are missing and CLI reinstall is blocked, manually implement missing scripts using standard patterns and `uv` runtime
- Whisper transcription is functional locally with `base` model, supporting offline voice note processing
- For Reuters AI news summarization, need to build a cron-compatible script using `requests` (no API key needed for HTML scraping) or fallback to web search tools once keys are provisioned