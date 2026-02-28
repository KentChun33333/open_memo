#!/bin/bash
# dry_run.sh
# Connects the bot in an environment where orders are monitored but not actually sent.
export RUST_LOG=info
source $HOME/.cargo/env
cd /Users/kentchiu/.nanobot/workspace/openmemo/polymarket-bot
cargo run
