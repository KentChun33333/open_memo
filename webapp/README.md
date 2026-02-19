# OpenMemo Web App

A production-level knowledge management platform with blogs, interactive mind maps, and nanobot agent monitoring.

- **Backend**: FastAPI (Python) — serves API and static files
- **Frontend**: React 19 + Vite — with React Flow for mind maps
- **Content**: Git-managed Markdown blogs, JSON mind maps, and nanobot status data
- **Auth**: Simple JWT login (default: `admin` / `openmemo`)
- **Deployment**: Docker multi-stage build for GCP Cloud Run

## Quick Start (Local Development)

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

### 3. Open in Browser

Open [http://localhost:5173](http://localhost:5173) — Vite proxies `/api/*` and `/nanobot-status/*` to the backend.

| Page | URL |
| --- | --- |
| Dashboard | [http://localhost:5173/](http://localhost:5173/) |
| Blogs | [http://localhost:5173/blogs](http://localhost:5173/blogs) |
| Mind Maps | [http://localhost:5173/mindmaps](http://localhost:5173/mindmaps) |
| Nanobot Status | [http://localhost:5173/nanobot](http://localhost:5173/nanobot) |

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

### Nanobot Status

The nanobot dashboard displays cron job schedules and agent memory. Data lives in `content/nanobot-status/`:

| File | Source | Description |
| --- | --- | --- |
| `cron-jobs.json` | `~/.nanobot/cron/jobs.json` | Scheduled job configurations |
| `memory.md` | `~/.nanobot/workspace/memory/MEMORY.md` | Agent persistent memory |

**Syncing data:** The `open_memo-git-update.sh` script automatically copies the latest nanobot data before each git push. You can also sync manually:

```bash
mkdir -p webapp/content/nanobot-status
cp ~/.nanobot/cron/jobs.json webapp/content/nanobot-status/cron-jobs.json
cp ~/.nanobot/workspace/memory/MEMORY.md webapp/content/nanobot-status/memory.md
```

The frontend fetches these files directly as static assets (no backend API needed) and parses them client-side.

## API Endpoints

| Endpoint | Description |
| --- | --- |
| `GET /api/health` | Health check |
| `GET /api/blogs` | List all blog posts |
| `GET /api/blogs/{slug}` | Get full blog post |
| `GET /api/mindmaps` | List all mind maps |
| `GET /api/mindmaps/{id}` | Get mind map data |
| `GET /api/mindmaps/{id}/resolve?target=file.json` | Resolve node link |
| `POST /api/auth/login` | Login (form data) |
| `GET /api/auth/me` | Current user |
| `GET /nanobot-status/cron-jobs.json` | Nanobot cron jobs (static) |
| `GET /nanobot-status/memory.md` | Nanobot memory (static) |

## Deploy to GCP Cloud Run

1. Connect your GitHub repo to Cloud Build
2. Every push to `main` triggers a new build
3. Cloud Run performs blue/green deployment automatically
