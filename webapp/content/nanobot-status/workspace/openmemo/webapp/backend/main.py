"""FastAPI application entry point."""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.auth import get_current_user, User

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


# Serve content assets securely (requires auth)
@app.get("/content-assets/{file_path:path}")
async def get_content_asset(file_path: str, current_user: User = Depends(get_current_user)):
    assets_dir = settings.content_dir / "assets"
    file = assets_dir / file_path
    if not file.exists() or not file.is_file():
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Security check to prevent directory traversal
    try:
        file.resolve().relative_to(assets_dir.resolve())
    except ValueError:
         raise HTTPException(status_code=403, detail="Forbidden")
         
    return FileResponse(file)

# Serve nanobot status files
@app.get("/nanobot-status/{file_path:path}")
async def get_nanobot_status(file_path: str, current_user: User = Depends(get_current_user)):
    # Exception: allow public access to reflections.json for frontend "Active Consciousness" feature
    is_public_reflection = file_path == "reflections.json"
    
    if not is_public_reflection and not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required for nanobot session logs",
        )
        
    nanobot_dir = settings.content_dir / "nanobot-status"
    file = nanobot_dir / file_path
    if not file.exists() or not file.is_file():
        raise HTTPException(status_code=404, detail="Status file not found")
        
    # Security check to prevent directory traversal
    try:
        file.resolve().relative_to(nanobot_dir.resolve())
    except ValueError:
         raise HTTPException(status_code=403, detail="Forbidden")
         
    return FileResponse(file)

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
