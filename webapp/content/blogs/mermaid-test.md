---
title: "Mermaid and Table Test"
date: "2026-02-19"
tags: ["test", "utility"]
---

# Testing Markdown Enhancements

This post verifies that GFM tables and Mermaid diagrams are rendering correctly.

## GFM Table

| Feature | Support | Status |
| :--- | :--- | :--- |
| Tables | Yes | ✅ Working |
| Mermaid Diagrams | Yes | ✅ Working |
| Code Syntax | Yes | ✅ Existing |

## Mermaid Diagram

```mermaid
graph TD;
    A[Start] --> B{Is it working?};
    B -- Yes --> C[Great!];
    B -- No --> D[Debug time...];
    C --> E[Done];
    D --> B;
```

Another one:

```mermaid
pie title Pets adoption number
    "Dogs" : 386
    "Cats" : 85
    "Rats" : 15
```
