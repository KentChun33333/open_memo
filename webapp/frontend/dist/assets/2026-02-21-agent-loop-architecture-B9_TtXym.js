import{j as e}from"./index-B2GV5NfK.js";const i={title:"Understanding Nanobot's AgentLoop: Architecture, MCP, and Skills",date:"2026-02-21",tags:["nanobot","architecture","agent","mcp"],slug:"nanobot-agent-loop-architecture"};function t(n){const s={code:"code",em:"em",h1:"h1",h2:"h2",h3:"h3",hr:"hr",li:"li",ol:"ol",p:"p",pre:"pre",strong:"strong",ul:"ul",...n.components};return e.jsxs(e.Fragment,{children:[e.jsx(s.h1,{children:"Understanding Nanobot's AgentLoop: Architecture, MCP, and Skills"}),`
`,e.jsxs(s.p,{children:["The ",e.jsx(s.code,{children:"AgentLoop"})," acts as the central cognitive engine of the Nanobot system. Operating on a ",e.jsx(s.strong,{children:"Pull Architecture"}),", it continually polls a ",e.jsx(s.code,{children:"MessageBus"})," for inbound messages, processes them through a Large Language Model (LLM) to determine necessary actions, executes those actions using tools, and publishes the final output back to the bus."]}),`
`,e.jsxs(s.p,{children:["This post provides a deep dive into the architecture of ",e.jsx(s.code,{children:"AgentLoop.py"}),", how it uses the Model Context Protocol (MCP) to interact with external tools, and the workflow for handling custom agent skills."]}),`
`,e.jsx(s.hr,{}),`
`,e.jsx(s.h2,{children:"1. High-Level Architecture"}),`
`,e.jsxs(s.p,{children:["The ",e.jsx(s.code,{children:"AgentLoop"})," brings together several distinct sub-systems:"]}),`
`,e.jsxs(s.ul,{children:[`
`,e.jsxs(s.li,{children:[e.jsx(s.strong,{children:"LLM Provider"})," (",e.jsx(s.code,{children:"self.provider"}),"): The intelligence engine responsible for processing prompts and making decisions about tool calls."]}),`
`,e.jsxs(s.li,{children:[e.jsx(s.strong,{children:"Tools Registry"})," (",e.jsx(s.code,{children:"self.tools"}),"): A unified manager containing all available agent capabilities, including default tools (filesystem, web search) and dynamic tools (MCP)."]}),`
`,e.jsxs(s.li,{children:[e.jsx(s.strong,{children:"Session Manager"})," (",e.jsx(s.code,{children:"self.sessions"}),"): Tracks conversation history over the short term, organized uniquely by ",e.jsx(s.code,{children:"channel"})," and ",e.jsx(s.code,{children:"chat_id"}),"."]}),`
`,e.jsxs(s.li,{children:[e.jsx(s.strong,{children:"Context Builder"})," (",e.jsx(s.code,{children:"self.context"}),"): Continuously assembles the LLM's system prompt by aggregating persona details, skills, and memory."]}),`
`,e.jsxs(s.li,{children:[e.jsx(s.strong,{children:"Memory Store"})," (",e.jsx(s.code,{children:"self.memory"}),"): Handles vector and markdown-based long-term memory retrieval and writes."]}),`
`]}),`
`,e.jsx(s.hr,{}),`
`,e.jsx(s.h2,{children:"2. The Core Workflow"}),`
`,e.jsxs(s.h3,{children:["A. The Ingestion Loop (",e.jsx(s.code,{children:"run"})," and ",e.jsx(s.code,{children:"_process_message"}),")"]}),`
`,e.jsxs(s.p,{children:["When you execute ",e.jsx(s.code,{children:"await agent.run()"}),", the agent starts an infinite asynchronous loop, waiting for messages via ",e.jsx(s.code,{children:"self.bus.consume_inbound()"}),"."]}),`
`,e.jsx(s.p,{children:"Upon receiving a message, the workflow is as follows:"}),`
`,e.jsxs(s.ol,{children:[`
`,e.jsxs(s.li,{children:[e.jsx(s.strong,{children:"System & Command Handling"}),": Checks for system background messages or slash commands (like ",e.jsx(s.code,{children:"/new"})," to flush session history)."]}),`
`,e.jsxs(s.li,{children:[e.jsx(s.strong,{children:"Context Routing"}),": Sets the ",e.jsx(s.code,{children:"channel"})," and ",e.jsx(s.code,{children:"chat_id"})," on stateful tools (like ",e.jsx(s.code,{children:"MessageTool"})," or ",e.jsx(s.code,{children:"SpawnTool"}),") so the agent knows precisely where to route its outgoing actions."]}),`
`,e.jsxs(s.li,{children:[e.jsx(s.strong,{children:"Memory Consolidation Validation"}),": Checks if the short-term memory history exceeds the defined ",e.jsx(s.code,{children:"memory_window"}),". If it does, an asynchronous task (",e.jsx(s.code,{children:"_consolidate_memory"}),") is fired off to summarize oldest messages into the long-term ",e.jsx(s.code,{children:"MEMORY.md"})," file."]}),`
`,e.jsxs(s.li,{children:[e.jsx(s.strong,{children:"Context Construction"}),": Assembles the user's new message, the session history, and system configurations into a strict prompt structure."]}),`
`]}),`
`,e.jsxs(s.h3,{children:["B. The ReAct Execution Engine (",e.jsx(s.code,{children:"_run_agent_loop"}),")"]}),`
`,e.jsxs(s.p,{children:['This function serves as the "brain," implementing the classic ',e.jsx(s.strong,{children:"ReAct (Reason + Act)"})," loop pattern capped by a ",e.jsx(s.code,{children:"max_iterations"})," guard (default 20) to prevent infinite loops."]}),`
`,e.jsx(s.pre,{children:e.jsx(s.code,{className:"language-python",children:`# Pseudo-code representation
msg_context = build_messages()
while iterations < max_iterations:
    response = LLM(msg_context, tools)
    
    if response.has_tool_calls:
        for tool in response.tool_calls:
            result = tools.execute(tool.name, tool.arguments)
            msg_context.append(result)
        
        msg_context.append("Reflect on the results and decide next steps.")
    else:
        return response.content
`})}),`
`,e.jsxs(s.p,{children:["If the LLM triggers a tool call, the ",e.jsx(s.code,{children:"AgentLoop"})," automatically intercepts it, runs the Python tool implementation, appends the string result back into the prompt history, and forces the LLM to process the result to determine its next move."]}),`
`,e.jsx(s.hr,{}),`
`,e.jsx(s.h2,{children:"3. Handling MCP (Model Context Protocol) Tools"}),`
`,e.jsxs(s.p,{children:["Nanobot seamlessly integrates external capabilities through the Model Context Protocol. Rather than hardcoding APIs, the ",e.jsx(s.code,{children:"AgentLoop"})," connects to MCP servers and registers their tools dynamically."]}),`
`,e.jsx(s.h3,{children:"Connection Phase"}),`
`,e.jsxs(s.p,{children:["In ",e.jsx(s.code,{children:"_connect_mcp()"}),", the loop initializes an ",e.jsx(s.code,{children:"AsyncExitStack"})," to manage the lifecycle of external processes. It connects to the configured MCP servers over ",e.jsx(s.code,{children:"stdio"})," channels and dynamically extracts all available tools exposed by the server. These tools are injected into the unified ",e.jsx(s.code,{children:"ToolRegistry"})," alongside native tools like ",e.jsx(s.code,{children:"exec"}),"."]}),`
`,e.jsx(s.h3,{children:"Execution Phase"}),`
`,e.jsxs(s.p,{children:["Because MCP tools are registered directly into the ",e.jsx(s.code,{children:"ToolRegistry"}),", the ",e.jsx(s.code,{children:"AgentLoop"})," doesn't differentiate between them and native Python tools."]}),`
`,e.jsxs(s.p,{children:["When the LLM requests an MCP tool (e.g., ",e.jsx(s.code,{children:"github_get_issue"}),"):"]}),`
`,e.jsxs(s.ol,{children:[`
`,e.jsxs(s.li,{children:[e.jsx(s.code,{children:"_run_agent_loop"})," extracts the JSON payload and calls ",e.jsx(s.code,{children:"self.tools.execute()"}),"."]}),`
`,e.jsxs(s.li,{children:["The ",e.jsx(s.code,{children:"ToolRegistry"})," identifies it as an MCP tool and forwards the JSON-RPC request across the ",e.jsx(s.code,{children:"stdio"})," boundary to the external server."]}),`
`,e.jsxs(s.li,{children:["The server replies with the result, which is funneled back as a string to the ",e.jsx(s.code,{children:"AgentLoop"}),", and ultimately back into the LLM's context window."]}),`
`]}),`
`,e.jsx(s.hr,{}),`
`,e.jsx(s.h2,{children:"4. The Flow of Custom Skills"}),`
`,e.jsxs(s.p,{children:["Custom skills in Nanobot extend the agent's capabilities via explicit instruction sets stored in ",e.jsx(s.code,{children:"<workspace>/skills/<skill-name>/SKILL.md"}),"."]}),`
`,e.jsxs(s.p,{children:["Here is the exact flow of how ",e.jsx(s.code,{children:"AgentLoop"})," and ",e.jsx(s.code,{children:"ContextBuilder"})," handle these skills during prompt generation:"]}),`
`,e.jsxs(s.ol,{children:[`
`,e.jsxs(s.li,{children:[e.jsx(s.strong,{children:"Progressive Loading initiation:"})," The ",e.jsx(s.code,{children:"ContextBuilder.build_system_prompt()"})," queries the ",e.jsx(s.code,{children:"SkillsLoader"})," to partition skills."]}),`
`,e.jsxs(s.li,{children:[e.jsxs(s.strong,{children:["Always-On Skills (",e.jsx(s.code,{children:"always_on=true"}),"):"]})," If a skill is marked as ",e.jsx(s.code,{children:"always_on"}),", the ",e.jsx(s.code,{children:"ContextBuilder"})," opens the ",e.jsx(s.code,{children:"SKILL.md"})," file and physically embeds the entire markdown instruction set directly into the LLM's system prompt prior to every message."]}),`
`,e.jsxs(s.li,{children:[e.jsxs(s.strong,{children:["Available Skills (",e.jsx(s.code,{children:"always_on=false"}),"):"]})," To preserve context window limits, the ",e.jsx(s.code,{children:"ContextBuilder"})," does not inject the entire file for standard skills. Instead, it generates a summary dictionary mapping the skill's name to a short description."]}),`
`,e.jsxs(s.li,{children:[e.jsx(s.strong,{children:"Agent Discovery and Usage:"})," The system prompt explicitly instructs the LLM: ",e.jsx(s.em,{children:'"The following skills extend your capabilities. To use a skill, read its SKILL.md file using the read_file tool."'})]}),`
`,e.jsxs(s.li,{children:[e.jsx(s.strong,{children:"Execution:"})," If the LLM determines a standard skill is required based on its summarized description, it will first generate a tool call to ",e.jsx(s.code,{children:"read_file"})," targeting the skill's ",e.jsx(s.code,{children:"SKILL.md"}),". Once the LLM reads the file's contents, it follows the explicit instructions—often utilizing the ",e.jsx(s.code,{children:"exec"})," tool to run the companion Bash or Python scripts associated with that skill."]}),`
`]}),`
`,e.jsx(s.p,{children:"By combining native ReAct execution, universal MCP integration, and progressive contextual loading for custom skills, Nanobot achieves maximum flexibility and extensibility while strictly managing its token overhead."})]})}function r(n={}){const{wrapper:s}=n.components||{};return s?e.jsx(s,{...n,children:e.jsx(t,{...n})}):t(n)}export{r as default,i as frontmatter};
