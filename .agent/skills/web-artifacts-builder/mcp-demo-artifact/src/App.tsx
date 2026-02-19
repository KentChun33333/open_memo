import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  Database, 
  FileJson, 
  GitBranch, 
  Activity, 
  ArrowRightLeft, 
  Code,
  ChevronRight
} from 'lucide-react'

// Helper to format JSON with syntax highlighting (basic colorization)
const JsonDisplay = ({ data, label }: { data: any; label?: string }) => {
  const jsonString = JSON.stringify(data, null, 2)
  // Simple syntax highlighting using basic color classes
  const highlighted = jsonString.split('\n').map((line, i) => {
    let content = line
    if (line.includes('"')) {
      // Highlight keys
      content = content.replace(/(".*?":)/g, '<span class="text-amber-300">$1</span>')
      // Highlight strings
      content = content.replace(/(".*?")/, '<span class="text-green-400">$1</span>')
    }
    return `<div class="whitespace-pre text-sm font-mono text-slate-300 ml-4">${content}</div>`
  })

  return (
    <div className="bg-slate-900 rounded-md p-4 overflow-x-auto my-4">
      {label && <h4 className="text-sm font-semibold text-slate-400 mb-2">{label}</h4>}
      <div dangerouslySetInnerHTML={{ __html: highlighted.join('\n') }} />
    </div>
  )
}

// Inline SVGs instead of external image assets
const ContextSchemaIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" className="w-6 h-6 text-blue-400" stroke="currentColor" strokeWidth="2">
    <rect x="2" y="4" width="20" height="16" rx="2" className="fill-blue-900/20" />
    <path d="M2 9h20" />
    <path d="M7 4v16" />
    <circle cx="17" cy="9" r="2" className="fill-blue-500" />
    <circle cx="17" cy="15" r="2" className="fill-blue-500" />
  </svg>
)

const LatencyIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" className="w-6 h-6 text-emerald-400" stroke="currentColor" strokeWidth="2">
    <path d="M12 2v4" />
    <path d="M12 18v4" />
    <path d="M4.93 4.93l2.83 2.83" />
    <path d="M16.24 16.24l2.83 2.83" />
    <path d="M2 12h4" />
    <path d="M18 12h4" />
    <path d="M4.93 19.07l2.83-2.83" />
    <path d="M16.24 7.76l2.83-2.83" />
    <circle cx="12" cy="12" r="5" />
  </svg>
)

function App() {
  // State for simulation
  const [latency, setLatency] = useState<number | null>(null)
  const [isSimulating, setIsSimulating] = useState(false)

  // Sample MCP Context Structure
  const mcpContext = {
    contextType: "markdown",
    version: "1.0",
    text: "# Sample Context\n\nThis paragraph represents the **serialized context** \
           sent to the model. It includes relevant document snippets, user instructions, \
           and any necessary metadata.",
    metadata: {
      source: "README.md",
      offset: 0,
      length: 256
    }
  }

  // Sample Schema Negotiation (Client → Server)
  const clientSchema = {
    requests: [
      "context/mentions",
      "text/diff",
      "tool/list"
    ],
    notifications: [
      "text/didChange"
    ]
  }

  const serverSchema = {
    requests: [
      "tools/call"
    ],
    notifications: [
      "progress"
    ]
  }

  // Round-trip timeline timeline mockup
  const roundTripData = {
    timestamp: new Date().toISOString(),
    latencySamples: [120, 95, 110, 88, 130, 102, 97]
  }

  // Simulate round-trip latency
  const simulateLatency = async () => {
    setLatency(null)
    setIsSimulating(true)

    // Simulate client → server
    await new Promise(r => setTimeout(r, 300))

    // Simulate server processing
    await new Promise(r => setTimeout(r, 200))

    // Simulate server → client
    await new Promise(r => setTimeout(r, 350))

    const totalLatency = 300 + 200 + 350
    setLatency(totalLatency)
    setIsSimulating(false)
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6">
      <div className="max-w-6xl mx-auto space-y-8">
        <header className="text-center space-y-4">
          <h1 className="text-4xl font-bold tracking-tight bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
            Model Context Protocol (MCP) Demo
          </h1>
          <p className="text-lg text-slate-400 max-w-2xl mx-auto">
            Interactive exploration of MCP’s core components: context serialization, schema negotiation, and round-trip latency measurement.
          </p>
        </header>

        <Tabs defaultValue="serialization" className="w-full">
          <TabsList className="grid w-full grid-cols-3 bg-slate-900">
            <TabsTrigger value="serialization" className="data-[state=active]:bg-blue-600">
              <Database className="w-4 h-4 mr-2" />
              Context Serialization
            </TabsTrigger>
            <TabsTrigger value="schema" className="data-[state=active]:bg-blue-600">
              <GitBranch className="w-4 h-4 mr-2" />
              Schema Negotiation
            </TabsTrigger>
            <TabsTrigger value="latency" className="data-[state=active]:bg-blue-600">
              <Activity className="w-4 h-4 mr-2" />
              Latency Simulation
            </TabsTrigger>
          </TabsList>

          {/* Context Serialization Tab */}
          <TabsContent value="serialization" className="space-y-6">
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-xl">
                  <ContextSchemaIcon />
                  Context Serialization Overview
                </CardTitle>
                <CardDescription>
                  Contexts are structured data payloads that encode relevant information for the model.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-3">
                    <h4 className="font-semibold text-slate-300">Key Concepts</h4>
                    <ul className="space-y-2 text-sm text-slate-400">
                      <li className="flex items-start gap-2">
                        <ChevronRight className="w-4 h-4 mt-0.5 text-emerald-400" />
                        <span><strong>Serialization:</strong> Converts structured data into plain text/JSON</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <ChevronRight className="w-4 h-4 mt-0.5 text-emerald-400" />
                        <span><strong>Context Window Management:</strong> Efficiently fits context into LLM limits</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <ChevronRight className="w-4 h-4 mt-0.5 text-emerald-400" />
                        <span><strong>Metadata:</strong> Tracks source, offsets, and versioning</span>
                      </li>
                    </ul>
                  </div>
                  <div className="space-y-3">
                    <h4 className="font-semibold text-slate-300">Sample Context Payload</h4>
                    <JsonDisplay data={mcpContext} label="Serialized Context" />
                    <p className="text-sm text-slate-500">
                      This JSON structure would be serialized to text and injected into the model's context window.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Schema Negotiation Tab */}
          <TabsContent value="schema" className="space-y-6">
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-xl">
                  <GitBranch className="w-6 h-6 text-blue-400" />
                  Schema Negotiation
                </CardTitle>
                <CardDescription>
                  Client and server exchange supported capabilities before communication begins.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex flex-col md:flex-row items-center gap-6">
                  <div className="flex-1 space-y-3">
                    <h4 className="font-semibold text-slate-300 flex items-center gap-2">
                      <FileJson className="w-5 h-5 text-purple-400" />
                      Client → Server (Client Capabilities)
                    </h4>
                    <JsonDisplay data={clientSchema} />
                    <p className="text-sm text-slate-500">
                      The client declares supported requests and notifications (e.g., mentions, diff updates).
                    </p>
                  </div>
                  <ArrowRightLeft className="w-6 h-6 text-emerald-400" />
                  <div className="flex-1 space-y-3">
                    <h4 className="font-semibold text-slate-300 flex items-center gap-2">
                      <FileJson className="w-5 h-5 text-amber-400" />
                      Server → Client (Server Capabilities)
                    </h4>
                    <JsonDisplay data={serverSchema} />
                    <p className="text-sm text-slate-500">
                      The server responds with its supported operations (e.g., tool calls, progress updates).
                    </p>
                  </div>
                </div>

                <div className="bg-slate-950 rounded-lg p-4 border border-slate-800">
                  <h5 className="font-semibold text-slate-300 mb-2">Negotiation Flow</h5>
                  <ol className="space-y-2 text-sm text-slate-400 list-decimal pl-6">
                    <li>Client initiates connection with its schema</li>
                    <li>Server receives and validates schema compatibility</li>
                    <li>Server responds with its schema</li>
                    <li>Both parties establish shared protocol contract</li>
                  </ol>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Latency Simulation Tab */}
          <TabsContent value="latency" className="space-y-6">
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-xl">
                  <LatencyIcon />
                  Round-Trip Latency Measurement
                </CardTitle>
                <CardDescription>
                  Simulate the complete request/response cycle: client → server → client.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center gap-4">
                  <Button 
                    onClick={simulateLatency}
                    disabled={isSimulating}
                    className={isSimulating ? "opacity-75 cursor-wait" : ""}
                  >
                    {isSimulating ? (
                      <>
                        <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                        Simulating...
                      </>
                    ) : (
                      <>
                        <Activity className="w-4 h-4 mr-2" />
                        Simulate Round-Trip
                      </>
                    )}
                  </Button>
                  
                  {latency !== null && (
                    <div className="ml-auto">
                      <span className="text-lg font-bold text-emerald-400">{latency} ms</span>
                    </div>
                  )}
                </div>

                {latency !== null && (
                  <div className="space-y-3">
                    <h4 className="font-semibold text-slate-300">Timeline Breakdown</h4>
                    <div className="space-y-2">
                      {[
                        { step: "Client initiates request", time: 0, duration: 300, color: "bg-blue-500" },
                        { step: "Server processes request", time: 300, duration: 200, color: "bg-purple-500" },
                        { step: "Server responds to client", time: 500, duration: 350, color: "bg-emerald-500" }
                      ].map((segment, i) => (
                        <div key={i} className="space-y-1">
                          <div className="flex justify-between text-sm text-slate-400">
                            <span>{segment.step}</span>
                            <span>{segment.time}–{segment.time + segment.duration}ms</span>
                          </div>
                          <div className="h-3 bg-slate-800 rounded-full overflow-hidden">
                            <div 
                              className={`h-full ${segment.color}`}
                              style={{ width: `${(segment.duration / 1000) * 100}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>

                    <div className="mt-4 bg-slate-950 rounded-lg p-4 border border-slate-800">
                      <h5 className="font-semibold text-slate-300 mb-2">Sample Latency History</h5>
                      <div className="flex items-end gap-1 h-16 bg-slate-900/50 rounded p-2">
                        {roundTripData.latencySamples.map((val, i) => (
                          <div key={i} className="flex-1 flex flex-col items-center gap-1">
                            <div 
                              className={`w-full rounded-t-sm ${val < 100 ? "bg-emerald-500" : "bg-yellow-500"}`}
                              style={{ height: `${(val / 150) * 100}%` }}
                            />
                            <span className="text-xs text-slate-500">{val}ms</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="text-lg">Latency Optimization Tips</CardTitle>
              </CardHeader>
              <CardContent className="grid md:grid-cols-3 gap-4 text-sm text-slate-400">
                <div className="p-3 bg-slate-950 rounded-lg">
                  <h5 className="font-semibold text-slate-300 mb-2">1. Preload Context</h5>
                  <p>Fetch and serialize context before sending to avoid blocking.</p>
                </div>
                <div className="p-3 bg-slate-950 rounded-lg">
                  <h5 className="font-semibold text-slate-300 mb-2">2. Compress Payloads</h5>
                  <p>Use gzip for larger text payloads where supported.</p>
                </div>
                <div className="p-3 bg-slate-950 rounded-lg">
                  <h5 className="font-semibold text-slate-300 mb-2">3. Parallel Requests</h5>
                  <p>Concurrent schema negotiation and context fetches.</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Footer */}
        <div className="text-center text-slate-500 text-sm mt-12">
          <p>MCP Demo Artifact • Built with React + Tailwind CSS + shadcn/ui</p>
        </div>
      </div>
    </div>
  )
}

export default App
