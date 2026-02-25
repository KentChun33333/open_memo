---
name: blog-creator
description: Skill to generate high-quality technical blogs using MDX, Shiki syntax highlighting, and React Flow / Syncfusion for interactive diagrams.
---

# Blog Creator Skill

This skill explains how to build high-quality technical blogs for OpenMemo.

## Capabilities & Tech Stack

1. **MDX (Markdown + JSX)**: All technical blogs must be written in MDX to embed interactive React components securely inside Markdown.
2. **Shiki Syntax Highlighting**: Use Shiki for code blocks. It matches perfectly with VS Code themes taking code snippets to the highest visual fidelity standard for 2026.
3. **Interactive Diagrams**: Do not use static images for complex flows. Instead, embed interactive diagrams using **React Flow** or **Syncfusion Diagram** (e.g., clicking through steps of an ANN clustering algorithm).

## Instructions

When the user asks you to "create a blog about X" or "write a technical post":

1. First, draft the content outline and the React components you will need (e.g., `<InteractiveAlgorithmViewer />`).
2. Create a new `.mdx` file directly in `open_memo/webapp/content/blogs/` with the appropriate frontmatter (title, date, tags).
3. Implement the React components in the standard React component folder (if they are reusable) or as inline components in the MDX framework if supported by the host bundler.
4. Populate the MDX file with high-quality explanations, leveraging the interactive components you built to demonstrate the concepts dynamically.

## Example MDX Structure

```mdx
---
title: "Understanding Complex AI Algorithms"
date: "2026-02-21"
tags: ["AI", "Algorithms"]
---

import { InteractiveClusterMap } from '../components/InteractiveClusterMap'
import { ShikiCodeBlock } from '../components/ShikiCodeBlock'

# Introduction

We can explore the concepts dynamically...

<InteractiveClusterMap data={targetData} />

## Code Implementation

<ShikiCodeBlock language="python">
{`
def train_model():
    print("Training the ultimate model...")
`}
</ShikiCodeBlock>
```
