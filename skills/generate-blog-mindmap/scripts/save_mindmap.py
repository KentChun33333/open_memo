#!/usr/bin/env python3
import sys
import json
import os
import re
from datetime import datetime

DEST_DIR = os.path.expanduser("~/.nanobot/workspace/openmemo/webapp/content/mind-maps")

def generate_slug(title):
    # Convert to lowercase and replace non-alphanumeric with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    return slug

def main():
    # Read input either from an argument or from stdin
    if len(sys.argv) > 1:
        json_content = sys.argv[1]
    else:
        json_content = sys.stdin.read()

    if not json_content.strip():
        print("Error: No JSON content provided.")
        sys.exit(1)

    try:
        # Parse JSON to validate it
        data = json.loads(json_content)
    except json.JSONDecodeError as e:
        print(f"Error validating JSON: {e}")
        sys.exit(1)

    # Basic schema validation
    required_keys = ['title', 'description', 'date', 'nodes', 'edges']
    for key in required_keys:
        if key not in data:
            print(f"Error: Missing required key '{key}' in JSON payload.")
            sys.exit(1)

    # Inject current date if missing
    if 'date' not in data:
        data['date'] = datetime.now().strftime("%Y-%m-%d")

    # Ensure destination directory exists
    os.makedirs(DEST_DIR, exist_ok=True)

    # Generate filename
    slug = generate_slug(data['title'])
    if not slug:
        slug = f"mindmap-{int(datetime.now().timestamp())}"
    
    filename = f"{slug}.json"
    filepath = os.path.join(DEST_DIR, filename)

    # Write the formatted output
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Successfully saved mind map to: {filepath}")
    except Exception as e:
        print(f"Error saving file to {filepath}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
