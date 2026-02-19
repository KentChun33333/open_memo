# Agent Trajectory Deep Analysis Report

**Date:** 2026-02-06  
**Duration Analyzed:** 2.5 hours (01:35 - 04:02)  
**Task:** Build MCP demo web artifact

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Duration | 2h 27m |
| Server Restarts | **~35** |
| Critical Crashes | **3** |
| Tool Calls | **~280** |
| Projects Created | **2** (duplicates) |

The agent completed the task but created **2 duplicate projects** in different folders due to severe working directory confusion.

---

## 🔴 Root Cause #1: Working Directory Chaos

The agent ran `init-artifact.sh mcp-demo` from **9 different working directories**, creating projects in:

| Location | Status |
|----------|--------|
| `/open_memo/.agent/skills/web-artifacts-builder/mcp-demo/` | Bundled ✅ |
| `/open_memo/mcp-demo/` | Bundled ✅ |
| `/open_memo/mcp_skill_agent/mcp-demo/` | Also created |

**Why:** The `init-artifact.sh` script creates projects in the current working directory. The agent never tracked which directories already had initialized projects.

---

## 🔴 Root Cause #2: Server Crashes During Long Operations

Three crashes occurred with `anyio.ClosedResourceError`:

| Time | Trigger |
|------|---------|
| 03:10:00 | `ls -la` sent during active `init-artifact.sh` |
| 03:19:39 | `ls -la mcp-demo/` sent during active script |
| 03:46:56 | `ls -la` sent during active script |

**Pattern:**

```
Agent calls init-artifact.sh (takes ~60s for npm install)
     ↓
Agent sends another command before completion
     ↓
MCP session tries to respond on closed stream
     ↓
ClosedResourceError → SERVER CRASH
     ↓
New server starts → Agent re-reads everything → Repeat
```

---

## 🔴 Root Cause #3: PostCSS Configuration Loop

The agent "fixed" the same PostCSS issue **6 times**:

```
01:36:30 - write_file .postcssrc + rm postcss.config.js
01:51:25 - write_file .postcssrc
01:56:37 - write_file .postcssrc  
02:40:12 - write_file .postcssrc
03:04:17 - write_file .postcssrc
```

**Why:** State was lost after each server restart.

---

## 📊 Efficiency Analysis

### Wasted Operations

| Operation | Repetitions | Time Wasted |
|-----------|-------------|-------------|
| `init-artifact.sh mcp-demo` | **18x** | ~18 min |
| `read_file init-artifact.sh` | **12x** | ~1 min |
| `read_file bundle-artifact.sh` | **10x** | ~1 min |
| `read_file App.tsx` | **14x** | ~1 min |
| Server restarts | **~35x** | ~5 min |

### Efficiency Potential

| Metric | Actual | Optimal | Factor |
|--------|--------|---------|--------|
| Time | 2.5 hours | 10-15 min | **10-15x** |
| Tool calls | 280 | 25-30 | **10x** |
| Server restarts | 35 | 0 | **∞** |

---

## 🛠️ Recommended Fixes

### 1. Script-Aware Timeouts in `execute_command`

```python
LONG_RUNNING_SCRIPTS = ['init-artifact.sh', 'bundle-artifact.sh', 'npm install']

async def execute_command(command: str, working_dir: Optional[str] = None) -> str:
    timeout = 60
    for script in LONG_RUNNING_SCRIPTS:
        if script in command:
            timeout = 180  # 3 minutes
            break
```

### 2. Agent Prompt Rules

```markdown
## Working Directory Rules
1. BEFORE running init-artifact.sh, verify target directory doesn't exist
2. AFTER init-artifact.sh completes, record the absolute path created
3. NEVER run init-artifact.sh if mcp-demo/ exists with package.json

## Long-Running Command Rules  
1. Commands containing 'init-artifact.sh' take 60-120 seconds
2. DO NOT send any other commands until completion
```

### 3. State Persistence

```python
class ExecutionState:
    initialized_projects: dict[str, str] = {}  # name -> path
    completed_bundles: set[str] = set()
    
    def mark_initialized(self, name: str, path: str):
        self.initialized_projects[name] = path
```

---

## Conclusion

Three cascading issues caused the agent's struggles:

1. **Working directory confusion** → Multiple duplicate projects
2. **No timeout handling** → Server crashes during long scripts  
3. **No state persistence** → Repeated work after every restart

**Priority Fix Order:**

1. Add longer timeouts for known long-running scripts
2. Implement state tracking for completed initializations
3. Add agent rules to prevent concurrent commands during `init-artifact.sh`
