#!/bin/bash
# Fast git update script for open_memo repository
# Usage: ./open_memo-git-update.sh [commit_message]

set -e

REPO_PATH="/Users/kentchiu/Documents/Github/open_memo"
NANOBOT_CONTENT="$REPO_PATH/webapp/content/nanobot-status"

# Sync nanobot data into webapp content
mkdir -p "$NANOBOT_CONTENT"
cp -rf ~/.nanobot/cron "$NANOBOT_CONTENT/"
cp -rf ~/.nanobot/workspace "$NANOBOT_CONTENT/"
echo "Synced nanobot data → $NANOBOT_CONTENT"

# Change to repo directory
cd "$REPO_PATH"

# Add all changes
git add .

# Check if there are any changes
if git diff --cached --quiet; then
    echo "No changes to commit."
    exit 0
fi

# Commit with provided message or default
if [ -n "$1" ]; then
    COMMIT_MSG="$1"
else
    COMMIT_MSG="update"
fi

git commit -m "$COMMIT_MSG"

# Push to remote
git push origin main

echo "Successfully updated open_memo repository"
