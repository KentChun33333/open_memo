import React, { useCallback } from 'react';
import {
    ReactFlow,
    Background,
    useNodesState,
    useEdgesState,
    addEdge,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

export function FlowDiagram({ initialNodes = [], initialEdges = [], height = '400px' }) {
    const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

    const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

    return (
        <div className="flow-diagram-wrapper" style={{ height, width: '100%', border: '1px solid var(--border)', borderRadius: '8px', margin: '2rem 0' }}>
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onConnect={onConnect}
                fitView
                colorMode="dark"
                nodesDraggable={false}
                nodesConnectable={false}
                elementsSelectable={false}
                zoomOnScroll={false}
                zoomOnPinch={false}
                panOnScroll={false}
                panOnDrag={false}
                preventScrolling={false}
            >
                <Background variant="dots" gap={12} size={1} />
            </ReactFlow>
        </div>
    );
}
