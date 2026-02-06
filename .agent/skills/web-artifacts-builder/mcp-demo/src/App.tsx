import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { ScrollArea } from "@/components/ui/scroll-area"
import { 
  Database, 
  Send, 
  Brain, 
  FileText, 
  Settings, 
  Trash2,
  Plus
} from 'lucide-react'

type Message = {
  id: string
  role: 'user' | 'model' | 'context'
  content: string
  timestamp: Date
}

function MCPApp() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'context',
      content: 'System context initialized with user preferences and document context.',
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState('')
  const [documents, setDocuments] = useState<string[]>(['Project Requirements.md', 'API Documentation.json', 'User Manual.pdf'])
  const [activeTab, setActiveTab] = useState('chat')
  const [lastInput, setLastInput] = useState('')
  
  const handleSend = () => {
    if (!input.trim()) return
    
    const newUserMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    }
    
    setLastInput(input)
    setMessages(prev => [...prev, newUserMessage])
    setInput('')
    
    // Simulate model response
    setTimeout(() => {
      const newMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'model',
        content: `I've processed your input "${lastInput}" using the provided context. Based on ${documents.length} documents in context, I can help with this.`,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, newMessage])
    }, 1000)
  }
  
  const addDocument = () => {
    const newDoc = `New Document ${documents.length + 1}.txt`
    setDocuments(prev => [...prev, newDoc])
  }
  
  const removeDocument = (doc: string) => {
    setDocuments(prev => prev.filter(d => d !== doc))
  }

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'user': return 'bg-blue-500'
      case 'model': return 'bg-green-500'
      case 'context': return 'bg-purple-500'
      default: return 'bg-gray-500'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-white p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2">Model Context Protocol Demo</h1>
          <p className="text-gray-300 max-w-2xl mx-auto">
            Visualizing how context flows between users, models, and documents in an AI system
          </p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <div className="flex justify-center mb-6">
            <TabsList className="grid grid-cols-3 w-full max-w-md">
              <TabsTrigger value="chat" className="data-[state=active]:bg-blue-600">
                <Send className="mr-2 h-4 w-4" />
                Chat
              </TabsTrigger>
              <TabsTrigger value="context" className="data-[state=active]:bg-purple-600">
                <Brain className="mr-2 h-4 w-4" />
                Context Flow
              </TabsTrigger>
              <TabsTrigger value="documents" className="data-[state=active]:bg-indigo-600">
                <FileText className="mr-2 h-4 w-4" />
                Documents
              </TabsTrigger>
            </TabsList>
          </div>

          {/* Chat Tab */}
          <TabsContent value="chat" className="flex flex-col h-[600px]">
            <div className="flex-1 overflow-hidden">
              <ScrollArea className="h-full pr-4">
                <div className="space-y-4">
                  {messages.map((msg) => (
                    <div key={msg.id} className="flex items-start space-x-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${getRoleColor(msg.role)}`}>
                        {msg.role === 'user' && <Send className="h-4 w-4 text-white" />}
                        {msg.role === 'model' && <Brain className="h-4 w-4 text-white" />}
                        {msg.role === 'context' && <Database className="h-4 w-4 text-white" />}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <span className="font-semibold text-sm capitalize">{msg.role}</span>
                          <span className="text-xs text-gray-400">
                            {msg.timestamp.toLocaleTimeString()}
                          </span>
                        </div>
                        <div className="bg-gray-800 p-3 rounded-lg text-sm whitespace-pre-wrap">
                          {msg.content}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </div>

            <div className="mt-4">
              <div className="flex space-x-2">
                <div className="flex-1 relative">
                  <Input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Enter your message..."
                    className="bg-gray-800 border-gray-700 text-white pr-12"
                  />
                  <Button 
                    onClick={handleSend}
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-blue-600 hover:bg-blue-700"
                    size="sm"
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              <div className="text-center mt-2 text-sm text-gray-400">
                Press Enter to send • Context: {documents.length} documents active
              </div>
            </div>
          </TabsContent>

          {/* Context Flow Tab */}
          <TabsContent value="context" className="h-[600px] overflow-y-auto">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* User Context */}
                <Card className="bg-gray-800 border-gray-700">
                  <CardHeader>
                    <CardTitle className="flex items-center text-blue-400">
                      <div className="w-3 h-3 rounded-full bg-blue-500 mr-2"></div>
                      <Send className="mr-2 h-5 w-5" />
                      <span>User Input</span>
                    </CardTitle>
                    <CardDescription>
                      Direct input from the user
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="p-3 bg-gray-900 rounded text-sm">
                        <p className="text-gray-400 mb-2 text-xs">Last message:</p>
                        <p className="truncate">{input || "No input yet"}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Context Processor */}
                <Card className="bg-gray-800 border-gray-700">
                  <CardHeader>
                    <CardTitle className="flex items-center text-purple-400">
                      <div className="w-3 h-3 rounded-full bg-purple-500 mr-2"></div>
                      <Brain className="mr-2 h-5 w-5" />
                      <span>Context Processor</span>
                    </CardTitle>
                    <CardDescription>
                      Processes and enriches context
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-gray-400">Documents loaded:</span>
                        <span className="font-bold text-purple-400">{documents.length}</span>
                      </div>
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-gray-400">System context:</span>
                        <span className="font-bold text-purple-400">Ready</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">Memory segments:</span>
                        <span className="font-bold text-purple-400">{messages.length}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Model Response */}
                <Card className="bg-gray-800 border-gray-700">
                  <CardHeader>
                    <CardTitle className="flex items-center text-green-400">
                      <div className="w-3 h-3 rounded-full bg-green-500 mr-2"></div>
                      <Brain className="mr-2 h-5 w-5" />
                      <span>Model Output</span>
                    </CardTitle>
                    <CardDescription>
                      Generated response with context
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="p-3 bg-gray-900 rounded text-sm">
                        <p className="text-gray-400 mb-2 text-xs">Last response:</p>
                        <p className="truncate">{messages.length > 1 ? messages[messages.length - 1].content : "Waiting for input"}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
              
              <Card className="mt-6 bg-gray-800 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-center">Context Flow Visualization</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">User Message →</span>
                      <div className="flex-1 h-1 bg-gray-700 mx-4">
                        <div className="h-full bg-blue-500 w-3/4 animate-pulse"></div>
                      </div>
                      <span className="text-sm">Context Processor</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Context Enrichment →</span>
                      <div className="flex-1 h-1 bg-gray-700 mx-4">
                        <div className="h-full bg-purple-500 w-1/2 animate-pulse"></div>
                      </div>
                      <span className="text-sm">Documents ({documents.length})</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Model Processing →</span>
                      <div className="flex-1 h-1 bg-gray-700 mx-4">
                        <div className="h-full bg-green-500 w-2/3 animate-pulse"></div>
                      </div>
                      <span className="text-sm">Response Generation</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

          {/* Documents Tab */}
          <TabsContent value="documents" className="h-[600px] overflow-y-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {documents.map((doc, idx) => (
                <Card key={idx} className="bg-gray-800 border-gray-700">
                  <CardHeader>
                    <CardTitle className="flex items-center text-indigo-400">
                      <FileText className="mr-2 h-4 w-4" />
                      <span>{doc}</span>
                    </CardTitle>
                    <CardDescription>
                      Context document {idx + 1}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <div className="flex space-x-1">
                        <span className="text-xs bg-gray-700 px-2 py-1 rounded">Read</span>
                        <span className="text-xs bg-gray-700 px-2 py-1 rounded">Indexed</span>
                      </div>
                      <Button 
                        onClick={() => removeDocument(doc)}
                        variant="ghost" 
                        size="sm"
                        className="text-red-400 hover:text-red-300 hover:bg-red-900/20"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
              
              <Button onClick={addDocument} variant="outline" className="border-dashed border-2 h-32 flex flex-col items-center justify-center text-gray-400 hover:text-indigo-400 hover:border-indigo-500">
                <Plus className="h-8 w-8 mb-2" />
                <span>Add New Document</span>
              </Button>
            </div>
            
            <Card className="mt-6 bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="text-center">Document Context Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Total Documents:</span>
                    <span className="font-bold text-lg">{documents.length}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Context Window Usage:</span>
                    <span className="font-bold text-lg">{Math.min(documents.length * 5, 100)}%</span>
                  </div>
                  <div className="w-full bg-gray-700 h-2 rounded-full mt-2">
                    <div 
                      className="bg-indigo-500 h-2 rounded-full transition-all duration-500" 
                      style={{ width: `${Math.min(documents.length * 5, 100)}%` }}
                    ></div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* MCP Protocol Info */}
        <Card className="mt-6 bg-gray-800 border-gray-700">
          <CardHeader>
            <CardTitle className="flex items-center text-yellow-400">
              <Settings className="mr-2 h-5 w-5" />
              <span>Model Context Protocol Overview</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="space-y-2">
                <h4 className="font-semibold text-white">1. User Context</h4>
                <p className="text-gray-400 text-xs">
                  User inputs and preferences that shape the conversation context
                </p>
              </div>
              <div className="space-y-2">
                <h4 className="font-semibold text-white">2. Document Enrichment</h4>
                <p className="text-gray-400 text-xs">
                  External documents and knowledge bases are retrieved and processed
                </p>
              </div>
              <div className="space-y-2">
                <h4 className="font-semibold text-white">3. Model Processing</h4>
                <p className="text-gray-400 text-xs">
                  Context is fed to the model with proper instructions and constraints
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default MCPApp
