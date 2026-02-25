---
title: "Master Guide: Terminating Persistent AI Agents on macOS"
date: "2026-02-22"
tags: ["macos", "agents", "troubleshooting", "process-management", "open_memo"]
summary: "When building agentic frameworks like OpenClaw or open_memo, processes often become immortal by registering with the macOS kernel. Learn how to perform a clean kill and deep exorcism."
---

When building agentic frameworks like OpenClaw or open_memo, processes often become "immortal" because they register themselves with the macOS kernel. Deleting the folder is not enough; you must de-register the service.

## Phase 1: The "Clean Kill" (Memory & Network)

First, identify exactly what is holding the port and kill the process in RAM.

**Identify by Port:**
Find the Process ID (PID) specifically using the port 18789:

```bash
lsof -i :18789
```

**Trace the Parent:**
If it keeps coming back, find out who is "spawning" it. If the PPID is 1, macOS is the one restarting it:

```bash
ps -o ppid= -p $(lsof -ti:18789) | xargs ps -p
```

**The Force Kill:**

```bash
kill -9 [PID]
```

## Phase 2: The "Exorcism" (System Registration)

If the process respawns, macOS has a LaunchAgent cached in memory. You must unload the instructions.

**Locate the Files:**
Check these three critical paths for `.plist` files (e.g., `com.clawdbot.gateway.plist`):

- `~/Library/LaunchAgents/` (User level)
- `/Library/LaunchAgents/` (System level)
- `/Library/LaunchDaemons/` (Root level)

**Unregister the Job:**
Even if you delete the file, the job stays in the launchd database. Find the label and remove it:

```bash
launchctl list | grep -i "claw"
launchctl remove [label_name]
```

**Permanent Deletion:**

```bash
rm -rf ~/Library/LaunchAgents/com.clawdbot.gateway.plist
```

## Phase 3: The "Deep Clean" (Global Binaries)

Since you are a lead dev, you likely have global packages that might still be active.

**Node.js:** Check for globally installed bots:

```bash
npm list -g --depth=0
```

**PM2:** If you use a process manager, it will restart the bot forever until killed:

```bash
pm2 delete all
```

**Docker:** Ensure no containers are mapped to your dev ports:

```bash
docker ps
```

## Summary Checklist for Future "Zombies"

| Symptom | Cause | Solution |
| :--- | :--- | :--- |
| Port 18789 is busy | Process is running in RAM | `kill -9 [PID]` |
| Process returns after kill | launchd "KeepAlive" is active | `launchctl remove [label]` |
| Code is deleted but it runs | Binary is in global /bin or RAM | `which [app]` and `killall node` |
| Browser still shows chat | Service Worker/Cache | Cmd+Shift+R or clear Service Workers |

## Pro-Tip for open_memo

To avoid this in the future, I recommend running your local agents inside a Docker container or using a Python Virtual Environment with a specific `stop.sh` script. This keeps the system-level LaunchAgents folder clean.

*Would you like me to draft a `cleanup.sh` script for your repository that automates these steps for your team?*
