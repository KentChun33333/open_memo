# MCP Demo Artifact

A demonstration of the Model Context Protocol (MCP) using React, TypeScript, Tailwind CSS, and shadcn/ui.

## Features

- **Interactive MCP interface** showcasing server connections, prompts, and resources
- **Shadcn/ui components** for polished, accessible UI elements
- **State management** with React hooks for real-time updates
- **Offline-capable**: Bundled into a single HTML file for easy sharing

## How to Run

1. To build the artifact, run:

   ```bash
   bash scripts/bundle-artifact.sh
   ```

2. View the generated `bundle.html` in a browser

## Components

The artifact includes:

- `ServerConfig` panel for managing MCP servers
- `PromptExecutor` for testing prompts
- `ResourceViewer` to inspect available resources
- `LogViewer` for real-time communication logs

## Tech Stack

- React 18 + TypeScript
- Vite (development)
- Parcel (bundling)
- Tailwind CSS + shadcn/ui

## License

MIT
