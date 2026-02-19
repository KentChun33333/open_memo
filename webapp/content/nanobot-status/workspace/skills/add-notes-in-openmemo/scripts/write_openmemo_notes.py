import sys
import os
from datetime import datetime
import re

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text).strip('-')
    return text

def create_note(content, repo_path):
    # Ensure notes directory exists
    notes_dir = os.path.join(repo_path, 'webapp', 'content', 'notes')
    os.makedirs(notes_dir, exist_ok=True)
    
    # Generate title from first line or timestamp
    lines = [l.strip() for l in content.split('\n') if l.strip()]
    if not lines:
        return "Error: Empty note content."
    
    original_title = lines[0]
    # Remove # if it's a markdown title
    clean_title = original_title.lstrip('#').strip()
    
    timestamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
    slug = slugify(clean_title)
    if not slug:
        slug = "untitled-note"
    
    filename = f"{timestamp}-{slug}.md"
    filepath = os.path.join(notes_dir, filename)
    
    # Prepare Frontmatter
    date_str = datetime.now().strftime('%Y-%m-%d')
    frontmatter = f"""---
title: "{clean_title}"
date: "{date_str}"
tags: ["quick-note", "consciousness"]
summary: "{clean_title[:100]}..."
---

"""
    
    full_content = frontmatter + content
    
    with open(filepath, 'w') as f:
        f.write(full_content)
    
    return f"Successfully created note: {filename} in {notes_dir}"

if __name__ == "__main__":
    # Enforced full path from SKILL.md
    DEFAULT_REPO_PATH = "/Users/kentchiu/Documents/Github/open_memo"
    
    if len(sys.argv) < 2:
        print("Usage: python write_openmemo_notes.py <note_content>")
        sys.exit(1)
        
    # Validating repository presence
    if not os.path.exists(DEFAULT_REPO_PATH):
        print(f"Error: OpenMemo repository not found at {DEFAULT_REPO_PATH}")
        sys.exit(1)
        
    note_content = " ".join(sys.argv[1:])
    
    result = create_note(note_content, DEFAULT_REPO_PATH)
    print(result)
