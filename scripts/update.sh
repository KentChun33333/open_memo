#!/bin/bash

# update.sh - Sync nanobot data and update open_memo repo
# Usage: bash scripts/update.sh "optional commit message"

set -e

# Navigate to repo root
cd /Users/kentchiu/Documents/Github/open_memo

# Sync cron-jobs.json
mkdir -p webapp/content/nanobot-status/cron
cp ~/.nanobot/cron/cron-jobs.json webapp/content/nanobot-status/cron/cron-jobs.json 2>/dev/null || echo "No cron-jobs.json found"

# Sync MEMORY.md
mkdir -p webapp/content/nanobot-status/memory
cp ~/.nanobot/workspace/memory/MEMORY.md webapp/content/nanobot-status/memory/MEMORY.md 2>/dev/null || echo "No MEMORY.md found"

# Sync workspace data if exists
if [ -d ~/.nanobot/workspace ]; then
    mkdir -p webapp/content/nanobot-status/workspace
    cp -r ~/.nanobot/workspace/* webapp/content/nanobot-status/workspace/ 2>/dev/null || echo "Workspace sync skipped"
fi

# Git operations
git add .
git commit -m "${1:-update}" || echo "No changes to commit"
git push origin main

echo "✅ open_memo repo updated successfully"
