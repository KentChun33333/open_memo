"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.auth import router as auth_router
from backend.config import settings
from backend.routers.blogs import router as blogs_router
from backend.routers.mindmaps import router as mindmaps_router
from backend.routers.notes import router as notes_router

app = FastAPI(
    title=settings.app_name,
    description="OpenMemo — Knowledge management with blogs and mind maps",
    version="0.1.0",
)

# CORS for development (Vite runs on :5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(auth_router)
app.include_router(blogs_router)
app.include_router(mindmaps_router)
app.include_router(notes_router)


# Health check
@app.get("/api/health")
async def health():
    return {"status": "ok", "app": settings.app_name}


# Mount content assets (images, etc.) at /content-assets/
# to avoid conflicting with Vite's /assets/ path
assets_dir = settings.content_dir / "assets"
if assets_dir.exists():
    app.mount(
        "/content-assets",
        StaticFiles(directory=str(assets_dir), html=False),
        name="content-assets",
    )

# Mount nanobot-status data (cron jobs, memory) as static files
nanobot_dir = settings.content_dir / "nanobot-status"
if nanobot_dir.exists():
    app.mount(
        "/nanobot-status",
        StaticFiles(directory=str(nanobot_dir), html=False),
        name="nanobot-status",
    )

# Serve React frontend (production only — when dist/ exists)
frontend_dir = settings.frontend_dist
if frontend_dir.exists():
    from fastapi.responses import FileResponse

    # Mount the entire dist/ as static files first — this serves
    # Vite's built JS/CSS/images in /assets/ with correct MIME types
    app.mount(
        "/assets",
        StaticFiles(directory=str(frontend_dir / "assets")),
        name="frontend-assets",
    )

    # SPA fallback: all other routes → index.html for client-side routing
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        static_file = frontend_dir / full_path
        if full_path and static_file.exists() and static_file.is_file():
            return FileResponse(static_file)
        return FileResponse(frontend_dir / "index.html")
