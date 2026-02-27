import{j as e}from"./index-DL95azgn.js";const i={title:"Gap Analysis: StepExecutor & Orchestrator",date:"2026-01-25",tags:["architecture","agent","analysis"],summary:"An analysis report on agent architecture."};function t(s){const n={code:"code",em:"em",h1:"h1",h2:"h2",h3:"h3",hr:"hr",li:"li",ol:"ol",p:"p",pre:"pre",strong:"strong",ul:"ul",...s.components};return e.jsxs(e.Fragment,{children:[e.jsx(n.h1,{children:"Gap Analysis: StepExecutor & Orchestrator vs. Production Standards"}),`
`,e.jsx(n.h2,{children:"Executive Summary"}),`
`,e.jsxs(n.p,{children:["The current implementation of ",e.jsx(n.code,{children:"StepExecutor"})," and ",e.jsx(n.code,{children:"Orchestrator"})," relies heavily on ",e.jsx(n.strong,{children:"Prompt Engineering"})," and ",e.jsx(n.strong,{children:"Reactive Interventions"}),' (e.g., regex-based auto-write checks). A "Production Grade" system relies on ',e.jsx(n.strong,{children:"Structured Engineering"}),", ",e.jsx(n.strong,{children:"Deterministic Constraints"}),", and ",e.jsx(n.strong,{children:"Stateful Context Management"}),"."]}),`
`,e.jsx(n.p,{children:'The primary failure mode ("not generating code" or "ignoring skill instructions") stems from three root causes:'}),`
`,e.jsxs(n.ol,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Loose Control Loop"}),': The ReAct loop pushes the model to "continue" without validating if the previous action was effective.']}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Context Dilution"}),": The rich instructions in ",e.jsx(n.code,{children:"SKILL.md"})," are potentially lost or fragmented when broken down into individual steps."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Lack of Structured Enforcement"}),": The agent is permitted to output free-form text when it ",e.jsx(n.em,{children:"should"})," be forced to use tools."]}),`
`]}),`
`,e.jsx(n.hr,{}),`
`,e.jsxs(n.h2,{children:["1. StepExecutor Analysis (",e.jsx(n.code,{children:"step_executor.py"}),")"]}),`
`,e.jsx(n.h3,{children:'Gap 1: The "Chatty" Agent Problem (Tool Usage)'}),`
`,e.jsxs(n.ul,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Current Implementation"}),": The ",e.jsx(n.code,{children:"StepExecutor"})," initializes an agent with prompts that ",e.jsx(n.em,{children:"ask"})," it to use tools (",e.jsx(n.code,{children:"SUBAGENT_INSTRUCTION"}),"). It relies on the LLM's training to prefer tool calls over text."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Production Standard"}),": Use ",e.jsx(n.strong,{children:"Tool Choice Enforcing"})," (e.g., ",e.jsx(n.code,{children:'tool_choice: "required"'})," in OpenAI API) or ",e.jsx(n.strong,{children:"Structured Outputs"})," (JSON Schema)."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Impact"}),': The model often "hallucinates" action by writing Markdown code blocks (',e.jsx(n.code,{children:"```python ... ```"}),") instead of invoking ",e.jsx(n.code,{children:"write_file"}),'. The current "Auto-Write Intervention" (lines 137-140) is a brittle regex patch that fails if the model uses slightly different formatting.']}),`
`]}),`
`,e.jsx(n.h3,{children:'Gap 2: The "Blind" ReAct Loop'}),`
`,e.jsxs(n.ul,{children:[`
`,e.jsxs(n.li,{children:[`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Current Implementation"}),":"]}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-python",children:`current_prompt = user_prompt if cycle == 1 else "Status Update: Continue execution..."
`})}),`
`,e.jsxs(n.p,{children:["This loop is agnostic to the ",e.jsx(n.em,{children:"result"})," of the previous cycle. It assumes the model knows what to do next."]}),`
`]}),`
`,e.jsxs(n.li,{children:[`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Production Standard"}),": The Controller should inspect the ",e.jsx(n.strong,{children:"Tool Output History"}),"."]}),`
`,e.jsxs(n.ul,{children:[`
`,e.jsxs(n.li,{children:["If ",e.jsx(n.code,{children:"write_file"}),' returned "Success", the prompt should be: "File written. Now verify X."']}),`
`,e.jsxs(n.li,{children:["If ",e.jsx(n.code,{children:"write_file"}),' returned "Error", the prompt should be: "Write failed due to X. Fix and retry."']}),`
`]}),`
`]}),`
`,e.jsxs(n.li,{children:[`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Impact"}),': The agent can get stuck in loops or exit prematurely because the "Continue" prompt is too vague.']}),`
`]}),`
`]}),`
`,e.jsx(n.h3,{children:"Gap 3: Missing Context Injection"}),`
`,e.jsxs(n.ul,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Current Implementation"}),":",`
`,e.jsxs(n.ul,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.code,{children:"SUBAGENT_INSTRUCTION"})," gets ",e.jsx(n.code,{children:"{task_input}"}),", ",e.jsx(n.code,{children:"{roadmap}"}),", ",e.jsx(n.code,{children:"{session_context}"}),"."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"MISSING"}),": The ",e.jsx(n.em,{children:"Global Skill Instructions"})," from ",e.jsx(n.code,{children:"SKILL.md"}),"."]}),`
`,e.jsxs(n.li,{children:["While ",e.jsx(n.code,{children:"orchestrator.py"})," parses the skill into steps, the ",e.jsx(n.em,{children:"nuanced guidelines"}),` (e.g., "Use Tailwind", "Don't use external images") often live in the preamble of the `,e.jsx(n.code,{children:"SKILL.md"}),", not inside the specific step description."]}),`
`]}),`
`]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Production Standard"}),": ",e.jsx(n.strong,{children:"Hierarchical Context Injection"}),". The Step Worker must receive:",`
`,e.jsxs(n.ol,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Global Constraints"})," (from Skill Preamble)."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Step Objectives"})," (from SOP)."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Dynamic State"})," (File contents)."]}),`
`]}),`
`]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Impact"}),': The agent builds the "What" (Step Goal) but ignores the "How" (Skill Guidelines).']}),`
`]}),`
`,e.jsx(n.hr,{}),`
`,e.jsxs(n.h2,{children:["2. Orchestrator Analysis (",e.jsx(n.code,{children:"orchestrator.py"}),")"]}),`
`,e.jsx(n.h3,{children:"Gap 4: SOP Parsing vs. Execution"}),`
`,e.jsxs(n.ul,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Current Implementation"}),":",`
`,e.jsxs(n.ul,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.code,{children:"_initialize_sop"})," loads content."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.code,{children:"SOPAgent"})," presumably parses this into ",e.jsx(n.code,{children:"SkillStep"})," objects."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Risk"}),': If the parser is naive (regex splits by headers), it might drop the "contextual glue" between steps.']}),`
`]}),`
`]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Production Standard"}),": The SOP Runtime should maintain a ",e.jsx(n.strong,{children:"Shared State"}),' that persists across steps. If Step 1 says "Use this variable," Step 2 must know that variable. currently, ',e.jsx(n.code,{children:"SessionMemory"})," tracks files, but not ",e.jsx(n.em,{children:"architectural decisions"}),"."]}),`
`]}),`
`,e.jsx(n.h3,{children:'Gap 5: The "One-Shot" Planner'}),`
`,e.jsxs(n.ul,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Current Implementation"}),": The Planner runs once at the beginning."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Production Standard"}),": ",e.jsx(n.strong,{children:"Dynamic Replanning"}),'. If Step 2 fails (e.g., "npm install failed"), the system should pause and ask the Planner to adjust the remaining steps, rather than forcing the Worker to retry the same doomed action.']}),`
`]}),`
`,e.jsx(n.hr,{}),`
`,e.jsxs(n.h2,{children:["3. Structs & Data Flow (",e.jsx(n.code,{children:"structs.py"}),")"]}),`
`,e.jsx(n.h3,{children:"Gap 6: Structured Inputs vs. Outputs"}),`
`,e.jsxs(n.ul,{children:[`
`,e.jsxs(n.li,{children:[`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Current Implementation"}),": ",e.jsx(n.code,{children:"CriticHandover"})," ensures structured ",e.jsx(n.em,{children:"Output"})," to the Critic."]}),`
`]}),`
`,e.jsxs(n.li,{children:[`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Missing"}),": Structured ",e.jsx(n.em,{children:"Input"})," to the Worker."]}),`
`]}),`
`,e.jsxs(n.li,{children:[`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Production Standard"}),": The ",e.jsx(n.code,{children:"StepExecutor"})," should not just feed a string ",e.jsx(n.code,{children:"task_input"}),". It should feed a ",e.jsx(n.code,{children:"StepContext"})," object ensuring consistency:"]}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-python",children:`@dataclass
class WorkerInput:
    global_constraints: str  # From Skill.md
    step_goal: str           # From SOP
    required_tools: List[str]
    file_context_paths: List[str] # Files to pre-read
`})}),`
`]}),`
`]}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:"Recommendations for Remediation"}),`
`,e.jsxs(n.ol,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Enforce Tools"}),": in ",e.jsx(n.code,{children:"StepExecutor"}),", modify the agent configuration to ",e.jsx(n.strong,{children:"REQUIRE"}),' tool calls when "coding" type steps are active.']}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Inject Global Context"}),": Update ",e.jsx(n.code,{children:"orchestrator.py"})," to pass the full ",e.jsx(n.code,{children:"SKILL.md"})," preamble to ",e.jsx(n.code,{children:"StepExecutor"}),", which then appends it to ",e.jsx(n.code,{children:"SUBAGENT_INSTRUCTION"}),"."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Smart Loop"}),": Update ",e.jsx(n.code,{children:"StepExecutor"}),"'s loop to parse the previous tool result. If ",e.jsx(n.code,{children:"write_file"})," wasn't called in a coding step, ",e.jsx(n.strong,{children:"reject the turn"})," and prompt specifically for it."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Replace Regex Intervention"}),": Instead of ",e.jsx(n.code,{children:'if "```" in response'}),", use a deterministic check: ",e.jsx(n.code,{children:"if step.type == 'coding' and not tool_calls: raise ActionRequiredError"}),"."]}),`
`]})]})}function o(s={}){const{wrapper:n}=s.components||{};return n?e.jsx(n,{...s,children:e.jsx(t,{...s})}):t(s)}export{o as default,i as frontmatter};
