import { useCallback } from 'react';
import {
    ReactFlow,
    MiniMap,
    Controls,
    Background,
    useNodesState,
    useEdgesState,
    addEdge,
    MarkerType
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const initialNodes = [
    {
        id: 'bus',
        type: 'default',
        position: { x: 250, y: 50 },
        data: { label: 'Message Bus\n(Inbound)' },
        style: {
            background: 'rgba(22, 33, 62, 0.9)',
            color: '#e8e8f0',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: '8px',
            padding: '10px 20px',
            fontWeight: 'bold',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.4)'
        }
    },
    {
        id: 'loop',
        type: 'default',
        position: { x: 250, y: 150 },
        data: { label: '_process_message()\nAgentLoop' },
        style: {
            background: 'rgba(99, 102, 241, 0.2)',
            color: '#e8e8f0',
            border: '2px solid #6366f1',
            borderRadius: '8px',
            padding: '10px 20px',
            fontWeight: 'bold',
            boxShadow: '0 0 15px rgba(99, 102, 241, 0.3)'
        }
    },
    {
        id: 'context',
        type: 'default',
        position: { x: 100, y: 250 },
        data: { label: 'Context Builder\n(System Prompt & Skills)' },
        style: {
            background: 'rgba(22, 33, 62, 0.9)',
            color: '#a0a0c0',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: '8px'
        }
    },
    {
        id: 'memory',
        type: 'default',
        position: { x: 400, y: 250 },
        data: { label: 'Session Manager\n& Memory Store' },
        style: {
            background: 'rgba(22, 33, 62, 0.9)',
            color: '#a0a0c0',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: '8px'
        }
    },
    {
        id: 'llm',
        type: 'default',
        position: { x: 250, y: 350 },
        data: { label: 'LLM Provider\n(Reasoning Engine)' },
        style: {
            background: 'rgba(16, 185, 129, 0.15)',
            color: '#e8e8f0',
            border: '2px solid #10b981',
            borderRadius: '8px',
            padding: '15px 30px',
            fontWeight: 'bold',
            boxShadow: '0 0 15px rgba(16, 185, 129, 0.2)'
        }
    },
    {
        id: 'tools',
        type: 'default',
        position: { x: 100, y: 450 },
        data: { label: 'Tool Registry\n(Native Tools)' },
        style: {
            background: 'rgba(245, 158, 11, 0.15)',
            color: '#e8e8f0',
            border: '1px solid #f59e0b',
            borderRadius: '8px'
        }
    },
    {
        id: 'mcp',
        type: 'default',
        position: { x: 400, y: 450 },
        data: { label: 'MCP Servers\n(External Capabilities)' },
        style: {
            background: 'rgba(245, 158, 11, 0.15)',
            color: '#e8e8f0',
            border: '1px solid #f59e0b',
            borderRadius: '8px'
        }
    },
    {
        id: 'out',
        type: 'default',
        position: { x: 250, y: 550 },
        data: { label: 'Message Bus\n(Outbound)' },
        style: {
            background: 'rgba(22, 33, 62, 0.9)',
            color: '#e8e8f0',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: '8px',
            padding: '10px 20px',
            fontWeight: 'bold',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.4)'
        }
    },
];

const initialEdges = [
    { id: 'e-bus-loop', source: 'bus', target: 'loop', animated: true, markerEnd: { type: MarkerType.ArrowClosed, color: '#6366f1' }, style: { stroke: '#6366f1', strokeWidth: 2 } },
    { id: 'e-loop-context', source: 'loop', target: 'context', animated: false, markerEnd: { type: MarkerType.ArrowClosed, color: '#a0a0c0' }, style: { stroke: '#a0a0c0' } },
    { id: 'e-loop-memory', source: 'loop', target: 'memory', animated: false, markerEnd: { type: MarkerType.ArrowClosed, color: '#a0a0c0' }, style: { stroke: '#a0a0c0' } },
    { id: 'e-loop-llm', source: 'loop', target: 'llm', animated: true, label: 'Prompt', markerEnd: { type: MarkerType.ArrowClosed, color: '#10b981' }, style: { stroke: '#10b981', strokeWidth: 2 } },

    // ReAct Tool Calls
    { id: 'e-llm-tools', source: 'llm', target: 'tools', animated: true, label: 'Tool Call', markerEnd: { type: MarkerType.ArrowClosed, color: '#f59e0b' }, style: { stroke: '#f59e0b' } },
    { id: 'e-llm-mcp', source: 'llm', target: 'mcp', animated: true, label: 'MCP JSON-RPC', markerEnd: { type: MarkerType.ArrowClosed, color: '#f59e0b' }, style: { stroke: '#f59e0b' } },

    // ReAct Return
    { id: 'e-tools-loop', source: 'tools', target: 'loop', animated: true, label: 'Result', markerEnd: { type: MarkerType.ArrowClosed, color: '#6366f1' }, style: { stroke: '#6366f1' } },
    { id: 'e-mcp-loop', source: 'mcp', target: 'loop', animated: true, label: 'Result', markerEnd: { type: MarkerType.ArrowClosed, color: '#6366f1' }, style: { stroke: '#6366f1' } },

    // Final Output
    { id: 'e-llm-out', source: 'llm', target: 'out', animated: true, label: 'Final Text', markerEnd: { type: MarkerType.ArrowClosed, color: '#e8e8f0' }, style: { stroke: '#e8e8f0', strokeWidth: 2 } },
];

export default function AgentLoopFlow() {
    const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

    const onConnect = useCallback(
        (params) => setEdges((eds) => addEdge({ ...params, animated: true }, eds)),
        [setEdges],
    );

    return (
        <div className="react-flow-container">
            <div className="react-flow-header">
                <h2>Nanobot AgentLoop Architecture</h2>
                <p>Interactive graph showing the continuous Pull Architecture, Context Building, and Tool/MCP executions.</p>
            </div>

            <div className="react-flow-wrapper">
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onConnect={onConnect}
                    fitView
                    colorMode="dark"
                >
                    <Controls />
                    <MiniMap
                        nodeColor={(node) => {
                            if (node.id === 'loop') return '#6366f1';
                            if (node.id === 'llm') return '#10b981';
                            if (node.id === 'tools' || node.id === 'mcp') return '#f59e0b';
                            return '#1a1a2e';
                        }}
                        style={{ backgroundColor: '#0f0f1a' }}
                        maskColor="rgba(0, 0, 0, 0.4)"
                    />
                    <Background variant="dots" gap={16} size={1} color="rgba(255,255,255,0.1)" />
                </ReactFlow>
            </div>
        </div>
    );
}
