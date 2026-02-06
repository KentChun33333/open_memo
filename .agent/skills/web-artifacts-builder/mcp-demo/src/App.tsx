import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Terminal, Server, FileCode, Database, CheckCircle2, XCircle, Activity, Zap } from 'lucide-react'

// --- Visual Components ---

function ConnectionStatus({ connected, latency }: { connected: boolean; latency: number }) {
  return (
    <div className="flex items-center space-x-2">
      {connected ? (
        <CheckCircle2 className="h-4 w-4 text-green-500" />
      ) : (
        <XCircle className="h-4 w-4 text-red-500" />
      )}
      <span className="text-sm font-medium">
        {connected ? `Connected (${latency}ms)` : 'Disconnected'}
      </span>
    </div>
  )
}

function ToolUsageCard({ tools }: { tools: { name: string; used: boolean; usageCount: number }[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileCode className="h-5 w-5" />
          Available Tools
        </CardTitle>
        <CardDescription>Tools exposed by MCP server</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {tools.map((tool) => (
            <div key={tool.name} className="flex items-center justify-between">
              <div className="flex flex-col">
                <span className="font-medium">{tool.name}</span>
                <span className="text-xs text-muted-foreground">
                  {tool.used ? `Used ${tool.usageCount} times` : 'Available'}
                </span>
              </div>
              {tool.used ? (
                <Badge variant="default">Active</Badge>
              ) : (
                <Badge variant="outline">Ready</Badge>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

function MemoryFlow({ memoryUsage, history }: { memoryUsage: number; history: string[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Database className="h-5 w-5" />
          Memory Context
        </CardTitle>
        <CardDescription>Context retention and history</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <div className="flex justify-between mb-2">
              <span className="text-sm font-medium">Memory Usage</span>
              <span className="text-sm text-muted-foreground">{Math.round(memoryUsage)}%</span>
            </div>
            <Progress value={memoryUsage} className="h-2" />
          </div>
          <div className="space-y-2">
            <h4 className="text-sm font-medium">Recent Context</h4>
            <div className="bg-muted rounded-md p-3 space-y-2 max-h-[200px] overflow-y-auto">
              {history.length === 0 ? (
                <p className="text-sm text-muted-foreground italic">No context history yet</p>
              ) : (
                history.slice(-5).reverse().map((msg, i) => (
                  <div key={i} className="text-xs border-l-2 border-border pl-2">
                    {msg}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// --- Main App Component ---

function App() {
  const [connected, setConnected] = useState(false)
  const [latency, setLatency] = useState(0)
  const [memoryUsage, setMemoryUsage] = useState(0)
  const [history, setHistory] = useState<string[]>([])
  const [tools, setTools] = useState([
    { name: 'fetch_web_content', used: false, usageCount: 0 },
    { name: 'read_file', used: false, usageCount: 0 },
    { name: 'write_file', used: false, usageCount: 0 },
    { name: 'list_files', used: false, usageCount: 0 },
    { name: 'execute_command', used: false, usageCount: 0 }
  ])
  const [logs, setLogs] = useState<string[]>([])
  const [activeTab, setActiveTab] = useState('overview')

  // Simulate connection
  const toggleConnection = () => {
    if (!connected) {
      // Connect
      setConnected(true)
      setLatency(Math.floor(Math.random() * 100) + 20)
      const connectLog = `MCP server connected at ${new Date().toLocaleTimeString()}`
      setLogs(prev => [connectLog, ...prev])
    } else {
      // Disconnect
      setConnected(false)
      setLatency(0)
      setMemoryUsage(0)
      setHistory([])
      const disconnectLog = `MCP server disconnected at ${new Date().toLocaleTimeString()}`
      setLogs(prev => [disconnectLog, ...prev])
    }
  }

  // Simulate context updates
  useEffect(() => {
    const interval = setInterval(() => {
      if (connected) {
        setMemoryUsage(prev => {
          const next = Math.min(prev + Math.random() * 5, 100)
          return Math.round(next * 100) / 100
        })
      }
      return () => clearInterval(interval)
    }, 2000)
  }, [connected])

  // Simulate tool usage and memory growth
  const simulateToolUsage = () => {
    if (!connected) return
    
    const availableTools = tools.filter(t => !t.used)
    if (availableTools.length === 0) return

    const randomTool = availableTools[Math.floor(Math.random() * availableTools.length)]
    
    setTools(prevTools => 
      prevTools.map(tool => tool.name === randomTool.name 
        ? { ...tool, used: true, usageCount: tool.usageCount + 1 }
        : tool
    ))

    const logMessage = `Used tool: ${randomTool.name}`
    setHistory(prev => [...prev, logMessage])
    setLogs(prev => [logMessage, ...prev])
  }

  return (
    <div className="min-h-screen bg-background p-8 font-sans">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Model Context Protocol (MCP)</h1>
            <p className="text-muted-foreground mt-2">Interactive demonstration of MCP architecture and workflow</p>
          </div>
          <Button 
            variant={connected ? "destructive" : "default"} 
            onClick={toggleConnection}
            className="flex items-center gap-2"
          >
            {connected ? (
              <>
                <XCircle className="h-4 w-4" />
                Disconnect
              </>
            ) : (
              <>
                <Server className="h-4 w-4" />
                Connect to Server
              </>
            )}
          </Button>
        </div>

        {/* Status Bar */}
        <div className="flex items-center gap-6 bg-muted/50 p-3 rounded-lg">
          <ConnectionStatus connected={connected} latency={latency} />
          <div className="h-4 w-px bg-border"></div>
          <div className="flex items-center gap-2 text-sm">
            <Terminal className="h-4 w-4" />
            <span>Node.js v18.12.0</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <Zap className="h-4 w-4" />
            <span>12ms avg latency</span>
          </div>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList className="grid grid-cols-3">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="tools">Tools & Functions</TabsTrigger>
            <TabsTrigger value="memory">Memory Context</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview">
            <div className="grid gap-6 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5" />
                    Context Flow
                  </CardTitle>
                  <CardDescription>How MCP processes and retains context</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center gap-2 text-sm">
                    <div className="h-5 w-5 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-xs">
                      1
                    </div>
                    <span>User input received</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <div className="h-5 w-5 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-xs">
                      2
                    </div>
                    <span>Context window built</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <div className="h-5 w-5 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-xs">
                      3
                    </div>
                    <span>Tools selected and invoked</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <div className="h-5 w-5 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-xs">
                      4
                    </div>
                    <span>Response generated with context</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <div className="h-5 w-5 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-xs">
                      5
                    </div>
                    <span>Memory updated and persisted</span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Database className="h-5 w-5" />
                    System State
                  </CardTitle>
                  <CardDescription>Real-time system metrics</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">Memory Usage</span>
                    <span className="text-sm">{memoryUsage}%</span>
                  </div>
                  <Progress value={memoryUsage} className="h-2" />
                  
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">Context Size</span>
                    <span className="text-sm">15.2 KB</span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">Active Tools</span>
                    <span className="text-sm">{tools.filter(t => t.used).length} / {tools.length}</span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">Connected Clients</span>
                    <span className="text-sm">1</span>
                  </div>
                </CardContent>
              </Card>
            </div>
            
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Terminal className="h-5 w-5" />
                  Event Log
                </CardTitle>
                <CardDescription>Recent MCP events and status changes</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="bg-muted rounded-md p-3 h-48 overflow-y-auto font-mono text-sm space-y-1">
                  {logs.length === 0 ? (
                    <p className="text-muted-foreground italic">No events yet</p>
                  ) : (
                    logs.map((log, i) => (
                      <div key={i} className="text-rose-500">
                        <span className="text-primary mr-2">[{new Date().toLocaleTimeString()}]</span>
                        {log}
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Tools Tab */}
          <TabsContent value="tools">
            <ToolUsageCard tools={tools} />
            <div className="mt-4">
              <Button 
                disabled={!connected} 
                onClick={simulateToolUsage}
                className="w-full"
              >
                <Zap className="mr-2 h-4 w-4" />
                Simulate Tool Usage
              </Button>
            </div>
          </TabsContent>

          {/* Memory Tab */}
          <TabsContent value="memory">
            <MemoryFlow memoryUsage={memoryUsage} history={history} />
          </TabsContent>
        </Tabs>

        {/* Footer */}
        <div className="border-t pt-4 text-center text-sm text-muted-foreground">
          <p>Model Context Protocol Implementation Demo</p>
          <p className="mt-1">Interactive frontend artifact for demonstrating MCP architecture</p>
        </div>
      </div>
    </div>
  )
}

export default App
