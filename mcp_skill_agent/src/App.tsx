import { useState } from "react";
import reactLogo from "./assets/react.svg";

import "./App.css";

function App() {
  const [count, setCount] = useState(0);

  return (
    <>
      <h1>Model Context Protocol (MCP) Demo</h1>
      <p>
        This demo shows how an MCP server can expose its
        <strong>context channels</strong>, {
          <strong>capabilities</strong>, and
          <strong>tool invocations</strong> to a client.
        </p>
      </p>
      <div className="card">
        <button onClick={() => setCount(c => c + 1)} className="btn">
          Clicked {count} times
        </button>
      </div>
      <p className="mt-4 text-sm text-muted">
        Built with React, Tailwind CSS and Shadcn UI – ready for bundling.
      </p>
    </>
  );
}

export default App;