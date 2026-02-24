---
name: diagram-builder
description: Skill to generate high-quality, interactive, and beautifully styled architecture diagrams using React Flow (React/XYFlow).
---

# Diagram Builder Skill

This skill explains how to build high-quality, complex technical architecture diagrams (like Kubernetes clusters, system architectures, or ML pipelines) for OpenMemo.

## Capabilities & Tech Stack

1. **React Flow (`@xyflow/react`)**: The primary library for rendering node-based UIs and interactive diagrams.
2. **Custom Nodes**: Do not use just the default nodes. High-quality diagrams require custom React components for nodes (e.g., a "Kubernetes Pod" node with an icon and specific styling, or a "Database" cylinder).
3. **Tailwind CSS / Standard CSS**: Ensure nodes and edges have crisp, professional styling (e.g., dashed edges for network requests, solid edges for data flow).
4. **Group Nodes**: Use parent/child node relationships to represent bounded contexts (like "K8s Control Plane", "VPC", or "Worker Nodes").
5. **Auto Layout**: For complex graphs, integrate `dagre` or `elkjs` to automatically calculate positions so the diagram doesn't load as a messy pile.

## Instructions

When the user asks you to "create an architecture diagram of X" or "draw a flowchart for Y":

1. **Understand the Architecture**: First, map out the required Entities (Nodes), their Categories (Groups), and their Relationships (Edges).
2. **Create Custom Node Components**: Draft reusable React components for the different types of elements. For example:
    * `<ServiceNode />` (Blue theme, cog icon)
    * `<DatabaseNode />` (Purple theme, database icon)
    * `<GroupNode />` (Transparent background with a dashed border representing a Subnet or Cluster)
3. **Define Initial Nodes and Edges**: Construct the `initialNodes` and `initialEdges` arrays.
    * Use appropriate edge markers (arrows) and styles (dashed/animated).
    * Assign nodes to parent groups using the `parentNode` attribute.
4. **Create the Main Flow Component**: Build the container that renders the `<ReactFlow />` component, injecting the custom `nodeTypes`.
5. **Embed in MDX**: Save the component in the appropriate React directory and import it into the requested `.mdx` blog post or note using the `blog-creator` skill guidelines.

## Example: Complex Component Structure

```tsx
import React, { useCallback } from 'react';
import {
  ReactFlow,
  useNodesState,
  useEdgesState,
  addEdge,
  Background,
  Controls,
  MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

// 1. Define Custom Nodes outside the render cycle
const CustomPodNode = ({ data }) => (
  <div className="border border-red-500 rounded p-2 bg-white text-xs">
    <div className="font-bold text-red-700">{data.label}</div>
  </div>
);

const GroupNode = ({ data }) => (
  <div className="border-2 border-dashed border-blue-400 bg-blue-50/50 w-full h-full rounded-lg pointer-events-none p-4">
    <div className="text-blue-800 font-semibold mb-2">{data.label}</div>
  </div>
);

const nodeTypes = {
  pod: CustomPodNode,
  group: GroupNode,
};

// 2. Define Architecture
const initialNodes = [
  // Parent Node (Cluster)
  {
    id: 'k8s-cluster',
    type: 'group',
    position: { x: 0, y: 0 },
    style: { width: 400, height: 300 },
    data: { label: 'K8s Worker Nodes' },
  },
  // Child Nodes (Pods within Cluster)
  {
    id: 'pod-1',
    type: 'pod',
    position: { x: 50, y: 50 },
    data: { label: 'ML Model API' },
    parentNode: 'k8s-cluster',
    extent: 'parent',
  },
  {
    id: 'ingress',
    position: { x: 150, y: -100 },
    data: { label: 'Ingress Controller' },
    style: { background: '#ffcc00', padding: 10, borderRadius: 20 },
  }
];

const initialEdges = [
  {
    id: 'e1',
    source: 'ingress',
    target: 'pod-1',
    animated: true,
    style: { stroke: '#ff6600' },
    markerEnd: { type: MarkerType.ArrowClosed, color: '#ff6600' },
  },
];

export default function ArchitectureDiagram() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  );

  return (
    <div style={{ width: '100vw', height: '600px' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
```

## Critical Rules

* **Never use static images** for new diagrams. ALways build React components.
* Ensure all technical charts have a polished, professional aesthetic mirroring modern cloud dashboards.
