# OpenMemo Web App

A production-level knowledge management platform with blogs and interactive mind maps.

- **Backend**: FastAPI (Python) — serves API and static files
- **Frontend**: React 19 + Vite — with React Flow for mind maps
- **Content**: Git-managed Markdown blogs and JSON mind maps
- **Auth**: Simple JWT login (default: `admin` / `openmemo`)
- **Deployment**: Docker multi-stage build for GCP Cloud Run

## Quick Start (Development)

### 1. Backend

```bash
cd webapp
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --reload --port 8080
```

### 2. Frontend

```bash
cd webapp/frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) — Vite proxies `/api/*` to the backend.

## Production (Docker)

```bash
cd webapp
docker build -t openmemo .
docker run -p 8080:8080 -e OPENMEMO_SECRET_KEY=your-secret openmemo
```

## Adding Content

### Blog Posts

Create `.md` files in `content/blogs/` with YAML frontmatter:

```markdown
---
title: "My Post Title"
date: "2025-02-19"
tags: ["topic1", "topic2"]
---

# Content here...
```

### Mind Maps

Create `.json` files in `content/mind-maps/` with this structure:

```json
{
  "title": "Map Title",
  "description": "What this map covers",
  "nodes": [
    {
      "id": "unique-id",
      "label": "Node Label",
      "description": "Node description",
      "targetFile": "other-map.json",
      "children": []
    }
  ],
  "edges": [
    { "source": "node1", "target": "node2" }
  ]
}
```

Use `targetFile` to link between mind maps for drill-down navigation.

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Health check |
| `GET /api/blogs` | List all blog posts |
| `GET /api/blogs/{slug}` | Get full blog post |
| `GET /api/mindmaps` | List all mind maps |
| `GET /api/mindmaps/{id}` | Get mind map data |
| `GET /api/mindmaps/{id}/resolve?target=file.json` | Resolve node link |
| `POST /api/auth/login` | Login (form data) |
| `GET /api/auth/me` | Current user |

## Deploy to GCP Cloud Run

1. Connect your GitHub repo to Cloud Build
2. Every push to `main` triggers a new build
3. Cloud Run performs blue/green deployment automatically
