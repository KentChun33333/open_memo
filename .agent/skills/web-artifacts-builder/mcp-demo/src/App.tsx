import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

function App() {
  return (
    <div className="min-h-screen bg-background p-8">
      <header className="mb-8 text-center">
        <h1 className="text-4xl font-bold tracking-tight">MCP Demo Artifact</h1>
        <p className="mt-2 text-muted-foreground">
          A multi-component React application with Tailwind CSS & shadcn/ui components
        </p>
      </header>

      <main className="max-w-3xl mx-auto space-y-8">
        {/* Intro Card */}
        <Card>
          <CardHeader>
            <CardTitle>Welcome to the MCP Demo</CardTitle>
            <CardDescription>
              This artifact demonstrates multiple shadcn/ui components working together
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Built using the web-artifacts-builder skill with React, TypeScript, 
              Tailwind CSS, and 40+ shadcn/ui components - all bundled into a single HTML file.
            </p>
          </CardContent>
        </Card>

        {/* Tabs Component */}
        <Tabs defaultValue="components">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="components">Components</TabsTrigger>
            <TabsTrigger value="form">Form</TabsWarning>
            <TabsTrigger value="about">About</TabsTrigger>
          </TabsList>

          <TabsContent value="components" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle>Button Component</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <p className="text-sm text-muted-foreground">
                   Primary, secondary, outline, ghost, and link button variants available.
                  </p>
                  <div className="flex flex-wrap gap-2">
                    <Button>Default</Button>
                    <Button variant="outline">Outline</Button>
                    <Button variant="secondary">Secondary</Button>
                    <Button variant="ghost">Ghost</Button>
                    <Button variant="link">Link</Button>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Input & Label</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <Label htmlFor="example">Example Input</Label>
                    <Input id="example" placeholder="Type something..." />
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="form" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Sample Form</CardTitle>
                <CardDescription>
                  Basic input form with validation and submit button
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form className="space-y-4" onSubmit={(e) => {
                  e.preventDefault();
                  alert("Form submitted!");
                }}>
                  <div className="space-y-2">
                    <Label htmlFor="name">Name</Label>
                    <Input id="name" placeholder="Your name" required />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input id="email" type="email" placeholder="your@email.com" required />
                  </div>
                  <Button type="submit" className="w-full">Submit Form</Button>
                </form>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="about" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>About This Artifact</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <p>This demo showcases:</p>
                <ul className="list-disc pl-5 space-y-1">
                  <li>Multiple shadcn/ui components in one app</li>
                  <li>Tabs navigation with content switching</li>
                  <li>Responsive grid layouts using Tailwind CSS</li>
                  <li>Interactive forms with validation-ready structure</li>
                  <li>Complete bundling into a single HTML file</li>
                </ul>
                <p className="text-sm text-muted-foreground mt-4">
                  Built with the web-artifacts-builder skill to create self-contained HTML artifacts
                  for Claude AI conversations.
                </p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}

export default App
