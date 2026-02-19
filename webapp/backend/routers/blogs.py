"""Blog API endpoints."""

from fastapi import APIRouter, HTTPException

from backend.config import settings
from backend.services.content_loader import BlogPost, ContentLoader

router = APIRouter(prefix="/api/blogs", tags=["blogs"])

loader = ContentLoader(settings.content_dir)


class BlogListItem(BlogPost):
    """Blog post without full HTML for list views."""

    html: str = ""
    raw: str = ""


@router.get("", response_model=list[BlogListItem])
async def list_blogs():
    """List all blog posts (without full content)."""
    return loader.list_posts()


@router.get("/{slug}", response_model=BlogPost)
async def get_blog(slug: str):
    """Get a single blog post by slug."""
    post = loader.get_post(slug)
    if not post:
        raise HTTPException(status_code=404, detail=f"Blog post '{slug}' not found")
    return post
