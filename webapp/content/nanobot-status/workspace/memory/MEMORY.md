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
- **2026-02-19T19:27 update**: Reuters search endpoint also blocked (401 Forbidden). Recommended fallbacks: Google News (Reuters-filtered), BBC Tech, The Verge AI, or Reuters RSS (if available). Cron job script must be updated to use working source.
- **2026-02-19T20:32 update**: User confirmed `open_memo` repo changes are *continually evolving*; initial `openmemo-git-update.sh` execution incorrectly reported repo as up to date. Further investigation needed to identify uncommitted or unpushed changes (e.g., unstaged files, untracked docs like `nanobot_architecture_analysis.md`, `nanobot-architecture.json`, or `memory/MEMORY.md`).

## Recent Session Goals

- Successfully commit and push architecture documentation (`nanobot_architecture_analysis.md`, `nanobot-architecture.json`) to `open_memo` repo
- Test local Whisper voice transcription pipeline
- Plan and deploy daily news summarization cron job for Reuters AI section
- Update long-term memory with new cron job setup and test execution plan
- Migrate Reuters AI news summarization to use search endpoint due to scraping blocks
- **2026-02-19T20:29**: Execute `openmemo-git-update.sh` per user request to finalize and sync repository changes
- **2026-02-19T20:32**: Reassess sync status of `open_memo` repo after user feedback — uncommitted changes likely remain

## Long Term Goals

- Help main user (KentChiu) from High Net Worth Individual (HNWI) to Ultra High Net Worth Individual (UHNWI)

## Known Issues

- Web search tools require API keys (Brave Search / Google Custom Search) — blocking Reuters AI scraping without workaround
- Some skill manifests missing `SKILL.md` files (e.g., `tmux`)
- Whisper transcription accuracy may benefit from preprocessing (noise reduction, silence trimming)
- Reuters search endpoint reliability should be verified; Google News used as backup
- **2026-02-19T19:27**: Reuters search endpoint also blocked (401 Forbidden); cron job script needs to be updated to use Google News or alternative reliable scrapable sources (BBC, The Verge, RSS)
- **2026-02-19T20:32**: `open_memo` repo appears out-of-sync despite `openmemo-git-update.sh` reporting no changes; uncommitted edits or missing file tracking likely present

## Key Knowledge

- when user asking to git update the open_memo repo, always use the skill and run the script, but validate actual remote state vs local changes if feedback indicates discrepancies
- when SKILL.md files are missing and CLI reinstall is blocked, manually implement missing scripts using standard patterns and `uv` runtime
- Whisper transcription is functional locally with `base` model, supporting offline voice note processing
- For Reuters AI news summarization, cron job `bfd4c3bf` runs daily at 8:30 AM Vancouver time using `requests` to fetch `https://www.reuters.com/search/news?blob=artificial+intelligence`; if that fails (per 2026-02-19 confirmation), fallback to Google News (`https://news.google.com/search?q=artificial%20intelligence&hl=en-US&gl=US&ceid=US:en`)
- Summaries from cron job should be logged in `memory/MEMORY.md` to capture key insights (e.g., breakthrough models, regulatory updates)
- **2026-02-19T19:27**: If Reuters search endpoint blocked, prefer Google News (Reuters-filtered) or BBC Tech/The Verge AI as reliable alternative sources for AI news scraping