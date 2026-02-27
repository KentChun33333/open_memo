import{j as e}from"./index-DL95azgn.js";const r={title:"Deep Analysis: Why the Web Artifacts Builder Agent Fails",date:"2026-01-21",tags:["debugging","failure-analysis","agent"]};function i(s){const n={code:"code",em:"em",h1:"h1",h2:"h2",h3:"h3",hr:"hr",li:"li",ol:"ol",p:"p",strong:"strong",ul:"ul",...s.components};return e.jsxs(e.Fragment,{children:[e.jsx(n.h1,{children:"Deep Analysis: Why the Web Artifacts Builder Agent Fails"}),`
`,e.jsxs(n.p,{children:["You observed that your ",e.jsx(n.code,{children:"mcp_skill_agent"})," successfully initializes the project (runs ",e.jsx(n.code,{children:"scripts/init-artifact.sh"}),') but fails to "Develop" it (customize the code), leaving you with just the template. In contrast, robust agents like ',e.jsx(n.code,{children:"antigravity"})," or ",e.jsx(n.code,{children:"claude-code"})," succeed."]}),`
`,e.jsx(n.p,{children:"Here is the root cause analysis and the solution."}),`
`,e.jsx(n.h2,{children:'1. The "Blind Programmer" Problem'}),`
`,e.jsx(n.p,{children:e.jsx(n.strong,{children:'The core failure condition is "Blindness".'})}),`
`,e.jsxs(n.ol,{children:[`
`,e.jsxs(n.li,{children:[`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Missing Exploration Tools"}),":"]}),`
`,e.jsxs(n.ul,{children:[`
`,e.jsxs(n.li,{children:["Your agent prompt ",e.jsx(n.em,{children:"claims"})," to have ",e.jsx(n.code,{children:"list_directory"}),", but the actual ",e.jsx(n.code,{children:"fs_server.py"})," implementation ",e.jsx(n.strong,{children:"DOES NOT"})," have this tool."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Result"}),": After running ",e.jsx(n.code,{children:"init-artifact.sh"}),", the agent is blindly guessing where the files are. It cannot run ",e.jsx(n.code,{children:"ls"})," or ",e.jsx(n.code,{children:"tree"})," to see the generated ",e.jsx(n.code,{children:"src/App.tsx"})," or ",e.jsx(n.code,{children:"src/components"}),". It doesn't know what files exist to edit."]}),`
`]}),`
`]}),`
`,e.jsxs(n.li,{children:[`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:'Missing "read-before-write" Loop'}),":"]}),`
`,e.jsxs(n.ul,{children:[`
`,e.jsxs(n.li,{children:["Effective agents (like Antigravity) follow a loop: ",e.jsx(n.code,{children:"Explore"})," -> ",e.jsx(n.code,{children:"Read"})," -> ",e.jsx(n.code,{children:"Think"})," -> ",e.jsx(n.code,{children:"Edit"}),"."]}),`
`,e.jsxs(n.li,{children:['Your subagent is told to "Develop your artifact", but without ',e.jsx(n.code,{children:"list_directory"}),`, it skips the "Explore" phase. It likely hallucinates path names or simply gives up because it can't "see" the code it just created.`]}),`
`]}),`
`]}),`
`]}),`
`,e.jsx(n.h2,{children:'2. The "Blunt Instrument" Problem'}),`
`,e.jsx(n.p,{children:e.jsx(n.strong,{children:'The second failure is "Lack of Precision".'})}),`
`,e.jsxs(n.ol,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"No Code Modification Tool"}),":",`
`,e.jsxs(n.ul,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.code,{children:"fs_server.py"})," only implements ",e.jsx(n.code,{children:"write_file"}),", which overwrites the ",e.jsx(n.em,{children:"entire"})," file."]}),`
`,e.jsxs(n.li,{children:["To change one line in ",e.jsx(n.code,{children:"App.tsx"}),", the LLM must perfectly hallucinate/reproduce the entire 50-line file with zero context. This is highly error-prone for smaller models (like Nemotron-3-nano)."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Required"}),": A ",e.jsx(n.code,{children:"replace_string"})," or ",e.jsx(n.code,{children:"apply_patch"}),' tool is essential. This allows the agent to say "Change ',e.jsx(n.code,{children:"<h1...>"})," to ",e.jsx(n.code,{children:"<h1>My Custom Title</h1>"}),'" without rewriting the whole file.']}),`
`]}),`
`]}),`
`]}),`
`,e.jsx(n.h2,{children:'3. The "State Amnesia" Problem'}),`
`,e.jsx(n.p,{children:e.jsx(n.strong,{children:'The third failure is "Context Isolation".'})}),`
`,e.jsxs(n.ol,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"No Feedback Loop"}),":",`
`,e.jsxs(n.ul,{children:[`
`,e.jsxs(n.li,{children:["When ",e.jsx(n.code,{children:"init-artifact.sh"}),` runs, it outputs a lot of logs. But the agent doesn't necessarily "ingest" the file structure from those logs into its "Mental Map" for the next step.`]}),`
`,e.jsxs(n.li,{children:["Advanced agents run ",e.jsx(n.code,{children:"ls -R"}),' immediately after avoiding "amnesia" about the file state.']}),`
`]}),`
`]}),`
`]}),`
`,e.jsx(n.hr,{}),`
`,e.jsx(n.h2,{children:'Proposed Solution: The "Developer Toolpack" Upgrade'}),`
`,e.jsxs(n.p,{children:["To fix this, we need to upgrade ",e.jsx(n.code,{children:"fs_server.py"}),' to give the agent "Vision" and "Surgical Hands".']}),`
`,e.jsxs(n.h3,{children:["Step 1: Upgrade ",e.jsx(n.code,{children:"fs_server.py"})]}),`
`,e.jsx(n.p,{children:"Add these three tools:"}),`
`,e.jsxs(n.ol,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.code,{children:"list_directory(path)"}),": (CRITICAL) Allows the agent to see the project structure."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.code,{children:"search_files(pattern)"}),': (Recommended) Simple grep to find text like "Edit this text".']}),`
`,e.jsxs(n.li,{children:[e.jsx(n.code,{children:"replace_in_file(path, search, replace)"}),': (CRITICAL) "Surgical" editing. Much easier for LLMs than full file overwrites.']}),`
`]}),`
`,e.jsx(n.h3,{children:"Step 2: Update Subagent Instruction"}),`
`,e.jsxs(n.p,{children:["Update ",e.jsx(n.code,{children:"SkillManager"})," to verify that the agent ",e.jsx(n.em,{children:"explores"})," before editing."]}),`
`,e.jsxs(n.ul,{children:[`
`,e.jsxs(n.li,{children:['Add to prompt: "After running a script that generates files, you MUST use ',e.jsx(n.code,{children:"list_directory"}),' to verify the structure before editing."']}),`
`]}),`
`,e.jsx(n.h3,{children:"Step 3: (Advanced) RAG / LSP"}),`
`,e.jsxs(n.ul,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"RAG"}),": You asked about RAG. While helpful, it's ",e.jsx(n.em,{children:"secondary"}),". The agent doesn't need to know every shadcn API perfectly to make ",e.jsx(n.em,{children:"some"})," edit. It first needs to simply ",e.jsx(n.em,{children:"see"})," the file to edit it."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"LSP"}),": Adding a Language Server is complex. Start with basic ",e.jsx(n.code,{children:"list"})," + ",e.jsx(n.code,{children:"read"})," + ",e.jsx(n.code,{children:"replace"}),". That is sufficient for 90% of tasks."]}),`
`]}),`
`,e.jsx(n.h2,{children:"Next Steps"}),`
`,e.jsxs(n.p,{children:["I recommend we implement the ",e.jsx(n.strong,{children:"Developer Toolpack"})," (Step 1) immediately."]})]})}function l(s={}){const{wrapper:n}=s.components||{};return n?e.jsx(n,{...s,children:e.jsx(i,{...s})}):i(s)}export{l as default,r as frontmatter};
