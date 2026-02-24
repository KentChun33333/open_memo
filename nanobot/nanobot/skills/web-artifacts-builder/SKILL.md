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

### Step 2: Develop Your Artifact in the <Vite Project Folder>

As professional nodejs developer, Build your application by editing the generated files, instrunction base on user request.

##### Codeing Guildence

1. levaerge the component we built in step 1 to build your artifact. where we have

- ✅ React + TypeScript (via Vite)
- ✅ Tailwind CSS 3.4.1 with shadcn/ui theming system
- ✅ Path aliases (`@/`) configured
- ✅ 40+ shadcn/ui components pre-installed
- ✅ All Radix UI dependencies included
- ✅ Parcel configured for bundling (via .parcelrc)
- ✅ Node 18+ compatibility (auto-detects and pins Vite version)

1. **Entry Point**: Modify `<project-name>/src/App.tsx` to implement your main logic, content and layout.

2. **Components**:
   - Create new components in `<project-name>/src/components/` if needed.
   - Only Use pre-installed shadcn/ui components: `import { Button } from "@/components/ui/button"`.
   - Do not use any other components to make sure the artifact can be bundled into a single HTML file in next step.

3. **Styling**: Apply Tailwind CSS classes directly (e.g., `className="p-4 rounded-lg"`).
4. **Icons**: Use `lucide-react` for icons (pre-installed).

5. **Tip**: Keep the design self-contained. Avoid external image links if possible; use SVG components or base64 data URIs so the final bundled artifact works offline.

6. **Troubleshooting & Coding Guidance (Important for Builds)**:

   If you encounter build errors related to PostCSS or Asset Resolution (Vite vs Parcel conflicts), follow these patterns:

   **A) PostCSS Config Conflict**:
   Parcel dislikes `postcss.config.js` with JS exports. Always use `.postcssrc` (JSON) and avoid redundant `autoprefixer`.
   - **Bad**: `postcss.config.js` exists with `export default { plugins: { ... } }`
   - **Fix**: Delete `postcss.config.js` and create `.postcssrc`:

       ```json
       {
         "plugins": {
           "tailwindcss": {}
         }
       }
       ```

   **B) Asset Paths (Vite vs Parcel)**:
   Vite Magic (`/public/file.svg` -> `/file.svg`) does NOT work in Parcel builds. You must be explicit or import relatively.
   - **Bad**: `import logo from '/vite.svg'` (assumes `public/` is root)
   - **Fix (Option 1)**: Explicit public path: `import logo from '/public/vite.svg'`
   - **Fix (Option 2)**: Relative import: `import logo from './assets/logo.svg'`

   **C) Case Study: mcp-demo Failure**:
   The `mcp-demo` template typically fails because it includes a JS-based `postcss.config.js` and uses root-relative asset imports (`/vite.svg`). Follw fixing A) and B) above will resolve this.

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

## Reference

- **shadcn/ui components**: <https://ui.shadcn.com/docs/components>
