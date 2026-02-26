---
name: "top-conference-system-visualization-react-flow"
description: "Guidelines and code templates for creating professional, publication-quality (IEEE, NeurIPS, ACL) architecture diagrams using React Flow."
---

# Top Conference System Visualization (React Flow)

Academic and enterprise whitepaper system diagrams must prioritize **clarity, logical flow, grayscale compatibility, and strict orthogonal alignments**. When a user requests a "top conference" or "professional paper" diagram using React Flow, you must abandon standard colorful or messy web designs and adhere strictly to the following principles.

## 1. Core Principles of Academic Diagrams

1. **Functional Minimalism**: Do not use neon colors or dark modes unless specifically requested. Use scholarly, low-saturation tones (whites, light grays, muted blues) with high-contrast text.
2. **Strict Grid Alignment**: Nodes must align on a rigid coordinate plane. For example, columns at `x = 0, 250, 500` and rows at `y = 0, 150, 300`. This creates the structured appearance of LaTeX/TikZ diagrams.
3. **Orthogonal Routing (No Overlaps)**: Edges must NEVER diagonally cut across nodes. Always use `type: 'smoothstep'` or `type: 'step'`. You **must** define exact `sourceHandle` (e.g., 'bottom', 'right') and `targetHandle` (e.g., 'top', 'left') to explicitly control edge routing around obstacles.
4. **Logical Grouping**: Distinct system phases (e.g., "Data Ingestion", "Agent Inference", "Retrieval") should visually group nodes together or follow a strict horizontal (left-to-right) or vertical (top-to-bottom) pipeline.

## 2. The Color Palette (Grayscale / Print Compatible)

Top conference diagrams are often printed in black and white. Use this palette for nodes to ensure professional contrast:

- **Core System Nodes**: `background: '#ffffff', border: '2px solid #334155', color: '#0f172a'`
- **Databases/Storage**: `background: '#f8fafc', border: '2px dashed #64748b', color: '#0f172a'` (Adding a radius `borderRadius: '4px'` or making it an explicit DB shape if possible).
- **LLMs / Processing Agents**: `background: '#f1f5f9', border: '2px solid #0f172a', color: '#000000', fontWeight: 'bold'`
- **Highlights/Gates**: Use muted functional colors sparingly, e.g., `border: '2px solid #0369a1'` (muted blue) or `#991b1b` (muted red).

## 3. Reference Implementation

Here is the perfect boilerplate to generate a publication-ready diagram. **Copy this structure exactly when writing JSX.**

```jsx
import React from 'react';
import { ReactFlow, Controls, Background, MarkerType } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

// 1. Define standard node styles for consistency
const scholarlyNodeStyle = {
    padding: '14px 20px',
    borderRadius: '4px', // Sharp, academic corners
    fontSize: '14px',
    fontFamily: 'system-ui, -apple-system, sans-serif',
    fontWeight: '500',
    width: '200px',
    textAlign: 'center',
    background: '#ffffff',
    color: '#0f172a',
    border: '2px solid #334155',
    boxShadow: '2px 2px 0px 0px rgba(51, 65, 85, 0.2)', // Hard shadow typical of academic figures
};

// 2. Strict Grid Coordinates
const initialNodes = [
    // Column 1: Input
    { 
        id: 'input', 
        position: { x: 50, y: 150 }, 
        data: { label: 'User Query\n(q)' }, 
        sourcePosition: 'right', // EXPLICIT ROUTING
        targetPosition: 'left',
        style: { ...scholarlyNodeStyle, border: '2px dashed #94a3b8' } 
    },
    
    // Column 2: Processing Matrix
    { 
        id: 'llm_agent', 
        position: { x: 350, y: 50 }, 
        data: { label: 'Agentic Controller\n(LLM)' }, 
        sourcePosition: 'right',
        targetPosition: 'left',
        style: { ...scholarlyNodeStyle, fontWeight: 'bold', border: '2px solid #0f172a' } 
    },
    { 
        id: 'database', 
        position: { x: 350, y: 250 }, 
        data: { label: 'Knowledge Graph\n(Subspace D)' }, 
        sourcePosition: 'right',
        targetPosition: 'left',
        style: { ...scholarlyNodeStyle, background: '#f8fafc' } 
    },

    // Column 3: Output
    { 
        id: 'output', 
        position: { x: 650, y: 150 }, 
        data: { label: 'Final Output\nR(q, d)' }, 
        sourcePosition: 'right',
        targetPosition: 'left',
        style: scholarlyNodeStyle 
    },
];

// 3. Orthogonal, Non-Overlapping Edges
const initialEdges = [
    { 
        id: 'e-in-llm', 
        source: 'input', 
        target: 'llm_agent', 
        type: 'smoothstep', // ALWAYS smoothstep or step
        markerEnd: { type: MarkerType.ArrowClosed, color: '#334155' },
        style: { strokeWidth: 2, stroke: '#334155' }
    },
    { 
        id: 'e-in-db', 
        source: 'input', 
        target: 'database', 
        type: 'smoothstep', 
        markerEnd: { type: MarkerType.ArrowClosed, color: '#334155' },
        style: { strokeWidth: 2, stroke: '#334155' }
    },
    { 
        id: 'e-llm-out', 
        source: 'llm_agent', 
        target: 'output', 
        type: 'smoothstep', 
        label: 'Policy',
        labelStyle: { fill: '#334155', fontWeight: 600 },
        markerEnd: { type: MarkerType.ArrowClosed, color: '#334155' },
        style: { strokeWidth: 2, stroke: '#334155' }
    },
    { 
        id: 'e-db-out', 
        source: 'database', 
        target: 'output', 
        type: 'smoothstep', 
        label: 'Context',
        labelStyle: { fill: '#334155', fontWeight: 600 },
        markerEnd: { type: MarkerType.ArrowClosed, color: '#334155' },
        style: { strokeWidth: 2, stroke: '#334155' }
    },
];

export default function AcademicArchitectureDiagram() {
    return (
        // The container MUST have a light, clean background with a tight border. No dark mode here.
        <div style={{ width: '100%', height: '500px', border: '1px solid #cbd5e1', borderRadius: '4px', margin: '2rem 0', background: '#fefefe' }}>
            <ReactFlow
                nodes={initialNodes}
                edges={initialEdges}
                fitView
                fitViewOptions={{ padding: 0.2 }}
                minZoom={0.1}
                attributionPosition="bottom-right"
            >
                {/* A subtle dot background mimics a drafting board */}
                <Background variant="dots" gap={20} size={1} color="#e2e8f0" />
                <Controls />
            </ReactFlow>
        </div>
    );
}
```

## 4. Checklist for Success
When you use this skill to generate a diagram, check off the following:
- [ ] Is the background strictly light/white for printability?
- [ ] Are all nodes perfectly aligned on a mathematical grid (e.g., all X or Y coordinates match exactly)?
- [ ] Do all edges use `type: 'smoothstep'`?
- [ ] Did you include `sourcePosition: 'bottom'`, `targetPosition: 'top'`, etc., on EVERY node so that React Flow mathematically forces the lines to route *around* the boxes instead of drawing straight lines through them?
- [ ] Are the fonts legible and the box shadows "hard" (not blurry UI glows) to resemble a vector graphic?
