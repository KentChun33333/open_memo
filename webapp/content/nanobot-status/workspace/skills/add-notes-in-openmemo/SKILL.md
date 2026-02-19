---
name: add-notes-in-openmemo
description: "Take quick notes, meeting minutes, or record life events and save them directly to OpenMemo."
---

# add-notes-in-openmemo

This skill allows you to capture quick thoughts, meeting notes, or life events and save them as Markdown files in your OpenMemo repository.

## Instructions

When the user wants to add a note, save a meeting minute, or record an event:

1. Capture the full content of the note.
2. Run the `write_openmemo_notes.py` script.
3. Pass the repository path and the note content as arguments.

## Usage Example

"Nanobot, take a note about the elder care project meeting. Discussion focused on local Whisper models for voice transcription."

## Scripts

### write_openmemo_notes.py

The primary script for writing the note to the filesystem.

- **Path**: `scripts/write_openmemo_notes.py`
- **Arguments**: `[repo_path] [note_content]`
- **Runtime**: `python3`

## Implementation Details

The script will:

- Automatically generate a slug-based filename with a timestamp.
- Add frontmatter (title, date, tags).
- Save the file to `webapp/content/notes/`.
