"""Markdown content loader — scans content/blogs/ and converts .md → HTML."""

from pathlib import Path
from typing import Optional

import frontmatter
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from pydantic import BaseModel


class ContentItem(BaseModel):
    """A generic parsed content item (blog, note, etc.)."""

    slug: str
    title: str
    date: str
    tags: list[str] = []
    icon: str = ""
    excerpt: str = ""
    html: str = ""
    raw: str = ""


class ContentLoader:
    """Loads and parses Markdown content from a specific subdirectory."""

    def __init__(self, content_dir: Path, sub_dir: str = "blogs"):
        self.target_dir = content_dir / sub_dir
        self._md = markdown.Markdown(
            extensions=[
                FencedCodeExtension(),
                CodeHiliteExtension(css_class="highlight", linenums=False),
                TableExtension(),
                "md_in_html",
            ]
        )

    def list_items(self) -> list[ContentItem]:
        """List all content items sorted by date (newest first)."""
        items = []
        if not self.target_dir.exists():
            return items

        for path in list(self.target_dir.glob("*.md")) + list(self.target_dir.glob("*.mdx")):
            item = self._parse_item(path, excerpt_only=True)
            if item:
                items.append(item)

        # Sort by date descending
        items.sort(key=lambda p: p.date, reverse=True)
        return items

    def get_item(self, slug: str) -> Optional[ContentItem]:
        """Get a single content item by slug."""
        md_file = self.target_dir / f"{slug}.md"
        mdx_file = self.target_dir / f"{slug}.mdx"
        
        target_file = md_file if md_file.exists() else mdx_file
        
        if not target_file.exists():
            return None
        return self._parse_item(target_file, excerpt_only=False)

    def _parse_item(self, path: Path, excerpt_only: bool = False) -> Optional[ContentItem]:
        """Parse a markdown file into a ContentItem."""
        try:
            content = path.read_text(encoding="utf-8")
            post = frontmatter.loads(content)

            # Extract metadata from frontmatter
            title = post.get("title", path.stem.replace("-", " ").replace("_", " ").title())
            date = str(post.get("date", "2025-01-01"))
            icon = post.get("icon", "")
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

            return ContentItem(
                slug=path.stem,
                title=title,
                date=date,
                tags=tags,
                icon=icon,
                excerpt=excerpt_text,
                html=html,
                raw=body if not excerpt_only else "",
            )
        except Exception:
            return None
