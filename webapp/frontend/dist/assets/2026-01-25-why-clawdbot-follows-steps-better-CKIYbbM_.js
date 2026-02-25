import{j as e}from"./index-B2GV5NfK.js";const l={title:"Why Clawdbot Follows Steps Better",date:"2026-01-25",tags:["architecture","agent","analysis"],summary:"An analysis report on agent architecture."};function t(s){const n={code:"code",em:"em",h1:"h1",h2:"h2",h3:"h3",li:"li",ol:"ol",p:"p",strong:"strong",ul:"ul",...s.components};return e.jsxs(e.Fragment,{children:[e.jsx(n.h1,{children:"Deep Research: Why Clawdbot Follows Steps Better than mcp_skill_agent"}),`
`,e.jsx(n.h2,{children:"Executive Summary"}),`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Clawdbot"})," enables superior adherence to step-by-step instructions through a ",e.jsx(n.strong,{children:'"Pull" architecture'})," (Agent actively retrieves skills as tools) and a ",e.jsx(n.strong,{children:"State-Aware Prompting System"})," that includes runtime context (time, capability, identity)."]}),`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"mcp_skill_agent"})," uses a ",e.jsx(n.strong,{children:'"Push" architecture'}),' (Planner forces skill text into System Prompt). While simpler, this overwhelms the context window upfront and lacks the "cognitive round-trip" that occurs when an agent must actively read and interpret a skill file.']}),`
`,e.jsx(n.h2,{children:"1. Architectural Difference: Pull vs. Push"}),`
`,e.jsx(n.h3,{children:'Clawdbot (The "Pull" Model)'}),`
`,e.jsxs(n.ul,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Discovery"}),": The system prompt lists ",e.jsx(n.em,{children:"descriptions"})," of skills but NOT their full content."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Action"}),": The agent must decidingly call a tool (e.g., ",e.jsx(n.code,{children:'read_skill("web-artifacts-builder")'}),") to get instructions."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Result"}),":",`
`,e.jsxs(n.ol,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Cognitive Break"}),": The agent pauses to read. The act of calling the tool reinforces intent."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Fresh Context"}),": The instructions arrive as a ",e.jsx(n.em,{children:"Tool Output"})," (Observation), which LLMs often prioritize over static System Prompts."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Step-by-Step State"}),': The agent is naturally in a "reading -> planning -> executing" loop.']}),`
`]}),`
`]}),`
`]}),`
`,e.jsx(n.h3,{children:'mcp_skill_agent (The "Push" Model)'}),`
`,e.jsxs(n.ul,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Discovery"}),": The Planner decides the skill."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Action"}),": The ",e.jsx(n.code,{children:"main.py"})," script retrieves the ",e.jsx(n.em,{children:"entire"})," skill content (HTML, Scripts, references) and injects it into the Subagent's System Prompt ",e.jsx(n.em,{children:"before"})," the first turn."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Result"}),":",`
`,e.jsxs(n.ol,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Context Overload"}),": The agent starts with a massive block of text (the skill)."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Lost Focus"}),': Without the active step of "reading" the skill, the agent treats it as background noise rather than active instructions.']}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"hallucination"}),": It often assumes it knows what to do without verifying the specific steps 1, 2, 3."]}),`
`]}),`
`]}),`
`]}),`
`,e.jsx(n.h2,{children:"2. Prompt Engineering & Context"}),`
`,e.jsxs(n.h3,{children:["Clawdbot's System Prompt (",e.jsx(n.code,{children:"system-prompt.ts"}),")"]}),`
`,e.jsxs(n.ul,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Dynamic Construction"}),": Builds prompt based on ",e.jsx(n.em,{children:"Runtime State"})," (Time, OS, Capabilities)."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Explicit Constraints"}),": ",e.jsx(n.em,{children:'"Constraints: never read more than one skill up front; only read after selecting."'})]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Tool-Native"}),": Defines tools clearly with ",e.jsx(n.code,{children:"coreToolSummaries"}),' and enforces specific usage patterns (e.g., "Narrate only when it helps").']}),`
`]}),`
`,e.jsxs(n.h3,{children:["mcp_skill_agent's Prompt (",e.jsx(n.code,{children:"main.py"}),")"]}),`
`,e.jsxs(n.ul,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Static Injection"}),": Appends ",e.jsx(n.code,{children:"skill_manager.get_skill_instruction(name)"})," + some fixed rules."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Loop Weakness"}),": Relies on ",e.jsx(n.code,{children:"mcp_agent.run_loop"})," (implied ",e.jsx(n.code,{children:"generate_str"})," loop). If the underlying library doesn't strictly enforce Thought/Action pairs, the model rushes to the final answer."]}),`
`]}),`
`,e.jsx(n.h2,{children:"3. Tooling Gaps (Addressed in recent update)"}),`
`,e.jsxs(n.ul,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Before"}),": ",e.jsx(n.code,{children:"mcp_skill_agent"})," lacked stateful bash (no ",e.jsx(n.code,{children:"cd"}),") and surgical editing."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Now"}),": We added ",e.jsx(n.code,{children:"bash_tools"})," (Editor, Persistent Shell)."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Remaining Gap"}),": The ",e.jsx(n.em,{children:"Agent Logic"}),` doesn't fully utilize them yet. It needs to "feel" the state.`]}),`
`]}),`
`,e.jsx(n.h2,{children:"Recommendation"}),`
`,e.jsxs(n.p,{children:["To make ",e.jsx(n.code,{children:"mcp_skill_agent"})," match Clawdbot's reliability, we should ",e.jsx(n.strong,{children:"mimic the Pull Model"}),":"]}),`
`,e.jsxs(n.ol,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Don't inject the full skill."})," Give the Subagent the ",e.jsx(n.code,{children:"Skill Name"})," and a tool ",e.jsx(n.code,{children:"read_skill_instruction()"}),"."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:'Force the "Read" Step.'})," In the initial user prompt, say: ",e.jsxs(n.em,{children:['"Task: X. First, use ',e.jsx(n.code,{children:"read_skill_instruction"}),' to get the steps."']})]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Enforce Verification."})," Use a loop that explicitly checks: ",e.jsx(n.em,{children:'"Have I completed Step X?"'})," before moving on."]}),`
`]})]})}function r(s={}){const{wrapper:n}=s.components||{};return n?e.jsx(n,{...s,children:e.jsx(t,{...s})}):t(s)}export{r as default,l as frontmatter};
