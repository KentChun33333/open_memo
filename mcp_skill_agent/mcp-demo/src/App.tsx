import { useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Terminal, Database, Cpu, Activity, ArrowRight, Layers, MessageSquare } from 'lucide-react'

// Mock MCP response types
type ContextData = {
  source: string;
  content: string;
  relevance: number;
}

function App() {
  const [userInput, setUserInput] = useState('')
  const [contextHistory, setContextHistory] = useState<ContextData[]>([])
  const [activeTab, setActiveTab] = useState('build')
  const [isProcessing, setIsProcessing] = useState(false)

  const handleAddContext = () => {
    if (!userInput.trim()) return
    
    setIsProcessing(true)
    
    // Simulate MCP processing
    setTimeout(() => {
      const newContext: ContextData = {
        source: 'user-input',
        content: userInput,
        relevance: Math.floor(Math.random() * 30) + 70
      }
      setContextHistory([...contextHistory, newContext])
      setUserInput('')
      setIsProcessing(false)
    }, 1500)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">Model Context Protocol</h1>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            Interactive demonstration of how models understand and process context through structured data flow
          </p>
        </div>

        {/* Main Demo Area */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Left Column: Context Builder */}
          <Card className="border-slate-200 shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <div className="p-2 bg-indigo-100 rounded-lg">
                  <Activity className="w-6 h-6 text-indigo-600" />
                </div>
                <span>Context Builder</span>
              </CardTitle>
              <CardDescription>
                Enter your input to simulate how context is processed through the model
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="context-input">Enter context or query</Label>
                  <div className="flex gap-2 mt-1">
                    <Input
                      id="context-input"
                      placeholder="e.g., analyze the performance of our recent campaign..."
                      value={userInput}
                      onChange={(e) => setUserInput(e.target.value)}
                      className="flex-1"
                    />
                    <Button 
                      onClick={handleAddContext}
                      disabled={!userInput.trim() || isProcessing}
                      className={isProcessing ? "animate-pulse" : ""}
                    >
                      {isProcessing ? "Processing..." : "Add Context"}
                    </Button>
                  </div>
                </div>

                {/* Context Visualization */}
                <div className="mt-6">
                  <h3 className="text-sm font-medium mb-3">Context Layers</h3>
                  <div className="space-y-3">
                    <div className="flex items-center gap-3 text-sm">
                      <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center">
                        <Layers className="w-4 h-4 text-slate-500" />
                      </div>
                      <div>
                        <div className="font-medium">Input Processing</div>
                        <div className="text-xs text-slate-500">Tokenization and encoding</div>
                      </div>
                    </div>
                    
                    {contextHistory.length > 0 && (
                      <>
                        <div className="flex items-center gap-3 text-sm">
                          <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center">
                            <Database className="w-4 h-4 text-slate-500" />
                          </div>
                          <div>
                            <div className="font-medium">Context Storage</div>
                            <div className="text-xs text-slate-500">Retrieval augmented generation</div>
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-3 text-sm">
                          <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center">
                            <Cpu className="w-4 h-4 text-slate-500" />
                          </div>
                          <div>
                            <div className="font-medium">Model Processing</div>
                            <div className="text-xs text-slate-500">Attention mechanisms active</div>
                          </div>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Right Column: Context Visualizer */}
          <Card className="border-slate-200 shadow-lg h-full">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <div className="p-2 bg-emerald-100 rounded-lg">
                  <Terminal className="w-6 h-6 text-emerald-600" />
                </div>
                <span>Context Flow Visualizer</span>
              </CardTitle>
              <CardDescription>
                Real-time visualization of context processing through the protocol layers
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="bg-slate-900 rounded-lg p-4 font-mono text-sm h-[400px] overflow-auto">
                {contextHistory.length === 0 ? (
                  <div className="text-slate-400 flex flex-col items-center justify-center h-full">
                    <MessageSquare className="w-12 h-12 mb-2 opacity-50" />
                    <p>Enter context to begin processing</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="text-emerald-400">[MCP] Initializing context pipeline...</div>
                    <div className="text-emerald-400">[MCP] Received user input: "{contextHistory[0]?.content.substring(0, 50)}..."</div>
                    
                    {contextHistory.map((context, idx) => (
                      <div key={idx} className="mt-4 border-l-2 border-indigo-500 pl-2">
                        <div className="text-slate-300">Context #{idx + 1}:</div>
                        <div className="text-indigo-300 mt-1">
                          <span className="font-bold">Source:</span> {context.source}
                        </div>
                        <div className="text-indigo-300">
                          <span className="font-bold">Content:</span> {context.content}
                        </div>
                        <div className="flex items-center gap-2 mt-2">
                          <span className="text-slate-400 font-bold">Relevance Score:</span>
                          <Badge variant="secondary" className="bg-slate-800 text-emerald-400">
                            {context.relevance}%
                          </Badge>
                        </div>
                        <div className="text-sm text-emerald-400 mt-2">
                          [MCP] Context embedded in vector space
                        </div>
                      </div>
                    ))}
                    
                    <div className="animate-pulse mt-2 text-emerald-400">[MCP] Generating response...</div>
                  </div>
                )}
              </div>
              
              <div className="mt-4 pt-4 border-t border-slate-100">
                <h3 className="text-sm font-medium mb-2">Protocol Flow</h3>
                <div className="flex justify-between items-center text-xs text-slate-500">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-slate-300 rounded-full"></div>
                    Input
                  </div>
                  <ArrowRight className="w-3 h-3" />
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-indigo-300 rounded-full"></div>
                    Processing
                  </div>
                  <ArrowRight className="w-3 h-3" />
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-emerald-300 rounded-full"></div>
                    Output
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Detailed Protocol Info */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">How the Model Context Protocol Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader>
                <div className="p-2 bg-blue-100 rounded-lg w-fit mb-2">
                  <Layers className="w-5 h-5 text-blue-600" />
                </div>
                <CardTitle className="text-lg">Context Layers</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-600">
                  MCP uses layered context processing with semantic memory, working memory, and procedural memory
                  to understand and maintain conversation context across interactions.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="p-2 bg-purple-100 rounded-lg w-fit mb-2">
                  <Database className="w-5 h-5 text-purple-600" />
                </div>
                <CardTitle className="text-lg">Retrieval Augmentation</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-600">
                  Relevant external context is retrieved and injected into the model's context window,
                  enhancing responses with up-to-date information and domain-specific knowledge.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="p-2 bg-amber-100 rounded-lg w-fit mb-2">
                  <Cpu className="w-5 h-5 text-amber-600" />
                </div>
                <CardTitle className="text-lg">Attention Mechanisms</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-600">
                  The model's attention mechanisms weigh different parts of the context differently,
                  focusing on the most relevant information for generation while maintaining coherence.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Interactive Accordion */}
        <Card>
          <CardHeader>
            <CardTitle>Technical Details</CardTitle>
            <CardDescription>Explore the implementation details of the Model Context Protocol</CardDescription>
          </CardHeader>
          <CardContent>
            <Accordion type="multiple" className="w-full">
              <AccordionItem value="item-1">
                <AccordionTrigger className="font-medium">Context Window Management</AccordionTrigger>
                <AccordionContent className="text-sm text-slate-600">
                  MCP implements sophisticated context window management, including sliding windows, 
                  summary compression, and selective retention to maximize effective context length.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="item-2">
                <AccordionTrigger className="font-medium">Context Embedding</AccordionTrigger>
                <AccordionContent className="text-sm text-slate-600">
                  All context is embedded into vector spaces for semantic retrieval and comparison, 
                  allowing the model to understand relationships between different pieces of information.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="item-3">
                <AccordionTrigger className="font-medium">State Persistence</AccordionTrigger>
                <AccordionContent className="text-sm text-slate-600">
                  Conversation state is persisted between interactions, allowing for long-term 
                  context retention and multi-turn dialogues that build understanding over time.
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default App
