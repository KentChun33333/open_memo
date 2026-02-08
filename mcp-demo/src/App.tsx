import { useState, useEffect } from 'react'
import { 
  Server, 
  Terminal, 
  Cpu, 
  FileCode, 
  Activity, 
  Play, 
  Settings,
  Code2,
  Box,
  AlertCircle,
  CheckCircle2,
  Loader2
} from 'lucide-react'

// MCP Client Component - Demonstrates Model Context Protocol
function MCPClient() {
  const [connected, setConnected] = useState(false)
  const [logs, setLogs] = useState<string[]>([])
  const [resources, setResources] = useState<string[]>([])
  const [tools, setTools] = useState<string[]>([])
  const [selectedTool, setSelectedTool] = useState<string>('')
  const [selectedResource, setSelectedResource] = useState<string>('')
  const [input, setInput] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [response, setResponse] = useState<string>('')

  // Initialize MCP client
  useEffect(() => {
    simulateMCPConnection()
  }, [])

  const simulateMCPConnection = () => {
    setConnected(true)
    setLogs(prev => [...prev, '[SYSTEM] MCP Client initialized'])
    setResources([
      'file:///workspace/README.md',
      'file:///workspace/src/main.ts',
      'https://api.github.com/repos/modelcontextprotocol/spec',
      'env://environment-variables'
    ])
    setTools([
      'search_codebase',
      'read_resource',
      'edit_file',
      'list_directory',
      'run_terminal_command'
    ])
    setLogs(prev => [...prev, '[SYSTEM] Discovered resources:', ...resources])
    setLogs(prev => [...prev, '[SYSTEM] Available tools:', ...tools])
  }

  const handleToolInvocation = async () => {
    if (!selectedTool) {
      setLogs(prev => [...prev, '[ERROR] No tool selected'])
      return
    }

    setIsProcessing(true)
    setResponse('')
    
    // Simulate tool execution
    setLogs(prev => [...prev, `[TOOL] Invoking: ${selectedTool}`])
    
    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 1200))
    
    let toolResponse = ''
    
    switch (selectedTool) {
      case 'search_codebase':
        toolResponse = `Searching codebase for: "${input || 'default query'}"\n` +
                      `Found 3 relevant matches:\n` +
                      `1. line 42: const mcpConfig = { ... } // Model Context Protocol config\n` +
                      `2. line 87: function handleMCPConnection() { ... }\n` +
                      `3. line 156: export const MCPClient = () => { ... }`
        break
      case 'read_resource':
        toolResponse = `Reading resource: ${selectedResource || 'default resource'}\n\n` +
                      `CONTENT PREVIEW:\n` +
                      `----------------------------------------\n` +
                      `// Model Context Protocol Implementation\n` +
                      `// This file contains MCP client logic\n\n` +
                      `function connectToServer() {\n  // MCP handshake\n  return { protocol: 'mcp', version: '1.0' }\n}`
        break
      case 'edit_file':
        toolResponse = `Editing file with the following changes:\n` +
                      `• Added: import { MCPClient } from './mcp-client'\n` +
                      `• Modified: configureMCP() method\n` +
                      `• Removed: Unused import statements`
        break
      case 'list_directory':
        toolResponse = `Listing directory: ${input || '/workspace'}\n\n` +
                      `Directory contents:\n` +
                      `drwxr-xr-x src/\n` +
                      `drwxr-xr-x components/\n` +
                      `drwxr-xr-x utils/\n` +
                      `-rw-r--r-- package.json\n` +
                      `-rw-r--r-- README.md`
        break
      default:
        toolResponse = `Executing tool: ${selectedTool}\n` +
                      `Parameters: ${input}\n\n` +
                      `Tool executed successfully with the following output:\n` +
                      `✓ Operation completed\n` +
                      `✓ Context updated\n` +
                      `✓ Status: ready`
    }
    
    setResponse(toolResponse)
    setLogs(prev => [...prev, `[TOOL] Response received from ${selectedTool}`])
    setIsProcessing(false)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Server className="w-6 h-6 text-blue-500" />
            Model Context Protocol
          </h2>
          <p className="text-gray-500 dark:text-gray-400">Interactive MCP Client Interface</p>
        </div>
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'} animate-pulse`} />
          <span className={`font-medium ${connected ? 'text-green-600' : 'text-red-600'}`}>
            {connected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Resources Panel */}
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-lg border border-slate-200 dark:border-slate-700">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Box className="w-5 h-5 text-purple-500" />
            Resources
          </h3>
          <div className="space-y-3">
            {resources.map((resource, index) => (
              <div 
                key={index}
                className={`p-3 rounded-lg cursor-pointer transition-all ${
                  selectedResource === resource 
                    ? 'bg-blue-50 dark:bg-blue-900/30 border-blue-300 dark:border-blue-700' 
                    : 'hover:bg-slate-50 dark:hover:bg-slate-700/50 border border-slate-200 dark:border-slate-700'
                }`}
                onClick={() => setSelectedResource(resource)}
              >
                <div className="font-mono text-sm text-slate-700 dark:text-slate-300 truncate">
                  {resource}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Tools Panel */}
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-lg border border-slate-200 dark:border-slate-700">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Code2 className="w-5 h-5 text-green-500" />
            Available Tools
          </h3>
          <div className="space-y-3">
            {tools.map((tool, index) => (
              <div 
                key={index}
                className={`p-3 rounded-lg cursor-pointer transition-all ${
                  selectedTool === tool 
                    ? 'bg-green-50 dark:bg-green-900/30 border-green-300 dark:border-green-700' 
                    : 'hover:bg-slate-50 dark:hover:bg-slate-700/50 border border-slate-200 dark:border-slate-700'
                }`}
                onClick={() => setSelectedTool(tool)}
              >
                <div className="font-medium text-slate-700 dark:text-slate-300">{tool}</div>
                <div className="text-xs text-slate-500">
                  {tool === 'search_codebase' && 'Query codebase for relevant context'}
                  {tool === 'read_resource' && 'Read content from registered resources'}
                  {tool === 'edit_file' && 'Make precise edits to files'}
                  {tool === 'list_directory' && 'List contents of directories'}
                  {tool === 'run_terminal_command' && 'Execute commands in terminal'}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Interaction Panel */}
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-lg border border-slate-200 dark:border-slate-700 flex flex-col">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5 text-orange-500" />
            Interaction
          </h3>
          
          <div className="flex-1 space-y-4">
            <div>
              <label className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-1 block">
                Input/Parameters
              </label>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Enter parameters or query"
                className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
              />
            </div>

            <div>
              <label className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-1 block">
                Selected Tool
              </label>
              <div className="px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-slate-50 dark:bg-slate-900 text-slate-800 dark:text-slate-200">
                {selectedTool || 'No tool selected'}
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-1 block">
                Selected Resource
              </label>
              <div className="px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-slate-50 dark:bg-slate-900 text-slate-800 dark:text-slate-200">
                {selectedResource || 'No resource selected'}
              </div>
            </div>

            <button
              onClick={handleToolInvocation}
              disabled={!selectedTool || isProcessing}
              className={`w-full py-3 rounded-lg flex items-center justify-center gap-2 transition-all ${
                !selectedTool || isProcessing
                  ? 'bg-slate-300 dark:bg-slate-700 cursor-not-allowed text-slate-500'
                  : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl'
              }`}
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  Invoke Tool
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Logs Panel */}
      <div className="bg-slate-900 rounded-xl p-6 shadow-lg">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Terminal className="w-5 h-5 text-green-400" />
          Protocol Logs
        </h3>
        <div className="bg-slate-950 rounded-lg p-4 font-mono text-sm h-64 overflow-y-auto border border-slate-800">
          {logs.map((log, index) => (
            <div key={index} className="mb-1">
              <span className="text-slate-500">[{new Date().toLocaleTimeString()}]</span>{' '}
              {log.startsWith('[ERROR]') ? (
                <span className="text-red-400">{log}</span>
              ) : log.startsWith('[TOOL]') ? (
                <span className="text-blue-400">{log}</span>
              ) : log.startsWith('[SYSTEM]') ? (
                <span className="text-green-400">{log}</span>
              ) : (
                <span className="text-slate-300">{log}</span>
              )}
            </div>
          ))}
          <div className="animate-pulse">
            <span className="text-blue-400">_</span>
          </div>
        </div>
      </div>

      {/* Response Panel */}
      {response && (
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-lg border border-slate-200 dark:border-slate-700">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-green-500" />
            Tool Response
          </h3>
          <div className="bg-slate-50 dark:bg-slate-900 rounded-lg p-4 font-mono text-sm whitespace-pre-wrap text-slate-800 dark:text-slate-300">
            {response}
          </div>
        </div>
      )}

      {/* MCP Protocol Info */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-slate-800 dark:to-slate-800/50 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <FileCode className="w-5 h-5 text-blue-500" />
          Model Context Protocol Overview
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white dark:bg-slate-900 rounded-lg p-4">
            <div className="font-semibold text-blue-600 dark:text-blue-400 mb-2">Resources</div>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Applications can register resources (files, URLs, etc.) that models can access
            </p>
          </div>
          <div className="bg-white dark:bg-slate-900 rounded-lg p-4">
            <div className="font-semibold text-green-600 dark:text-green-400 mb-2">Tools</div>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Models can invoke tools to perform actions and retrieve information
            </p>
          </div>
          <div className="bg-white dark:bg-slate-900 rounded-lg p-4">
            <div className="font-semibold text-purple-600 dark:text-purple-400 mb-2">Context</div>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Automatic context management enables rich, stateful interactions
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

function App() {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-12 text-center">
          <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Model Context Protocol
          </h1>
          <p className="text-xl text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
            An interactive demonstration of how MCP enables applications to provide context to AI models through standardized tools and resources
          </p>
        </div>
        <MCPClient />
        <div className="mt-12 text-center text-slate-500 text-sm">
          <p>Interactive MCP Client Demo • Model Context Protocol Implementation</p>
        </div>
      </div>
    </div>
  )
}

export default App
