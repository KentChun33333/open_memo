import{j as e}from"./index-DL95azgn.js";const r={title:"Master Guide: Terminating Persistent AI Agents on macOS",date:"2026-02-22",tags:["macos","agents","troubleshooting","process-management","open_memo"],summary:"When building agentic frameworks like OpenClaw or open_memo, processes often become immortal by registering with the macOS kernel. Learn how to perform a clean kill and deep exorcism."};function t(s){const n={code:"code",em:"em",h2:"h2",li:"li",p:"p",pre:"pre",strong:"strong",table:"table",tbody:"tbody",td:"td",th:"th",thead:"thead",tr:"tr",ul:"ul",...s.components};return e.jsxs(e.Fragment,{children:[e.jsx(n.p,{children:'When building agentic frameworks like OpenClaw or open_memo, processes often become "immortal" because they register themselves with the macOS kernel. Deleting the folder is not enough; you must de-register the service.'}),`
`,e.jsx(n.h2,{children:'Phase 1: The "Clean Kill" (Memory & Network)'}),`
`,e.jsx(n.p,{children:"First, identify exactly what is holding the port and kill the process in RAM."}),`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Identify by Port:"}),`
Find the Process ID (PID) specifically using the port 18789:`]}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-bash",children:`lsof -i :18789
`})}),`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Trace the Parent:"}),`
If it keeps coming back, find out who is "spawning" it. If the PPID is 1, macOS is the one restarting it:`]}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-bash",children:`ps -o ppid= -p $(lsof -ti:18789) | xargs ps -p
`})}),`
`,e.jsx(n.p,{children:e.jsx(n.strong,{children:"The Force Kill:"})}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-bash",children:`kill -9 [PID]
`})}),`
`,e.jsx(n.h2,{children:'Phase 2: The "Exorcism" (System Registration)'}),`
`,e.jsx(n.p,{children:"If the process respawns, macOS has a LaunchAgent cached in memory. You must unload the instructions."}),`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Locate the Files:"}),`
Check these three critical paths for `,e.jsx(n.code,{children:".plist"})," files (e.g., ",e.jsx(n.code,{children:"com.clawdbot.gateway.plist"}),"):"]}),`
`,e.jsxs(n.ul,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.code,{children:"~/Library/LaunchAgents/"})," (User level)"]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.code,{children:"/Library/LaunchAgents/"})," (System level)"]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.code,{children:"/Library/LaunchDaemons/"})," (Root level)"]}),`
`]}),`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Unregister the Job:"}),`
Even if you delete the file, the job stays in the launchd database. Find the label and remove it:`]}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-bash",children:`launchctl list | grep -i "claw"
launchctl remove [label_name]
`})}),`
`,e.jsx(n.p,{children:e.jsx(n.strong,{children:"Permanent Deletion:"})}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-bash",children:`rm -rf ~/Library/LaunchAgents/com.clawdbot.gateway.plist
`})}),`
`,e.jsx(n.h2,{children:'Phase 3: The "Deep Clean" (Global Binaries)'}),`
`,e.jsx(n.p,{children:"Since you are a lead dev, you likely have global packages that might still be active."}),`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Node.js:"})," Check for globally installed bots:"]}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-bash",children:`npm list -g --depth=0
`})}),`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"PM2:"})," If you use a process manager, it will restart the bot forever until killed:"]}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-bash",children:`pm2 delete all
`})}),`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Docker:"})," Ensure no containers are mapped to your dev ports:"]}),`
`,e.jsx(n.pre,{children:e.jsx(n.code,{className:"language-bash",children:`docker ps
`})}),`
`,e.jsx(n.h2,{children:'Summary Checklist for Future "Zombies"'}),`
`,e.jsxs(n.table,{children:[e.jsx(n.thead,{children:e.jsxs(n.tr,{children:[e.jsx(n.th,{style:{textAlign:"left"},children:"Symptom"}),e.jsx(n.th,{style:{textAlign:"left"},children:"Cause"}),e.jsx(n.th,{style:{textAlign:"left"},children:"Solution"})]})}),e.jsxs(n.tbody,{children:[e.jsxs(n.tr,{children:[e.jsx(n.td,{style:{textAlign:"left"},children:"Port 18789 is busy"}),e.jsx(n.td,{style:{textAlign:"left"},children:"Process is running in RAM"}),e.jsx(n.td,{style:{textAlign:"left"},children:e.jsx(n.code,{children:"kill -9 [PID]"})})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{style:{textAlign:"left"},children:"Process returns after kill"}),e.jsx(n.td,{style:{textAlign:"left"},children:'launchd "KeepAlive" is active'}),e.jsx(n.td,{style:{textAlign:"left"},children:e.jsx(n.code,{children:"launchctl remove [label]"})})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{style:{textAlign:"left"},children:"Code is deleted but it runs"}),e.jsx(n.td,{style:{textAlign:"left"},children:"Binary is in global /bin or RAM"}),e.jsxs(n.td,{style:{textAlign:"left"},children:[e.jsx(n.code,{children:"which [app]"})," and ",e.jsx(n.code,{children:"killall node"})]})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{style:{textAlign:"left"},children:"Browser still shows chat"}),e.jsx(n.td,{style:{textAlign:"left"},children:"Service Worker/Cache"}),e.jsx(n.td,{style:{textAlign:"left"},children:"Cmd+Shift+R or clear Service Workers"})]})]})]}),`
`,e.jsx(n.h2,{children:"Pro-Tip for open_memo"}),`
`,e.jsxs(n.p,{children:["To avoid this in the future, I recommend running your local agents inside a Docker container or using a Python Virtual Environment with a specific ",e.jsx(n.code,{children:"stop.sh"})," script. This keeps the system-level LaunchAgents folder clean."]}),`
`,e.jsx(n.p,{children:e.jsxs(n.em,{children:["Would you like me to draft a ",e.jsx(n.code,{children:"cleanup.sh"})," script for your repository that automates these steps for your team?"]})})]})}function i(s={}){const{wrapper:n}=s.components||{};return n?e.jsx(n,{...s,children:e.jsx(t,{...s})}):t(s)}export{i as default,r as frontmatter};
