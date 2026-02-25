title: "Generate Blog Mindmap"
description: "A skill to analyze related blog posts and progressively build a mind map JSON file, saving it to the OpenMemo mind-maps directory."
---

# Generate Blog Mindmap

This skill allows you to summarize and extract ideas from existing blog posts to progressively build a comprehensive mind map in JSON format, which is then saved to the OpenMemo mind maps directory.

## Instructions

When the user asks to summarize blogs or create a mind map from existing content:

1.  **Search:** Use the `grep_search` or `list_dir` and `view_file` tools to explore current blog posts in `~/.nanobot/workspace/openmemo/webapp/content/blogs`.
2.  **Analyze:** Read the content of the relevant blog posts.
3.  **Synthesize:** Progressively summarize the ideas into a hierarchical structure. You must output the mind map according to the `MindMapJSON` schema, which includes a root node with a `children` array, where each child can also have its own `children` array.
4.  **Save:** Once the JSON structure is complete, call the `save_mindmap.py` script and pass the valid JSON string as the first argument, or pass it via standard input.

## Schema Requirements

The extracted mind map MUST follow this structure:
```json
{
    "title": "Main Topic Title",
    "date": "2026-02-19",
    "description": "A high-level overview of the mind map topic.",
    "nodes": [
        {
            "id": "root_node_id",
            "label": "Root Topic",
            "description": "Root topic description",
            "children": [
                 {
                     "id": "child_1",
                     "label": "Sub Topic 1",
                     "description": "Description of sub topic 1"
                 }
            ]
        }
    ],
    "edges": [
         {
             "source": "root_node_id",
             "target": "child_1"
         }
    ]
}
```

## Few-Shot Example

**User:** Can you create a mind map summarizing our blog posts about agentic memory?

**Agent Thought Process:**
1.  *I need to search for agentic memory blogs.* (Calls `grep_search` or `list_dir` on `~/.nanobot/workspace/openmemo/webapp/content/blogs*`)
2.  *I found `2026-02-24-advanced-agentic-memory-system.mdx`.* (Calls `view_file` to read the content).
3.  *I will synthesize this into the required JSON format.* (Generates JSON payload).
4.  *I will now execute the save script.* (Calls `run_command` with `python3 ~/.nanobot/workspace/skills/generate-blog-mindmap/scripts/save_mindmap.py '<JSON_STRING>'`)

## Scripts

### save_mindmap.py

The main script to validate and securely save the generated mind map JSON to the OpenMemo content repository.

-   **Path**: `scripts/save_mindmap.py`
-   **Arguments**: `[json_content_string]` (Can also accept JSON via `stdin` if argument is omitted)
-   **Runtime**: `python3`
