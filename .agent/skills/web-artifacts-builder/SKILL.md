---
name: web-artifacts-builder
description: Suite of tools for creating elaborate, multi-component claude.ai HTML artifacts using modern frontend web technologies (React, Tailwind CSS, shadcn/ui). Use for complex artifacts requiring state management, routing, or shadcn/ui components - not for simple single-file HTML/JSX artifacts.
license: Complete terms in LICENSE.txt
---

# Web Artifacts Builder

To build powerful frontend claude.ai artifacts, follow these steps:

**Agent Note**: You must complete steps 1, 2, AND 3 in sequence. Do not stop until you have produced the bundled HTML file.

1. Initialize the frontend repo using `scripts/init-artifact.sh`
2. Develop your artifact by editing the generated code
3. Bundle all code into a single HTML file using `scripts/bundle-artifact.sh`
4. Display artifact to user
5. (Optional) Test the artifact

**Stack**: React 18 + TypeScript + Vite + Parcel (bundling) + Tailwind CSS + shadcn/ui

## Design & Style Guidelines

VERY IMPORTANT: To avoid what is often referred to as "AI slop", avoid using excessive centered layouts, purple gradients, uniform rounded corners, and Inter font.

## Quick Start

### Step 1: Initialize Project

Run the initialization script to create a new React project:

```bash
bash scripts/init-artifact.sh <project-name>
cd <project-name>
```

This creates a fully configured project with:

- ✅ React + TypeScript (via Vite)
- ✅ Tailwind CSS 3.4.1 with shadcn/ui theming system
- ✅ Path aliases (`@/`) configured
- ✅ 40+ shadcn/ui components pre-installed
- ✅ All Radix UI dependencies included
- ✅ Parcel configured for bundling (via .parcelrc)
- ✅ Node 18+ compatibility (auto-detects and pins Vite version)

### Step 2: Develop Your Artifact in the <Vite Project Folder>

Start develop your artifact in the <Vite Project Folder> that you initialized in step 1.

As professional nodejs developer, Build your application by editing the generated files, instrunction as below.

Notice that the main file is <project-name>/src/App.tsx, you can first define the UI, then implement the logic, and components.

1. **Entry Point**: Modify `<project-name>/src/App.tsx` to implement your main logic, content and layout.

2. **Components**:
   - Create new components in `<project-name>/src/components/` if needed.
   - Use pre-installed shadcn/ui components: `import { Button } from "@/components/ui/button"`.
3. **Styling**: Apply Tailwind CSS classes directly (e.g., `className="p-4 rounded-lg"`).
4. **Icons**: Use `lucide-react` for icons (pre-installed).

**Tip**: Keep the design self-contained. Avoid external image links if possible; use SVG components or base64 data URIs so the final bundled artifact works offline.

### Step 3: Bundle to Single HTML File

To bundle the React app into a single HTML artifact:

you are in the  <project-name> where is the root folder now, and you run the skill script at skill script folder

```bash
bash <your skill folder>/scripts/bundle-artifact.sh
```

This creates `bundle.html` - a self-contained artifact with all JavaScript, CSS, and dependencies inlined. This file can be directly shared in Claude conversations as an artifact.

**Requirements**: Your project must have an `index.html` in the root directory.

**What the script does**:

- Installs bundling dependencies (parcel, @parcel/config-default, parcel-resolver-tspaths, html-inline)
- Creates `.parcelrc` config with path alias support
- Builds with Parcel (no source maps)
- Inlines all assets into single HTML using html-inline

### Step 4: Share Artifact with User

Finally, share or point out the bundled HTML file in conversation with the user so they can view it as an artifact.

### Step 5: Testing/Visualizing the Artifact (Optional)

Note: This is a completely optional step. Only perform if necessary or requested.

To test/visualize the artifact, use available tools (including other Skills or built-in tools like Playwright or Puppeteer). In general, avoid testing the artifact upfront as it adds latency between the request and when the finished artifact can be seen. Test later, after presenting the artifact, if requested or if issues arise.

## Reference

- **shadcn/ui components**: <https://ui.shadcn.com/docs/components>
