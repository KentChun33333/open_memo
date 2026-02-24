import React, { useMemo } from 'react';
import { ReactFlow, Controls, Background } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const initialNodes = [
    { id: '1', position: { x: 50, y: 150 }, data: { label: 'Agent Query' }, type: 'input' },
    { id: '2', position: { x: 250, y: 50 }, data: { label: 'Embed Query Vector' } },
    { id: '3', position: { x: 250, y: 250 }, data: { label: 'BM25 Full-Text Search' } },
    { id: '4', position: { x: 450, y: 50 }, data: { label: 'Vector Search ANN' } },
    { id: '5', position: { x: 650, y: 150 }, data: { label: 'RRF Fusion' } },
    { id: '6', position: { x: 800, y: 150 }, data: { label: 'Cross-Encoder Rerank' } },
    { id: '7', position: { x: 1000, y: 150 }, data: { label: 'Recency Boost' } },
    { id: '8', position: { x: 1200, y: 150 }, data: { label: 'Noise Filter' } },
    { id: '9', position: { x: 1400, y: 150 }, data: { label: 'Final Context Window' }, type: 'output' },
];

const initialEdges = [
    { id: 'e1-2', source: '1', target: '2', animated: true },
    { id: 'e1-3', source: '1', target: '3', animated: true },
    { id: 'e2-4', source: '2', target: '4' },
    { id: 'e4-5', source: '4', target: '5' },
    { id: 'e3-5', source: '3', target: '5' },
    { id: 'e5-6', source: '5', target: '6' },
    { id: 'e6-7', source: '6', target: '7' },
    { id: 'e7-8', source: '7', target: '8' },
    { id: 'e8-9', source: '8', target: '9' },
];

export default function MemoryFlowChart() {
    return (
        <div style={{ width: '100%', height: '400px', border: '1px solid var(--accent, #333)', borderRadius: '8px', margin: '20px 0', background: 'var(--bg-color, #1a1a1a)' }}>
            <ReactFlow
                nodes={initialNodes}
                edges={initialEdges}
                fitView
                colorMode="dark"
                minZoom={0.1}
            >
                <Background variant="dots" gap={12} size={1} />
                <Controls />
            </ReactFlow>
        </div>
    );
}
