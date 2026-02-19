# Memory

## Key Facts

- User workspace: `/Users/kentchiu/.nanobot/workspace`
- System: macOS arm64, Python 3.13.5
- Chat channel: Telegram (Chat ID: 6291416524)
- `uv` is installed (user confirmed environment ready for testing)
- Missing `SKILL.md` files detected across multiple nanobot skills, including `tmux` (disabled)
- Voice transcription using Whisper `base` model confirmed working locally (~3.9s load and inference time), no API keys required
- Daily cron job ID `bfd4c3bf` created for 8:30 AM Vancouver time to summarize AI news from Reuters (URL: https://www.reuters.com/technology/artificial-intelligence)
- Reuters AI news summarization: direct scraping blocked (401 Forbidden); fallback plan implemented starting 2026-02-19 — use Reuters search endpoint (`https://www.reuters.com/search/news?blob=artificial+intelligence`) as primary source; Google News as secondary fallback if search also blocked

## Recent Session Goals

- Successfully commit and push architecture documentation (`nanobot_architecture_analysis.md`, `nanobot-architecture.json`) to `open_memo` repo
- Test local Whisper voice transcription pipeline
- Plan and deploy daily news summarization cron job for Reuters AI section
- Update long-term memory with new cron job setup and test execution plan
- Migrate Reuters AI news summarization to use search endpoint due to scraping blocks

## Long Term Goals

- Help main user (KentChiu) from High Net Worth Individual (HNWI) to Ultra High Net Worth Individual (UHNWI)

## Known Issues

- Web search tools require API keys (Brave Search / Google Custom Search) — blocking Reuters AI scraping without workaround
- Some skill manifests missing `SKILL.md` files (e.g., `tmux`)
- Whisper transcription accuracy may benefit from preprocessing (noise reduction, silence trimming)
- Reuters search endpoint reliability should be verified; Google News used as backup

## Key Knowledge

- when user asking to git update the open_memo repo, always use the skill and run the script.
- when SKILL.md files are missing and CLI reinstall is blocked, manually implement missing scripts using standard patterns and `uv` runtime
- Whisper transcription is functional locally with `base` model, supporting offline voice note processing
- For Reuters AI news summarization, cron job `bfd4c3bf` runs daily at 8:30 AM Vancouver time using `requests` to fetch `https://www.reuters.com/search/news?blob=artificial+intelligence`; if that fails, fallback to Google News (`https://news.google.com/search?q=artificial%20intelligence&hl=en-US&gl=US&ceid=US:en`)
- Summaries from cron job should be logged in `memory/MEMORY.md` to capture key insights (e.g., breakthrough models, regulatory updates)