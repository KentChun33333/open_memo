import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Terminal, Database, FileText, Send, Code, Play, Activity } from 'lucide-react'

type LogType = 'client-request' | 'server-response' | 'tool-call' | 'resource-fetch' | 'error'
type LogItem = {
  id: string
  type: LogType
  timestamp: string
  title: string
  details: string
  payload?: object
}

const tools = [
  { id: 't1', name: 'SearchKnowledgeBase', description: 'Search internal documentation', params: 'query: string' },
  { id: 't2', name: 'GetCurrentWeather', description: 'Get weather for a location', params: 'location: string' },
  { id: 't3', name: 'ListFiles', description: 'List files in a directory', params: 'path?: string' },
  { id: 't4', name: 'ExecuteSQL', description: 'Execute read-only SQL query', params: 'query: string' },
]

const resources = [
  { id: 'r1', title: 'Project README', type: 'text/markdown', uri: 'file://docs/README.md' },
  { id: 'r2', title: 'API Schema', type: 'application/json', uri: 'file://docs/api.schema.json' },
  { id: 'r3', title: 'Environment Config', type: 'application/env', uri: 'file://.env.example' },
]

export default function App() {
  const [logs, setLogs] = useState<LogItem[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [autoScroll, setAutoScroll] = useState(true)
  const [activeTool, setActiveTool] = useState<string>('')

  const addLog = (type: LogType, title: string, details: string, payload?: object) => {
    const newLog: LogItem = {
      id: Math.random().toString(36).substring(7),
      type,
      timestamp: new Date().toLocaleTimeString(),
      title,
      details,
      payload,
    }
    setLogs((prev) => [...prev, newLog])
  }

  useEffect(() => {
    if (autoScroll) {
      const div = document.getElementById('log-container')
      if (div) div.scrollTop = div.scrollHeight
    }
  }, [logs, autoScroll])

  const handleConnect = () => {
    setIsConnected(true)
    addLog('client-request', 'Connect to MCP Server', 'Establishing connection...')
    setTimeout(() => {
      addLog('server-response', 'Connected to MCP Server', 'WebSocket connection established')
      addLog('server-response', 'Resources Advertised', `Loaded ${resources.length} resources`)
    }, 800)
  }

  const handleDisconnect = () => {
    setIsConnected(false)
    addLog('client-request', 'Disconnect', 'Closing connection...')
  }

  const handleToolCall = (toolId: string) => {
    const tool = tools.find((t) => t.id === toolId)
    if (!tool) return

    addLog('client-request', `Tool Call: ${tool.name}`, tool.params)

    // Simulate server response
    const toolName = tool.name
    setTimeout(() => {
      addLog('tool-call', `Executing: ${toolName}`, `Running ${toolName} with parameters...`)
      setTimeout(() => {
        let result = ''
        switch (toolName) {
          case 'SearchKnowledgeBase':
            result = JSON.stringify({ matches: ['Docs: /api/create', 'Docs: /api/read'], count: 2 }, null, 2)
            break
          case 'GetCurrentWeather':
            result = JSON.stringify({ temperature: 72, unit: '°F', condition: 'Sunny' }, null, 2)
            break
          case 'ListFiles':
            result = JSON.stringify(['src/', 'docs/', 'config.ts'], null, 2)
            break
          case 'ExecuteSQL':
            result = JSON.stringify([
              { id: 1, name: 'Alice', role: 'admin' },
              { id: 2, name: 'Bob', role: 'developer' },
            ], null, 2)
            break
        }
        addLog('server-response', `Result from ${toolName}`, `Query completed`, { result })
      }, 600)
    }, 300)
  }

  return (
    <div className="flex flex-col h-screen bg-background font-sans text-foreground">
      <header className="border-b px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary text-primary-foreground rounded-lg">
            <Terminal className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold">MCP Explorer</h1>
            <p className="text-sm text-muted-foreground">Model Context Protocol Demo</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <Badge
            variant={isConnected ? 'default' : 'secondary'}
            className={isConnected ? 'bg-emerald-500 hover:bg-emerald-600' : ''}
          >
            {isConnected ? 'Connected' : 'Disconnected'}
          </Badge>
          {isConnected ? (
            <Button size="sm" variant="outline" onClick={handleDisconnect}>
              Disconnect
            </Button>
          ) : (
            <Button size="sm" onClick={handleConnect}>
              Connect to Server
            </Button>
          )}
        </div>
      </header>

      <main className="flex-1 flex gap-6 p-6">
        {/* Left Panel: Tools */}
        <Card className="flex-1 min-w-[300px] max-w-[350px] flex flex-col">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Tools
            </CardTitle>
            <CardDescription>
              Available tools the server can execute
            </CardDescription>
          </CardHeader>
          <CardContent className="flex-1 overflow-hidden">
            <ScrollArea className="h-[calc(100%-100px)] pr-4">
              <div className="space-y-3">
                {tools.map((tool) => (
                  <Card key={tool.id} className="hover:border-primary transition-colors">
                    <CardContent className="pt-4">
                      <div className="flex justify-between items-start mb-2">
                        <Badge variant="outline">{tool.name}</Badge>
                        <Label className="text-xs text-muted-foreground">
                          {tool.id === activeTool ? 'Active' : 'Ready'}
                        </Label>
                      </div>
                      <p className="text-sm text-muted-foreground mb-3">{tool.description}</p>
                      <div className="text-xs bg-muted p-2 rounded mb-3 font-mono">
                        <span className="text-primary">params:</span> {tool.params}
                      </div>
                      <Button
                        variant="secondary"
                        size="sm"
                        className="w-full"
                        onClick={() => handleToolCall(tool.id)}
                        disabled={!isConnected}
                      >
                        <Play className="h-3 w-3 mr-2" />
                        Call Tool
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>

        {/* Middle Panel: Log/Timeline */}
        <Card className="flex-1 min-w-[400px] flex flex-col">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Terminal className="h-5 w-5" />
              Message Log
            </CardTitle>
            <CardDescription>
              Real-time communication timeline between client and server
            </CardDescription>
          </CardHeader>
          <CardContent className="flex-1 overflow-hidden">
            <div className="flex flex-col gap-4 h-full">
              <div className="flex items-center justify-between">
                <Label htmlFor="auto-scroll">Auto-scroll logs</Label>
                <Switch id="auto-scroll" checked={autoScroll} onCheckedChange={setAutoScroll} />
              </div>
              <ScrollArea id="log-container" className="flex-1 pr-2">
                <div className="space-y-4">
                  {logs.length === 0 && (
                    <div className="text-center text-muted-foreground mt-12">
                      <Activity className="h-12 w-12 mx-auto mb-3 opacity-30" />
                      <p>No activity yet. Connect to start.</p>
                    </div>
                  )}
                  {logs.map((log) => (
                    <div key={log.id} className="border-l-4 pl-4"
                      style={{ borderLeftColor:
                        log.type === 'client-request' ? '#4f46e5' :
                        log.type === 'server-response' ? '#10b981' :
                        log.type === 'tool-call' ? '#f59e0b' :
                        log.type === 'resource-fetch' ? '#3b82f6' :
                        '#ef4444'
                      }}>
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant="outline" className="text-xs capitalize">
                          {log.type}
                        </Badge>
                        <span className="text-xs text-muted-foreground font-mono">{log.timestamp}</span>
                      </div>
                      <div className="font-medium text-sm mb-1">{log.title}</div>
                      <div className="text-xs text-muted-foreground mb-2">{log.details}</div>
                      {log.payload && (
                        <div className="bg-muted p-2 rounded text-xs font-mono overflow-x-auto">
                          <pre>{JSON.stringify(log.payload, null, 2)}</pre>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </ScrollArea>
              <div className="flex justify-center text-xs text-muted-foreground py-2">
                <Send className="h-3 w-3 mr-1" />
                {isConnected ? 'Listening for events...' : 'Not connected to server'}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Right Panel: Resources & Prompts */}
        <Card className="flex-1 min-w-[300px] max-w-[300px] flex flex-col">
          <Tabs defaultValue="resources" className="flex-1 flex flex-col">
            <CardHeader className="pb-2">
              <TabsList className="w-full">
                <TabsTrigger value="resources" className="flex-1">
                  <FileText className="h-4 w-4 mr-2" />
                  Resources
                </TabsTrigger>
                <TabsTrigger value="contexts" className="flex-1">
                  <Code className="h-4 w-4 mr-2" />
                  Contexts
                </TabsTrigger>
              </TabsList>
            </CardHeader>
            <CardContent className="flex-1 overflow-hidden">
              <TabsContent value="resources" className="h-full">
                <ScrollArea className="h-full pr-2">
                  <div className="space-y-3">
                    <Alert className="mb-2">
                      <Database className="h-4 w-4" />
                      <AlertTitle>Connection Required</AlertTitle>
                      <AlertDescription>
                        Resources are only available after connecting to the server
                      </AlertDescription>
                    </Alert>
                    {resources.map((res) => (
                      <Card key={res.id}>
                        <CardContent className="pt-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium text-sm">{res.title}</span>
                            <Badge variant="secondary" className="text-xs">{res.type.split('/')[1]}</Badge>
                          </div>
                          <code className="text-xs text-muted-foreground font-mono break-all">
                            {res.uri}
                          </code>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </ScrollArea>
              </TabsContent>
              <TabsContent value="contexts" className="h-full">
                <ScrollArea className="h-full pr-2">
                  <div className="text-center text-muted-foreground mt-12">
                    <Code className="h-12 w-12 mx-auto mb-3 opacity-30" />
                    <p>Context templates appear here when tools are invoked</p>
                  </div>
                  {logs.filter(l => l.type === 'server-response' && l.payload).map((log) => (
                    <Card key={`context-${log.id}`} className="mb-3">
                      <CardContent className="pt-4">
                        <div className="font-medium text-sm mb-1">Tool: {log.title}</div>
                        <div className="bg-muted p-2 rounded text-xs font-mono max-h-32 overflow-auto">
                          <pre>{JSON.stringify(log.payload, null, 2)}</pre>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                  {logs.filter(l => l.type === 'server-response' && l.payload).length === 0 && (
                    <div className="text-center text-xs text-muted-foreground mt-6">
                      Use tools to see context examples here
                    </div>
                  )}
                </ScrollArea>
              </TabsContent>
            </CardContent>
          </Tabs>
        </Card>
      </main>
    </div>
  )
}
