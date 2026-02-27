import{j as e}from"./index-DL95azgn.js";const o={title:"Nanobot Architecture Analysis: Memory System & Mindmap",date:"2026-02-19",tags:["nanobot","architecture","memory","agent"]};function r(s){const n={blockquote:"blockquote",code:"code",h1:"h1",h2:"h2",h3:"h3",hr:"hr",li:"li",ol:"ol",p:"p",pre:"pre",strong:"strong",table:"table",tbody:"tbody",td:"td",th:"th",thead:"thead",tr:"tr",...s.components};return e.jsxs(e.Fragment,{children:[e.jsx(n.h1,{children:"Nanobot Architecture Analysis"}),`
`,e.jsxs(n.blockquote,{children:[`
`,e.jsxs(n.p,{children:["Ultra-lightweight personal AI assistant (~3,700 LOC) inspired by OpenClaw — ",e.jsx(n.strong,{children:"99% smaller"})," than Clawdbot's 430k+ lines."]}),`
`]}),`
`,e.jsx(n.h2,{children:"Architecture Mindmap"}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-mermaid",children:`mindmap
  root((🐈 nanobot))
    📡 Channels
      Telegram
      Discord
      WhatsApp
      Feishu
      Slack
      DingTalk
      Email
      QQ
      Mochat
    🔀 Message Bus
      InboundMessage
      OutboundMessage
      Event-driven routing
    🧠 Agent Core
      AgentLoop
        LLM call loop
        Tool execution
        Max iterations guard
      ContextBuilder
        System prompt assembly
        Bootstrap files
        Memory injection
        Skills injection
      SubagentManager
        Background tasks
        Parallel execution
    💾 Memory System
      MEMORY.md
        Long-term facts
        User preferences
        Project context
        Always in prompt
      HISTORY.md
        Append-only log
        Grep-searchable
        Event summaries
      Sessions
        JSONL per chat
        Append-only messages
        Tool call metadata
      Auto-Consolidation
        LLM-powered
        Fact extraction
        History summarization
        Sliding window
    🔧 Tools
      File Tools
        read / write / edit
        list / search
      Exec Tool
        Shell commands
        Timeout control
      Web Tools
        Search
        Fetch pages
      Message Tool
        Send to channel
      Spawn Tool
        Subagents
      Cron Tool
        Scheduled tasks
      MCP Servers
        External integrations
    📦 Skills
      Always-on
        memory skill
      On-demand
        summarize
        weather
        voice-transcribe
        web-artifacts-builder
        clawhub
        github
      Progressive loading
    🤖 Providers
      Anthropic
      OpenAI
      DeepSeek
      Groq
      Gemini
      vLLM / Ollama
      OpenRouter
      Moonshot
      MiniMax
      SiliconFlow
      AiHubMix
      GitHub Copilot
      OpenAI Codex
    ⚙️ Config
      ~/.nanobot/config.json
      Pydantic schema
      camelCase aliases
      Environment overrides
`})}),`
`,e.jsx(n.h2,{children:"Component Overview"}),`
`,e.jsxs(n.table,{children:[e.jsx(n.thead,{children:e.jsxs(n.tr,{children:[e.jsx(n.th,{children:"Component"}),e.jsx(n.th,{style:{textAlign:"center"},children:"Lines"}),e.jsx(n.th,{children:"Purpose"})]})}),e.jsxs(n.tbody,{children:[e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.code,{children:"agent/loop.py"})}),e.jsx(n.td,{style:{textAlign:"center"},children:"477"}),e.jsx(n.td,{children:"Core agent loop — LLM calls, tool execution, consolidation"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.code,{children:"agent/context.py"})}),e.jsx(n.td,{style:{textAlign:"center"},children:"243"}),e.jsx(n.td,{children:"Prompt assembly — bootstrap files, memory, skills"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.code,{children:"session/manager.py"})}),e.jsx(n.td,{style:{textAlign:"center"},children:"199"}),e.jsx(n.td,{children:"JSONL session persistence per channel:chat_id"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.code,{children:"agent/memory.py"})}),e.jsx(n.td,{style:{textAlign:"center"},children:"31"}),e.jsx(n.td,{children:"Two-layer memory store (MEMORY.md + HISTORY.md)"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.code,{children:"agent/skills.py"})}),e.jsx(n.td,{style:{textAlign:"center"},children:"~200"}),e.jsx(n.td,{children:"Progressive skill loading (always-on vs on-demand)"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.code,{children:"channels/manager.py"})}),e.jsx(n.td,{style:{textAlign:"center"},children:"228"}),e.jsx(n.td,{children:"Channel init & routing (9 platforms)"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.code,{children:"bus/events.py"})}),e.jsx(n.td,{style:{textAlign:"center"},children:"38"}),e.jsx(n.td,{children:"InboundMessage / OutboundMessage dataclasses"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.code,{children:"config/schema.py"})}),e.jsx(n.td,{style:{textAlign:"center"},children:"340"}),e.jsx(n.td,{children:"Pydantic config schema with 14 LLM providers"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"Total"})}),e.jsx(n.td,{style:{textAlign:"center"},children:e.jsx(n.strong,{children:"~3,700"})}),e.jsx(n.td,{children:e.jsx(n.strong,{children:"99% smaller than Clawdbot"})})]})]})]}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Memory System Deep Dive"}),`
`,e.jsxs(n.p,{children:["Nanobot's memory is a ",e.jsx(n.strong,{children:"three-layer file-based system"})," with LLM-powered auto-consolidation. Total memory code: ~115 lines."]}),`
`,e.jsx(n.h3,{children:"Architecture Flow"}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-mermaid",children:`flowchart LR
    subgraph Input
        U["User Message"]
    end

    subgraph Session["Session Layer"]
        S["sessions/*.jsonl"]
    end

    subgraph Prompt["Prompt Assembly"]
        CB["ContextBuilder"]
    end

    subgraph Memory["Memory Layer"]
        M["MEMORY.md<br/>long-term facts"]
        H["HISTORY.md<br/>event log"]
    end

    subgraph LLM["LLM"]
        L["Provider"]
    end

    subgraph Consolidation["Auto-Consolidation"]
        C["LLM extracts facts<br/>+ summarizes history"]
    end

    U --> S
    S -->|"history"| CB
    M -->|"always injected"| CB
    CB --> L
    L -->|"response"| S

    S -->|"when session grows"| C
    C -->|"facts"| M
    C -->|"summary"| H
`})}),`
`,e.jsxs(n.h3,{children:["Layer 1 — Long-Term Memory (",e.jsx(n.code,{children:"MEMORY.md"}),")"]}),`
`,e.jsxs(n.p,{children:["Key facts, user preferences, project context. ",e.jsx(n.strong,{children:"Always injected into every system prompt."})]}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-python",children:`# agent/memory.py — only 31 lines!
class MemoryStore:
    def __init__(self, workspace: Path):
        self.memory_dir = ensure_dir(workspace / "memory")
        self.memory_file = self.memory_dir / "MEMORY.md"
        self.history_file = self.memory_dir / "HISTORY.md"

    def read_long_term(self) -> str:
        if self.memory_file.exists():
            return self.memory_file.read_text(encoding="utf-8")
        return ""

    def write_long_term(self, content: str) -> None:
        self.memory_file.write_text(content, encoding="utf-8")

    def append_history(self, entry: str) -> None:
        with open(self.history_file, "a", encoding="utf-8") as f:
            f.write(entry.rstrip() + "\\n\\n")

    def get_memory_context(self) -> str:
        long_term = self.read_long_term()
        return f"## Long-term Memory\\n{long_term}" if long_term else ""
`})}),`
`,e.jsxs(n.h3,{children:["Layer 2 — History Log (",e.jsx(n.code,{children:"HISTORY.md"}),")"]}),`
`,e.jsxs(n.p,{children:["Append-only event log. ",e.jsx(n.strong,{children:"NOT loaded into context"})," — retrieved on-demand via ",e.jsx(n.code,{children:"grep"}),"."]}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-markdown",children:`<!-- Example auto-generated entry -->
[2026-02-19 17:00] User configured Telegram channel for nanobot.
Migrated bot token from Clawdbot config. Gateway started successfully.
User's Telegram Chat ID is 6291416524.
`})}),`
`,e.jsxs(n.h3,{children:["Layer 3 — Session Persistence (",e.jsx(n.code,{children:"sessions/*.jsonl"}),")"]}),`
`,e.jsxs(n.p,{children:["Raw message history per ",e.jsx(n.code,{children:"channel:chat_id"}),", stored as JSONL for streaming reads."]}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-python",children:`@dataclass
class Session:
    key: str                          # "telegram:6291416524"
    messages: list[dict[str, Any]]    # Full message history
    last_consolidated: int = 0        # Watermark for consolidation

    def get_history(self, max_messages=500) -> list[dict]:
        return self.messages[-max_messages:]
`})}),`
`,e.jsx(n.h3,{children:'Auto-Consolidation — The "Brain Compactor"'}),`
`,e.jsxs(n.p,{children:["The most elegant part: uses the ",e.jsx(n.strong,{children:"LLM itself"})," to extract facts and summarize old messages when the session grows large."]}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-python",children:`# agent/loop.py — _consolidate_memory()
async def _consolidate_memory(self, session, archive_all=False):
    memory = MemoryStore(self.workspace)
    keep_count = self.memory_window // 2
    old_messages = session.messages[session.last_consolidated:-keep_count]

    # Format conversation and ask LLM to process it
    prompt = """Process this conversation and return JSON:
    1. "history_entry": 2-5 sentence summary with timestamp
    2. "memory_update": Updated long-term memory with new facts"""

    response = await self.provider.chat(messages=[...])
    result = json_repair.loads(response.content)

    # Write to files
    memory.append_history(result["history_entry"])    # → HISTORY.md
    memory.write_long_term(result["memory_update"])   # → MEMORY.md
    session.last_consolidated = len(session.messages) - keep_count
`})}),`
`,e.jsx(n.h3,{children:"How Memory Gets Injected Into Prompts"}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-python",children:`# agent/context.py — build_system_prompt()
def build_system_prompt(self) -> str:
    parts = []
    parts.append(self._get_identity())       # Core identity + workspace info
    parts.append(self._load_bootstrap_files()) # AGENTS.md, SOUL.md, USER.md...
    memory = self.memory.get_memory_context()
    if memory:
        parts.append(f"# Memory\\n\\n{memory}")  # ← MEMORY.md injected here
    parts.append(skills_summary)              # Available skills
    return "\\n\\n---\\n\\n".join(parts)
`})}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Design Principles"}),`
`,e.jsxs(n.ol,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"File-based memory"})," — No database. Plain markdown files readable by both humans and the agent"]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"LLM-powered consolidation"})," — The agent's own LLM extracts facts and summarizes history automatically"]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Progressive skill loading"})," — Only ",e.jsx(n.code,{children:"always: true"})," skills injected; others loaded on-demand via ",e.jsx(n.code,{children:"read_file"})]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Append-only sessions"})," — Messages never modified for LLM cache efficiency"]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Event-driven bus"})," — Decoupled channels from agent via ",e.jsx(n.code,{children:"MessageBus"})]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Minimal code"})," — ~3,700 lines total delivers full agent + 9 chat platforms + 14 LLM providers"]}),`
`]}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Comparison with mcp_skill_agent"}),`
`,e.jsxs(n.table,{children:[e.jsx(n.thead,{children:e.jsxs(n.tr,{children:[e.jsx(n.th,{children:"Feature"}),e.jsx(n.th,{children:"Nanobot"}),e.jsx(n.th,{children:"mcp_skill_agent"})]})}),e.jsxs(n.tbody,{children:[e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"LOC"})}),e.jsx(n.td,{children:"~3,700"}),e.jsx(n.td,{children:"~2,500"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"Memory"})}),e.jsx(n.td,{children:"3-layer (files + LLM consolidation)"}),e.jsx(n.td,{children:"SessionMemoryManager (JSON state)"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"Channels"})}),e.jsx(n.td,{children:"9 platforms"}),e.jsx(n.td,{children:"CLI only"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"Skills"})}),e.jsx(n.td,{children:"Progressive (always-on + on-demand)"}),e.jsx(n.td,{children:"MCP server based"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"Token Management"})}),e.jsx(n.td,{children:"Auto-consolidation with sliding window"}),e.jsx(n.td,{children:"None (append indefinitely)"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"Error Recovery"})}),e.jsx(n.td,{children:"Basic retry in loop"}),e.jsx(n.td,{children:"SOP-guided retry"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"Session Persistence"})}),e.jsx(n.td,{children:"JSONL files"}),e.jsx(n.td,{children:"JSON state file"})]})]})]})]})}function i(s={}){const{wrapper:n}=s.components||{};return n?e.jsx(n,{...s,children:e.jsx(r,{...s})}):r(s)}export{i as default,o as frontmatter};
