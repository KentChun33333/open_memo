"""Markdown content loader — scans content/blogs/ and converts .md → HTML."""

from pathlib import Path
from typing import Optional

import frontmatter
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from pydantic import BaseModel


class BlogPost(BaseModel):
    """A parsed blog post."""

    slug: str
    title: str
    date: str
    tags: list[str] = []
    excerpt: str = ""
    html: str = ""
    raw: str = ""


class ContentLoader:
    """Loads and parses Markdown blog posts from disk."""

    def __init__(self, content_dir: Path):
        self.blogs_dir = content_dir / "blogs"
        self._md = markdown.Markdown(
            extensions=[
                FencedCodeExtension(),
                CodeHiliteExtension(css_class="highlight", linenums=False),
                TableExtension(),
                "md_in_html",
            ]
        )

    def list_posts(self) -> list[BlogPost]:
        """List all blog posts sorted by date (newest first)."""
        posts = []
        if not self.blogs_dir.exists():
            return posts

        for md_file in sorted(self.blogs_dir.glob("*.md"), reverse=True):
            post = self._parse_post(md_file, excerpt_only=True)
            if post:
                posts.append(post)

        # Sort by date descending
        posts.sort(key=lambda p: p.date, reverse=True)
        return posts

    def get_post(self, slug: str) -> Optional[BlogPost]:
        """Get a single blog post by slug."""
        md_file = self.blogs_dir / f"{slug}.md"
        if not md_file.exists():
            return None
        return self._parse_post(md_file, excerpt_only=False)

    def _parse_post(self, path: Path, excerpt_only: bool = False) -> Optional[BlogPost]:
        """Parse a markdown file into a BlogPost."""
        try:
            content = path.read_text(encoding="utf-8")
            post = frontmatter.loads(content)

            # Extract metadata from frontmatter
            title = post.get("title", path.stem.replace("-", " ").replace("_", " ").title())
            date = str(post.get("date", "2025-01-01"))
            tags = post.get("tags", [])
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(",")]

            # Render HTML
            self._md.reset()
            body = post.content
            html = ""
            if not excerpt_only:
                html = self._md.convert(body)

            # Generate excerpt (first 200 chars of plain text)
            excerpt_text = body.strip()[:200]
            if len(body.strip()) > 200:
                excerpt_text += "..."

            return BlogPost(
                slug=path.stem,
                title=title,
                date=date,
                tags=tags,
                excerpt=excerpt_text,
                html=html,
                raw=body if not excerpt_only else "",
            )
        except Exception:
            return None
