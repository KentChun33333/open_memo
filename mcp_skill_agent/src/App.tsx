import { useState } from "react";

export default function App() {
  const [showDiagram, setShowDiagram] = useState(false);

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Header */}
      <header className="bg-indigo-600 text-white p-4 text-center text-lg font-semibold mb-6">
        Model Context Protocol (MCP) Demo
      </header>

      {/* Main content */}
      <main className="flex-1 p-6 space-y-8">
        {/* Explanation section */}
        <section>
          <h2 className="text-xl font-medium mb-2">What is MCP?</h2>
          <p>The Model Context Protocol proposes a standardized way for AI models to describe, retrieve,
            and update contextual information that influences their outputs.</p>

          {/* Diagram placeholder */}
          <pre className="bg-white p-3 rounded text-sm overflow-x-auto border prose max-w-none">
            // Diagram Placeholder: MCP Architecture
            +-------------------+        +------------------+
            |   Context Provider|<------>|   Context       |
            +-------------------+        +------------------+
                                       |
                               +--------------------------+
                               |  Context Consumer (AI)   |
                               +--------------------------+
          </pre>
        </section>

        {/* Interactive example */}
        <section>
          <h2 className="text-xl font-medium mb-2">Interactive Demo</h2>
          <p>Toggle a local state to simulate loading context.</p>
          <button
            onClick={() => setShowDiagram((s) => !s)}
            className="rounded bg-blue-500 px-4 py-2 text-white hover:bg-blue-600 transition"
          >
            {showDiagram ? "Hide" : "Show"} Diagram
          </button>
          {showDiagram && (
            <div className="bg-white p-4 rounded shadow-md mt-2">
              <p>This area would contain a visual diagram of the protocol.</p>
            </div>
          )}
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-gray-200 text-center p-3 text-sm">
        © 2025 MCP Sample App
      </footer>
    </div>
  );
}