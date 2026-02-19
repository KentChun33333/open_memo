
import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { Terminal, Database, Cpu, User, ArrowRight, Play, FileText } from 'lucide-react'

type LogEntry = {
  id: number;
  source: 'User' | 'Orchestrator' | 'MCP Server';
  message: string;
  type: 'info' | 'request' | 'response';
  timestamp: string;
}

function App() {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [status, setStatus] = useState<'IDLE' | 'PLANNING' | 'EXECUTING'>('IDLE')

  const addLog = (source: LogEntry['source'], message: string, type: LogEntry['type'] = 'info') => {
    const entry: LogEntry = {
      id: Date.now(),
      source,
      message,
      type,
      timestamp: new Date().toLocaleTimeString()
    }
    setLogs(prev => [...prev, entry])
  }

  const simulateListFiles = async () => {
    setStatus('PLANNING')
    addLog('User', 'Request: "List files in current directory"', 'request')

    setTimeout(() => {
      addLog('Orchestrator', 'Analyzing request... Identified tool: list_directory', 'info')
      setStatus('EXECUTING')

      setTimeout(() => {
        addLog('Orchestrator', 'Sending JSON-RPC Request: { method: "tools/call", params: { name: "list_directory" } }', 'request')

        setTimeout(() => {
          addLog('MCP Server', 'Handling list_directory...', 'info')

          setTimeout(() => {
            addLog('MCP Server', 'JSON-RPC Response: { result: { files: ["App.tsx", "main.tsx", "index.css"] } }', 'response')
            setStatus('IDLE')
          }, 800)
        }, 800)
      }, 800)
    }, 800)
  }

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-50 p-8 font-sans">
      <header className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Model Context Protocol</h1>
          <p className="text-neutral-400">Agentic Architecture Demonstration</p>
        </div>
        <Badge variant={status === 'IDLE' ? 'secondary' : 'default'} className="text-sm px-4 py-1">
          Status: {status}
        </Badge>
      </header>

      <main className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Architecture View */}
        <Card className="lg:col-span-2 bg-neutral-900 border-neutral-800">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Cpu className="h-5 w-5 text-blue-400" />
              System Architecture
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center min-h-[400px] gap-8 relative">

            {/* Diagram Nodes */}
            <div className="flex items-center justify-between w-full max-w-2xl px-8">
              {/* User Node */}
              <div className="flex flex-col items-center gap-2 z-10">
                <div className={`h-16 w-16 rounded-full bg-neutral-800 border-2 flex items-center justify-center transition-all duration-300 ${status !== 'IDLE' ? 'border-green-500 shadow-[0_0_15px_rgba(34,197,94,0.3)]' : 'border-neutral-700'}`}>
                  <User className="h-8 w-8 text-neutral-300" />
                </div>
                <span className="font-semibold text-neutral-300">User</span>
              </div>

              <ArrowRight className={`h-6 w-6 text-neutral-600 transition-opacity ${status !== 'IDLE' ? 'opacity-100 animate-pulse' : 'opacity-30'}`} />

              {/* Orchestrator Node */}
              <div className="flex flex-col items-center gap-2 z-10">
                <div className={`h-20 w-20 rounded-xl bg-blue-950/30 border-2 flex items-center justify-center transition-all duration-300 ${status === 'PLANNING' || status === 'EXECUTING' ? 'border-blue-500 shadow-[0_0_20px_rgba(59,130,246,0.5)]' : 'border-blue-900'}`}>
                  <Cpu className="h-10 w-10 text-blue-400" />
                </div>
                <span className="font-semibold text-blue-400">LLM Orchestrator</span>
              </div>

              <ArrowRight className={`h-6 w-6 text-neutral-600 transition-opacity ${status === 'EXECUTING' ? 'opacity-100 animate-pulse' : 'opacity-30'}`} />

              {/* MCP Server Node */}
              <div className="flex flex-col items-center gap-2 z-10">
                <div className={`h-16 w-16 rounded-lg bg-orange-950/30 border-2 flex items-center justify-center transition-all duration-300 ${status === 'EXECUTING' ? 'border-orange-500 shadow-[0_0_15px_rgba(249,115,22,0.3)]' : 'border-orange-900'}`}>
                  <Database className="h-8 w-8 text-orange-400" />
                </div>
                <span className="font-semibold text-orange-400">MCP Server</span>
              </div>
            </div>

            {/* Connection Lines (Visual Decor) */}
            <div className="absolute top-1/2 left-0 w-full h-0.5 bg-neutral-800 -z-0"></div>

          </CardContent>
          <CardContent className="border-t border-neutral-800 pt-6">
            <div className="flex gap-4">
              <Button onClick={simulateListFiles} disabled={status !== 'IDLE'} className="gap-2">
                <Play className="h-4 w-4" />
                Simulate: List Files
              </Button>
              <Button variant="secondary" disabled className="gap-2">
                <FileText className="h-4 w-4" />
                Simulate: Read File (Coming Soon)
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Telemetry Panel */}
        <Card className="bg-black border-neutral-800 flex flex-col h-[600px]">
          <CardHeader className="bg-neutral-900/50 pb-3">
            <CardTitle className="flex items-center gap-2 text-sm font-mono text-neutral-400">
              <Terminal className="h-4 w-4" />
              Telemetry Log (JSON-RPC)
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0 flex-1 overflow-hidden font-mono text-xs">
            <ScrollArea className="h-full p-4">
              <div className="flex flex-col gap-3">
                {logs.length === 0 && <span className="text-neutral-600 italic">Analysis engine ready. Waiting for events...</span>}
                {logs.map((log) => (
                  <div key={log.id} className="flex flex-col gap-1 anim-fade-in">
                    <div className="flex items-center gap-2">
                      <span className="text-neutral-500">[{log.timestamp}]</span>
                      <Badge variant="outline" className={`text-[10px] h-5 px-1 
                         ${log.source === 'User' ? 'text-green-400 border-green-900' :
                          log.source === 'Orchestrator' ? 'text-blue-400 border-blue-900' :
                            'text-orange-400 border-orange-900'}`}>
                        {log.source.toUpperCase()}
                      </Badge>
                    </div>
                    <p className={`pl-2 border-l-2 ml-1 ${log.type === 'request' ? 'border-yellow-600 text-yellow-100' : log.type === 'response' ? 'border-green-600 text-green-100' : 'border-neutral-700 text-neutral-300'}`}>
                      {log.message}
                    </p>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}

export default App
