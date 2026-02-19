import { useState } from 'react'
import { 
  Cpu, 
  Database, 
  GitBranch, 
  Zap, 
  Globe, 
  Settings, 
  Code, 
  Terminal,
  CheckCircle,
  ArrowRight,
  Box
} from 'lucide-react'
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle, 
  CardDescription 
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

// Simulated MCP components
interface MCPTool {
  id: string
  name: string
  description: string
  type: 'data' | 'action' | 'integration'
  connected: boolean
}

interface MCPModel {
  id: string
  name: string
  provider: string
  capabilities: string[]
  active: boolean
}

function MCPExample() {
  const [connectedTools, setConnectedTools] = useState<MCPTool[]>([
    { id: '1', name: 'File System Reader', description: 'Read files and directories', type: 'data', connected: true },
    { id: '2', name: 'Web Search', description: 'Search the web for information', type: 'data', connected: true },
    { id: '3', name: 'Database Query', description: 'Execute database queries', type: 'data', connected: false },
    { id: '4', name: 'Git Operations', description: 'Execute git commands', type: 'action', connected: false },
    { id: '5', name: 'API Caller', description: 'Make HTTP requests', type: 'integration', connected: false },
  ])

  const [models, setModels] = useState<MCPModel[]>([
    { id: '1', name: 'Claude 3.5 Sonnet', provider: 'Anthropic', capabilities: ['reasoning', 'coding', 'analysis'], active: true },
    { id: '2', name: 'GPT-4 Turbo', provider: 'OpenAI', capabilities: ['coding', 'writing', 'translation'], active: false },
    { id: '3', name: 'Llama 3', provider: 'Meta', capabilities: ['reasoning', 'coding', 'chat'], active: false },
  ])

  const toggleToolConnection = (toolId: string) => {
    setConnectedTools(prev => prev.map(tool => 
      tool.id === toolId ? { ...tool, connected: !tool.connected } : tool
    ))
  }

  const setActiveModel = (modelId: string) => {
    setModels(prev => prev.map(model => 
      model.id === modelId ? { ...model, active: true } : { ...model, active: false }
    ))
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-50">
      {/* Header */}
      <div className="border-b bg-white dark:bg-slate-900 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2 rounded-lg">
              <Box className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold">Model Context Protocol</h1>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Connect AI models with tools and data sources
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="border-green-500 text-green-600 dark:text-green-400">
              <CheckCircle className="mr-2 h-3 w-3" />
              System Ready
            </Badge>
          </div>
        </div>
      </div>

      <div className="container mx-auto max-w-6xl p-6 space-y-6">
        {/* Introduction */}
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Globe className="h-5 w-5" />
                What is MCP?
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Model Context Protocol (MCP) is an open standard for connecting AI models 
                with external tools and data sources. It enables AI assistants to interact 
                with your data, services, and tools in a secure and standardized way.
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Zap className="h-5 w-5" />
                Key Features
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {[
                  'Standardized interface for AI-tool communication',
                  'Secure connection management',
                  'Tool discovery and registration',
                  'Context-aware data handling'
                ].map((feature, idx) => (
                  <div key={idx} className="flex items-start gap-2">
                    <ArrowRight className="h-4 w-4 mt-1 text-blue-500" />
                    <span className="text-sm">{feature}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Interactive Section */}
        <Tabs defaultValue="tools" className="space-y-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="tools">
              <GitBranch className="mr-2 h-4 w-4" />
              Tools & Data
            </TabsTrigger>
            <TabsTrigger value="models">
              <Cpu className="mr-2 h-4 w-4" />
              AI Models
            </TabsTrigger>
            <TabsTrigger value="context">
              <Database className="mr-2 h-4 w-4" />
              Context
            </TabsTrigger>
          </TabsList>

          {/* Tools Tab */}
          <TabsContent value="tools" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {connectedTools.map((tool) => (
                <Card key={tool.id} className="transition-all hover:shadow-md">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <CardTitle className="flex items-center gap-2">
                        {tool.type === 'data' && <Database className="h-5 w-5 text-blue-500" />}
                        {tool.type === 'action' && <Settings className="h-5 w-5 text-purple-500" />}
                        {tool.type === 'integration' && <GitBranch className="h-5 w-5 text-green-500" />}
                        {tool.name}
                      </CardTitle>
                      <Badge variant={tool.connected ? "default" : "secondary"}>
                        {tool.connected ? "Connected" : "Disconnected"}
                      </Badge>
                    </div>
                    <CardDescription>{tool.description}</CardDescription>
                  </CardHeader>
                    <CardContent>
                    <Button 
                      variant={tool.connected ? "outline" : "default"}
                      size="sm"
                      className="w-full"
                      onClick={() => toggleToolConnection(tool.id)}
                    >
                      {tool.connected ? "Disconnect" : "Connect"}
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>

            <Alert className="border-l-4 border-l-blue-500">
              <Zap className="h-5 w-5" />
              <AlertTitle>How Tools Work</AlertTitle>
              <AlertDescription className="mt-2">
                MCP tools are functions that AI models can call. Each tool has:
                <ul className="list-disc ml-5 mt-2 space-y-1">
                  <li>A unique identifier and name</li>
                  <li>Description of what it does</li>
                  <li>Input parameters and output format</li>
                  <li>Authentication and security settings</li>
                </ul>
              </AlertDescription>
            </Alert>
          </TabsContent>

          {/* Models Tab */}
          <TabsContent value="models" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {models.map((model) => (
                <Card key={model.id} className={`transition-all hover:shadow-md ${model.active ? 'ring-2 ring-blue-500' : ''}`}>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <CardTitle>{model.name}</CardTitle>
                      <Badge variant="secondary">{model.provider}</Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 mb-4">
                      <p className="text-sm font-medium">Capabilities:</p>
                      <div className="flex flex-wrap gap-1">
                        {model.capabilities.map(cap => (
                          <Badge key={cap} variant="outline" className="text-xs">
                            {cap}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <Button 
                      variant={model.active ? "default" : "outline"}
                      className="w-full"
                      onClick={() => setActiveModel(model.id)}
                    >
                      {model.active ? "Active Model" : "Set as Active"}
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>

            <Alert className="border-l-4 border-l-purple-500">
              <Cpu className="h-5 w-5" />
              <AlertTitle>About AI Models</AlertTitle>
              <AlertDescription className="mt-2">
                MCP supports multiple AI models simultaneously. Each model can access the same 
                toolset but may interpret and process information differently based on its 
                training and capabilities.
              </AlertDescription>
            </Alert>
          </TabsContent>

          {/* Context Tab */}
          <TabsContent value="context" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="h-5 w-5" />
                  Current Context State
                </CardTitle>
                <CardDescription>
                  Context is automatically accumulated as the AI interacts with tools
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-900 rounded-lg">
            <span className="text-sm font-medium">Active Model</span>
            <span className="text-sm text-slate-600 dark:text-slate-400">
              {models.find(m => m.active)?.name || "None selected"}
            </span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-900 rounded-lg">
            <span className="text-sm font-medium">Connected Tools</span>
            <span className="text-sm text-slate-600 dark:text-slate-400">
              {connectedTools.filter(t => t.connected).length} / {connectedTools.length}
            </span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-900 rounded-lg">
            <span className="text-sm font-medium">Total Tokens Used</span>
            <span className="text-sm text-slate-600 dark:text-slate-400">1,248</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-900 rounded-lg">
            <span className="text-sm font-medium">Session Duration</span>
            <span className="text-sm text-slate-600 dark:text-slate-400">12 min</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Alert className="border-l-4 border-l-green-500">
              <Database className="h-5 w-5" />
              <AlertTitle>Context Management</AlertTitle>
              <AlertDescription className="mt-2">
                MCP maintains conversation context across tool calls. This context includes:
                <ul className="list-disc ml-5 mt-2 space-y-1">
                  <li>Previous tool calls and results</li>
                  <li>User instructions and preferences</li>
                  <li>Session state and variables</li>
                  <li>Memory references and embeddings</li>
                </ul>
              </AlertDescription>
            </Alert>
          </TabsContent>
        </Tabs>

        {/* Code Example */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Code className="h-5 w-5" />
              MCP in Action
            </CardTitle>
            <CardDescription>
              Example of how MCP enables AI to use tools
            </CardDescription>
          </CardHeader>
          <CardContent>
            <pre className="bg-slate-900 text-slate-50 p-4 rounded-lg overflow-x-auto text-sm font-mono">
              <code>
                {`// MCP Tool Definition
const fileReaderTool = {
  name: "read_file",
  description: "Read the contents of a file",
  parameters: {
    type: "object",
    properties: {
      path: {
        type: "string",
        description: "The path to the file"
      }
    },
    required: ["path"]
  }
};

// AI Model calls the tool
{
  "tool_name": "read_file",
  "tool_arguments": {
    "path": "./src/App.tsx"
  }
}

// Tool returns result
{
  "tool_result": "import { useState } from 'react'...",
  "is_error": false
}`}
              </code>
            </pre>
          </CardContent>
        </Card>

        {/* Documentation Links */}
        <div className="grid gap-4 md:grid-cols-2">
          <Card className="cursor-pointer transition-all hover:shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <GitBranch className="h-5 w-5" />
                MCP Specification
              </CardTitle>
              <CardDescription>Read the official MCP standard</CardDescription>
            </CardHeader>
          </Card>
          <Card className="cursor-pointer transition-all hover:shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Terminal className="h-5 w-5" />
                CLI Integration
              </CardTitle>
              <CardDescription>Use MCP with command-line tools</CardDescription>
            </CardHeader>
          </Card>
        </div>
      </div>

      {/* Footer */}
      <div className="border-t bg-white dark:bg-slate-900 py-6 mt-8">
        <div className="container mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-sm text-slate-500">
            © 2024 Model Context Protocol Demo
          </p>
          <div className="flex items-center gap-4">
            <a href="#" className="text-sm text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-50">
              Documentation
            </a>
            <a href="#" className="text-sm text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-50">
              GitHub
            </a>
            <a href="#" className="text-sm text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-50">
              Examples
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}

export default MCPExample
