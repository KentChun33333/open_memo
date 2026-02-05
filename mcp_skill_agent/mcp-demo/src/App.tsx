import { BrainCircuit, Database, Server, Layout, Zap, Menu, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-md sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BrainCircuit className="h-8 w-8 text-indigo-600" />
            <h1 className="text-xl font-bold text-slate-900">Model Context Protocol</h1>
          </div>
          <div className="flex items-center gap-4">
            <Button variant="outline" size="sm">Documentation</Button>
            <Button size="sm">Get Started</Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 text-center">
        <Badge className="mb-6 bg-indigo-100 text-indigo-700 hover:bg-indigo-200">
          Open Standard for AI Context
        </Badge>
        <h1 className="text-4xl md:text-6xl font-bold text-slate-900 mb-6">
          Connect Your AI Models to Real-World Data
        </h1>
        <p className="text-xl text-slate-600 max-w-2xl mx-auto mb-8">
          The Model Context Protocol (MCP) enables seamless integration between AI models and your data sources, tools, and systems.
        </p>
        <div className="flex flex-wrap justify-center gap-4">
          <Button size="lg" className="bg-indigo-600 hover:bg-indigo-700">
            <Zap className="mr-2 h-5 w-5" />
            Start Building
          </Button>
          <Button size="lg" variant="outline">
            <Database className="mr-2 h-5 w-5" />
            Explore Servers
          </Button>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">Key Features</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <Card>
            <CardHeader>
              <BrainCircuit className="h-10 w-10 text-indigo-500 mb-4" />
              <CardTitle>Context Enrichment</CardTitle>
              <CardDescription>Provide rich context to your AI models with real-time data integration</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-slate-600">Access databases, APIs, and files directly from your AI prompts.</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Server className="h-10 w-10 text-indigo-500 mb-4" />
              <CardTitle>Server Ecosystem</CardTitle>
              <CardDescription>Connect with a growing ecosystem of MCP-compatible servers</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-slate-600">Pre-built connectors for popular services and custom integrations.</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Layout className="h-10 w-10 text-indigo-500 mb-4" />
              <CardTitle>Unified Interface</CardTitle>
              <CardDescription>Consistent protocol across all AI applications</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-slate-600">Standardized communication format for predictable integration.</p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Quick Example Tabs */}
      <section className="container mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
        <Tabs defaultValue="example" className="max-w-2xl mx-auto">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="example">Example</TabsTrigger>
            <TabsTrigger value="protocol">Protocol</TabsTrigger>
            <TabsTrigger value="integration">Integration</TabsTrigger>
          </TabsList>
          <TabsContent value="example" className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle>Hello World Example</CardTitle>
                <CardDescription>A simple MCP connection example</CardDescription>
              </CardHeader>
              <CardContent className="bg-slate-900 text-slate-50 p-4 rounded-lg font-mono text-sm">
                <div className="mb-2">
                  <span className="text-purple-400">import</span> {{'{'}} MCPClient {'}}{' '}
                  <span className="text-purple-400">from</span> <span className="text-green-400">'@modelcontextprotocol/sdk'</span>;
                </div>
                <div>
                  <span className="text-blue-400">const</span> client = <span className="text-purple-400">new</span> MCPClient(
                    <span className="text-green-400">'https://api.example.com/mcp'</span>
                  );
                  {'\n'}
                  <span className="text-blue-400">await</span> client.initialize();
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="protocol" className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle>MCP Protocol Flow</CardTitle>
                <CardDescription>How data flows between models and sources</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center">1</div>
                    <span className="text-slate-700">AI model sends context request</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center">2</div>
                    <span className="text-slate-700">MCP server fetches relevant data</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center">3</div>
                    <span className="text-slate-700">Data is formatted and sent back</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center">4</div>
                    <span className="text-slate-700">Model uses context to respond</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="integration" className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle>Getting Started</CardTitle>
                <CardDescription>Three simple steps to integrate MCP</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-3">
                  <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center font-bold text-slate-700 shrink-0">1</div>
                  <div>
                    <h4 className="font-medium text-slate-900">Install SDK</h4>
                    <p className="text-sm text-slate-600">npm install @modelcontextprotocol/sdk</p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center font-bold text-slate-700 shrink-0">2</div>
                  <div>
                    <h4 className="font-medium text-slate-900">Configure Server</h4>
                    <p className="text-sm text-slate-600">Set up your data sources in server.json</p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center font-bold text-slate-700 shrink-0">3</div>
                  <div>
                    <h4 className="font-medium text-slate-900">Connect Client</h4>
                    <p className="text-sm text-slate-600">Initialize client and start requesting context</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="bg-indigo-600 rounded-2xl p-8 md:p-12 text-center text-white">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to Build with Model Context Protocol?
          </h2>
          <p className="text-xl mb-8 opacity-90 max-w-2xl mx-auto">
            Join thousands of developers delivering context-aware AI experiences with MCP.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button className="bg-white text-indigo-600 hover:bg-slate-100 font-semibold py-4 px-8">
              Get Started Now
            </Button>
            <Button className="bg-transparent border-2 border-white text-white hover:bg-white/10 font-semibold py-4 px-8">
              View Documentation
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-slate-300 py-12">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <BrainCircuit className="h-6 w-6 text-indigo-500" />
                <h3 className="text-lg font-semibold text-white">Model Context Protocol</h3>
              </div>
              <p className="text-sm text-slate-400">Open standard for AI context integration.</p>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-4">Resources</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-indigo-400">Documentation</a></li>
                <li><a href="#" className="hover:text-indigo-400">API Reference</a></li>
                <li><a href="#" className="hover:text-indigo-400">Example Servers</a></li>
                <li><a href="#" className="hover:text-indigo-400">Community</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-4">Protocol</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-indigo-400">Overview</a></li>
                <li><a href="#" className="hover:text-indigo-400">Specification</a></li>
                <li><a href="#" className="hover:text-indigo-400">Servers</a></li>
                <li><a href="#" className="hover:text-indigo-400">Clients</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-4">Connect</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-indigo-400">GitHub</a></li>
                <li><a href="#" className="hover:text-indigo-400">Discord</a></li>
                <li><a href="#" className="hover:text-indigo-400">Twitter</a></li>
                <li><a href="#" className="hover:text-indigo-400">Email</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-800 mt-8 pt-8 text-center text-sm text-slate-500">
            <p> © 2025 Model Context Protocol. Open source under the MIT License.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
