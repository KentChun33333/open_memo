import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Slider } from '@/components/ui/slider'
import { 
  SendHorizontal, 
  Database, 
  Cpu, 
  TextQuote, 
  FileText,
  Sparkles
} from 'lucide-react'

type MCPState = {
  prompt: string
  contextLength: number
  retrievedDocs: { title: string; snippet: string }[]
  tokensProcessed: number
  tokenSequence: string[]
}

const INITIAL_STATE: MCPState = {
  prompt: '',
  contextLength: 5,
  retrievedDocs: [
    {
      title: 'MCP Architecture Overview',
      snippet: 'The Model Context Protocol defines how context is captured, processed, and delivered to language models...'
    },
    {
      title: 'Retrieval Strategies',
      snippet: 'Effective RAG implementations use hybrid search combining semantic and lexical matching for optimal results...'
    }
  ],
  tokensProcessed: 0,
  tokenSequence: []
}

function App() {
  const [state, setState] = useState<MCPState>(INITIAL_STATE)
  const [isProcessing, setIsProcessing] = useState(false)
  const [generatedOutput, setGeneratedOutput] = useState('')

  const handleProcess = async () => {
    if (!state.prompt.trim()) {
      setGeneratedOutput('❌ Please enter a prompt to process.')
      return
    }

    setIsProcessing(true)
    setGeneratedOutput('')

    // Simulate tokenization
    const words = state.prompt.split(/\s+/)
    const tokens = words.map((word, i) => `▁${word}`) // BPE-style tokens
    setState(prev => ({ ...prev, tokensProcessed: tokens.length, tokenSequence: tokens }))

    // Simulate context retrieval visualization
    const retrievedTokens = Math.min(state.contextLength * 10, 100)
    setState(prev => ({ ...prev, tokensProcessed: tokens.length + retrievedTokens }))

    // Simulate generation with progressive text
    const progressMessages = [
      'Tokenizing input...', 
      `Retrieving ${state.contextLength} context windows...`, 
      'Processing with attention layers...',
      'Generating response...'
    ]

    for (let i = 0; i < progressMessages.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 400))
      setGeneratedOutput(prev => prev + (i === 0 ? '' : '\n') + progressMessages[i])
    }

    // Generate final response
    const response = `Based on your query: "${state.prompt}"\n\nThe Model Context Protocol successfully retrieved ${state.contextLength} context windows containing ${state.tokensProcessed} tokens total.\n\nKey insights from the context:\n1. Context window optimization improves retrieval accuracy by up to 40%\n2. Hybrid search strategies combine best of semantic and lexical matching\n3. Attention mechanisms prioritize most relevant context segments\n\nWould you like me to elaborate on any specific aspect?`

    setGeneratedOutput(prev => prev + '\n\n✅ Generation complete!\n\n' + response)
    setIsProcessing(false)
  }

  const handleContextLengthChange = (value: number[]) => {
    setState(prev => ({ ...prev, contextLength: value[0] }))
  }

  return (
    <div className="min-h-screen bg-slate-50 p-6 font-sans text-slate-900">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold tracking-tight text-slate-900">
            <Sparkles className="inline-block w-8 h-8 mr-2 align-middle text-amber-500" />
            Model Context Protocol Demo
          </h1>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            Interactive visualization of how MCP retrieves, processes, and injects context into AI models
          </p>
        </div>

        {/* Input Section */}
        <Card className="shadow-lg border-slate-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <SendHorizontal className="w-5 h-5 text-indigo-500" />
              1. Input Layer
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700">
                User Prompt
              </label>
              <Input
                placeholder="Enter your question or prompt here..."
                value={state.prompt}
                onChange={(e) => setState(prev => ({ ...prev, prompt: e.target.value }))}
                className="h-24 resize-none"
              />
            </div>
            <div className="flex items-center gap-4">
              <div className="flex-1 space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-600">Context Window Length</span>
                  <span className="font-bold text-indigo-600">{state.contextLength} windows</span>
                </div>
                <Slider
                  value={[state.contextLength]}
                  onValueChange={handleContextLengthChange}
                  min={1}
                  max={10}
                  step={1}
                  className="py-2"
                />
              </div>
              <Button 
                onClick={handleProcess} 
                disabled={isProcessing || !state.prompt}
                className="w-32 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 transition-all"
              >
                {isProcessing ? 'Processing...' : 'Process'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Context Window Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="shadow-lg border-slate-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="w-5 h-5 text-emerald-500" />
                2. Context Window
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-slate-50 rounded-lg p-4 text-sm space-y-2 border border-slate-200">
                <div className="flex justify-between items-center">
                  <span className="font-semibold text-slate-700">Retrieved Documents: {state.retrievedDocs.length}</span>
                  <span className="text-xs bg-emerald-100 text-emerald-800 px-2 py-1 rounded-full">
                    {state.contextLength * 10} tokens
                  </span>
                </div>
                <div className="space-y-2">
                  {state.retrievedDocs.map((doc, idx) => (
                    <div key={idx} className="bg-white p-3 rounded-md border border-slate-200 shadow-sm">
                      <div className="flex items-center gap-2 mb-1">
                        <TextQuote className="w-3 h-3 text-emerald-600" />
                        <span className="font-medium text-sm text-slate-800">{doc.title}</span>
                      </div>
                      <p className="text-xs text-slate-600 italic">"{doc.snippet}"</p>
                    </div>
                  ))}
                </div>
              </div>
              <div className="bg-slate-50 rounded-lg p-4 text-sm space-y-2 border border-slate-200">
                <div className="font-semibold text-slate-700 mb-2">Token Sequence (preview):</div>
                <div className="flex flex-wrap gap-1">
                  {state.tokenSequence.slice(0, 15).map((token, idx) => (
                    <span 
                      key={idx} 
                      className="bg-indigo-50 text-indigo-700 px-2 py-1 rounded text-xs font-mono"
                    >
                      {token}
                    </span>
                  ))}
                  {state.tokenSequence.length > 15 && (
                    <span className="text-slate-500 text-xs py-1">+{state.tokenSequence.length - 15} more...</span>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Processing Visualization */}
          <Card className="shadow-lg border-slate-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Cpu className="w-5 h-5 text-purple-500" />
                3. Model Processing
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Processing Stages */}
              <div className="space-y-3">
                {[
                  { label: 'Tokenization', completed: state.tokenSequence.length > 0 },
                  { label: 'Context Injection', completed: state.tokensProcessed > 0 },
                  { label: 'Attention Processing', completed: isProcessing },
                  { label: 'Response Generation', completed: generatedOutput.length > 0 }
                ].map((stage, idx) => (
                  <div key={idx} className="flex items-center gap-3">
                    <div 
                      className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-colors ${
                        stage.completed 
                          ? 'bg-emerald-500 text-white' 
                          : isProcessing && idx === 2 ? 'bg-purple-500 text-white animate-pulse' 
                          : 'bg-slate-200 text-slate-500'
                      }`}
                    >
                      {stage.completed ? '✓' : idx + 1}
                    </div>
                    <span className={`text-sm font-medium ${
                      stage.completed ? 'text-emerald-700' : isProcessing && idx === 2 ? 'text-purple-700' : 'text-slate-600'
                    }`}>
                      {stage.label}
                    </span>
                  </div>
                ))}
              </div>

              {/* Token Usage Bar */}
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-600">Token Usage</span>
                  <span className="font-bold text-slate-900">{state.tokensProcessed} / 8192</span>
                </div>
                <div className="h-3 bg-slate-200 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-500"
                    style={{ width: `${Math.min((state.tokensProcessed / 8192) * 100, 100)}%` }}
                  />
                </div>
              </div>

              {/* Processing Log */}
              {isProcessing && (
                <div className="bg-slate-900 rounded-lg p-4 font-mono text-xs text-slate-300 h-32 overflow-y-auto">
                  {generatedOutput ? (
                    generatedOutput.split('\n').map((line, i) => (
                      <div key={i} className="mb-1">{'>'} {line}</div>
                    ))
                  ) : (
                    <div>Start processing to see logs...</div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Output Section */}
        <Card className="shadow-lg border-slate-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <SendHorizontal className="w-5 h-5 text-amber-500 rotate-180" />
              4. Output Generation
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-white border border-slate-200 rounded-lg p-6 min-h-[200px] shadow-inner relative">
              {isProcessing && (
                <div className="absolute inset-0 bg-slate-50/50 z-10 flex items-center justify-center">
                  <div className="flex items-center gap-3 bg-white px-6 py-3 rounded-full shadow-lg">
                    <div className="w-5 h-5 border-3 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
                    <span className="text-slate-700 font-medium">Generating response...</span>
                  </div>
                </div>
              )}
              
              <div className="space-y-4">
                <div className="flex items-center gap-3 mb-2">
                  <Sparkles className="w-5 h-5 text-amber-500" />
                  <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wide">
                    AI Response
                  </h3>
                </div>
                
                <div className="prose prose-slate max-w-none">
                  <p className="text-slate-700 whitespace-pre-wrap leading-relaxed">
                    {generatedOutput || (
                      <span className="text-slate-400 italic">
                        Click "Process" to generate a response with context from the Model Context Protocol...
                      </span>
                    )}
                  </p>
                </div>
              </div>

              {/* Response Metadata */}
              {generatedOutput.length > 0 && (
                <div className="flex flex-wrap gap-3 mt-4 pt-4 border-t border-slate-100 text-xs text-slate-500">
                  <div className="flex items-center gap-1">
                    <FileText className="w-3 h-3" />
                    <span>{generatedOutput.split(/\s+/).length} words</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Cpu className="w-3 h-3" />
                    <span>{state.tokensProcessed + 150} total tokens</span>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default App
