import{j as e}from"./index-DYAXeqNr.js";import{F as i}from"./FlowDiagram-BqDL7bSF.js";function s(n){const t={a:"a",code:"code",em:"em",h1:"h1",h2:"h2",h3:"h3",hr:"hr",img:"img",li:"li",ol:"ol",p:"p",strong:"strong",...n.components};return e.jsxs(e.Fragment,{children:[e.jsx(t.hr,{}),`
`,e.jsx(t.h2,{children:`title: "Building AI Consciousness: Nanobot, GCP, and Telegram Automation"
date: "2026-02-21"
tags: ["nanobot", "architecture", "devops", "cloud-run"]`}),`
`,`
`,e.jsx(t.h1,{children:"Building AI Consciousness: Nanobot, GCP, and Telegram Automation"}),`
`,e.jsxs(t.p,{children:["Welcome to a deep dive into how I built the ",e.jsx(t.a,{href:"https://kentchiu-memo-662008816033.asia-southeast1.run.app/consciousness",children:"Consciousness"})," portal for OpenMemo. This architecture acts as the central nervous system for my digital second brain, combining a custom agent (",e.jsx(t.strong,{children:"Nanobot"}),"), Google Cloud Platform (",e.jsx(t.strong,{children:"GCP Cloud Run"}),"), and ",e.jsx(t.strong,{children:"Telegram"})," as the primary interface."]}),`
`,e.jsx(t.h2,{children:"System Architecture"}),`
`,e.jsx(t.p,{children:"At its core, Nanobot serves as the intelligent backend. It orchestrates skills, manages memory, and handles long-running DevOps tasks. By deploying to GCP Cloud Run, the system runs reliably in the cloud, accepting requests instantly."}),`
`,e.jsx(i,{height:"400px",initialNodes:[{id:"1",position:{x:50,y:150},data:{label:"Telegram App (User/Dev)"},type:"input"},{id:"2",position:{x:300,y:150},data:{label:"Nanobot (GCP Cloud Run)"}},{id:"3",position:{x:550,y:50},data:{label:"GitHub Repository"}},{id:"4",position:{x:550,y:250},data:{label:"OpenMemo Webapp (Public)"},type:"output"}],initialEdges:[{id:"e1-2",source:"1",target:"2",animated:!0,label:"Commands & Messages"},{id:"e2-3",source:"2",target:"3",animated:!0,label:"Git Push (DevOps Skills)"},{id:"e3-4",source:"3",target:"4",animated:!0,label:"Automated CI/CD"}]}),`
`,e.jsx(t.h3,{children:"1. Telegram as the Operating Channel"}),`
`,e.jsx(t.p,{children:"Instead of building a massive custom chat UI, I rely on Telegram. It’s mobile-first, robust, and provides an immediate tether to Nanobot no matter where I am. I can send commands directly to the bot, which parses them and triggers the appropriate execution loops."}),`
`,e.jsx(t.h3,{children:"2. Custom DevOps Skills"}),`
`,e.jsxs(t.p,{children:["One of the most powerful aspects of this architecture is how it automates the deployment of ",e.jsx(t.code,{children:"open_memo/webapp"}),". Nanobot has customized skills specifically designed to handle DevOps workflows."]}),`
`,e.jsx(t.p,{children:"When I ask it to create a new blog or update a page, Nanobot:"}),`
`,e.jsxs(t.ol,{children:[`
`,e.jsx(t.li,{children:"Generates the content or code adjustments."}),`
`,e.jsx(t.li,{children:"Integrates it directly into the repository."}),`
`,e.jsx(t.li,{children:"Automatically pushes the branch to GitHub."}),`
`,e.jsx(t.li,{children:"The deployment pipeline picks it up, updating the live webapp, making the new knowledge publicly accessible to interested users without requiring any custom manual API bridges."}),`
`]}),`
`,e.jsx(t.h2,{children:"Real-World Examples"}),`
`,e.jsx(t.p,{children:"Here are two snapshots of the agent interacting with the system:"}),`
`,e.jsx(t.p,{children:e.jsx(t.img,{src:"/20260221-nanobot-example1.png",alt:"Nanobot Example 1"})}),`
`,e.jsx(t.p,{children:e.jsx(t.em,{children:"Triggering deep DevOps and content creation flows natively through the Telegram interface."})}),`
`,e.jsx(t.p,{children:e.jsx(t.img,{src:"/20260221-nanobot-example2.png",alt:"Nanobot Example 2"})}),`
`,e.jsx(t.p,{children:e.jsx(t.em,{children:"The seamless resulting output rendered directly into the webapp's consciousness stream."})}),`
`,e.jsx(t.h2,{children:"Conclusion"}),`
`,e.jsx(t.p,{children:"By treating the agent itself as the development orchestrator living on GCP, and wrapping it via Telegram, the friction of maintaining a complex personal knowledge base drops to near zero. I can simply think, chat, and watch the system build itself out in the open."})]})}function r(n={}){const{wrapper:t}=n.components||{};return t?e.jsx(t,{...n,children:e.jsx(s,{...n})}):s(n)}export{r as default};
