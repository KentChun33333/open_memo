# Open Memo Dashboard

A React-based dashboard to showcase workflows and architectural insights from the open_memo documents.

## Features

- **Workflow Summaries** - Browse key documents with concise summaries
- **Tag Filtering** - Filter documents by topic (architecture, workflow, production, etc.)
- **Interactive Cards** - Click to view detailed key points and metadata
- **Responsive Design** - Clean, modern UI that works on all screen sizes

## Getting Started

```bash
cd open-memo-dashboard
npm start
```

Runs the app in development mode at http://localhost:3000

### Build for Production

```bash
npm run build
```

## Data Source

The dashboard reads from `/Users/kentchiu/Documents/Github/open_memo/doc/`.

Document categories include:
- **Architecture** - Agent architectures and design patterns
- **Workflow** - Execution plans and step-by-step processes
- **Production** - Industrial-grade requirements and best practices

## Tech Stack

- React 18 + TypeScript
- CSS Modules (inline styles)
- Responsive CSS Grid & Flexbox
