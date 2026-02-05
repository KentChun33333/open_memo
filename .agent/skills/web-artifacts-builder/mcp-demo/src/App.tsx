import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Lightbulb, FileText, MessageSquare } from "lucide-react"

interface ContextItem {
  id: string
  title: string
  type: "resource" | "document" | "intent"
  summary: string
}

const mockContext: ContextItem[] = [
  { id: "1", title: "Product Roadmap Q4", type: "document", summary: "Q4 priorities: new dashboard, auth refactor, mobile-first." },
  { id: "2", title: "User Feedback: Dark Mode", type: "intent", summary: "Users request dark mode with improved theme persistence." },
  { id: "3", title: "Tailwind CSS Docs", type: "resource", summary: "https://tailwindcss.com/docs" },
]

export default function App() {
  const [isExpanded, setIsExpanded] = useState(false)
  const [inputText, setInputText] = useState("How do I implement MCP context?")

  const handleSend = () => {
    alert("Context sent with input: " + inputText)
  }

  return (
    <div className="min-h-screen bg-background p-6 font-sans">
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex items-center gap-3">
          <Lightbulb className="text-yellow-500" />
          <h1 className="text-3xl font-bold">Model Context Protocol (MCP) Artifact</h1>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Context Pool</CardTitle>
            <CardDescription>Example static MCP context items</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {mockContext.map((item) => (
              <div key={item.id} className="flex gap-3 items-start border rounded-lg p-3 hover:bg-accent/50 transition">
                <Badge variant="outline" className="capitalize w-24 justify-center">{item.type}</Badge>
                <div className="flex-1">
                  <div className="font-medium">{item.title}</div>
                  <div className="text-sm text-muted-foreground mt-1">{item.summary}</div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <MessageSquare className="text-blue-500" />
              <CardTitle>Input Context</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex gap-2">
              <Input
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Your query to embed in context..."
              />
              <Button onClick={handleSend}>Send</Button>
            </div>
            {isExpanded && (
              <div className="mt-3 p-3 bg-muted/30 rounded-md text-sm text-amber-600">
                ✓ Context sent with {mockContext.length} artifacts + user query
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}