---
name: update-open-memo
description: Git update skill for the open_memo repository. Repo must be located at `/Users/kentchiu/Documents/Github/open_memo`. Always use this skill when the user asks to update the open_memo project.
---

# Intro

This skill automates the process of syncing nanobot data and updating the `open_memo` repository.

## Just Running the Script - The only way

```bash
# Set a custom commit message if provided by the user
bash /scripts/update.sh "Your commit message"
```

If no message is provided, the script defaults to "update".

## What Script Will Do

- Syncs `cron-jobs.json` from `~/.nanobot/cron/` to `webapp/content/nanobot-status/`.
- Syncs `MEMORY.md` from `~/.nanobot/workspace/memory/` to `webapp/content/nanobot-status/`.
- Executes `git add`, `git commit`, and `git push` for the `open_memo` repository.
