import React from 'react';
import { ReactFlow, Controls, Background, MarkerType } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

// Styling to match the "ByteByteGo" / "LightMem" references
// Clean, rounded, separated header sections, and solid backgrounds.

const colors = {
    bgOpt: '#e8f5e9',       // Light green background
    borderOpt: '#4caf50',   // Green border
    bgRag: '#e3f2fd',       // Light blue background
    borderRag: '#2196f3',   // Blue border
    bgAI: '#f3e5f5',        // Light purple background
    borderAI: '#9c27b0',    // Purple border
    nodeBg: '#ffffff',
    text: '#1e293b',
    edge: '#64748b'
};

const scholarlyNode = {
    padding: '0px',
    borderRadius: '12px',
    fontSize: '12px',
    fontFamily: 'Inter, system-ui, sans-serif',
    background: colors.nodeBg,
    color: colors.text,
    border: '2px solid #cbd5e1',
    boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)',
    width: '180px',
    textAlign: 'center',
    overflow: 'hidden'
};

const headerStyle = (bgColor) => ({
    backgroundColor: bgColor,
    color: 'white',
    padding: '6px 10px',
    fontWeight: 'bold',
    fontSize: '13px',
    borderBottom: '1px solid rgba(0,0,0,0.1)'
});

const bodyStyle = {
    padding: '12px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '6px'
};

const groupStyle = (bgColor, borderColor, w, h) => ({
    width: w,
    height: h,
    backgroundColor: bgColor,
    border: `2px solid ${borderColor}`,
    borderRadius: '16px',
    zIndex: -1,
});

const GroupLabel = ({ title, bg, color }) => (
    <div style={{ position: 'absolute', top: 0, left: 16, transform: 'translateY(-50%)' }}>
        <div style={{ 
            fontSize: '14px', 
            fontWeight: 'bold', 
            color: 'white', 
            backgroundColor: bg,
            padding: '4px 16px',
            borderRadius: '20px',
            border: `2px solid ${color}`,
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>{title}</div>
    </div>
);

const initialNodes = [
    // --- MAIN VISUAL REGIONS (GROUPS) ---
    {
        id: 'g_init',
        position: { x: 20, y: 120 },
        data: { label: <GroupLabel title="D-RAG Formalization" bg={colors.borderOpt} color="#388e3c" /> },
        style: groupStyle(colors.bgOpt, colors.borderOpt, 420, 320),
        type: 'default',
        draggable: false, selectable: false
    },
    {
        id: 'g_evo',
        position: { x: 460, y: 120 },
        data: { label: <GroupLabel title="Autonomous DDL Evolution" bg={colors.borderEvo || '#f59e0b'} color="#d97706" /> },
        style: groupStyle('#fffbeb', '#fcd34d', 440, 320),
        type: 'default',
        draggable: false, selectable: false
    },
    {
        id: 'g_select',
        position: { x: 20, y: 480 },
        data: { label: <GroupLabel title="Hybrid Subspace Retrieval" bg={colors.borderRag} color="#1565c0" /> },
        style: groupStyle(colors.bgRag, colors.borderRag, 880, 260),
        type: 'default',
        draggable: false, selectable: false
    },

    // --- ACTORS & TOP LEVEL ---
    { 
        id: 'task', 
        position: { x: 130, y: 20 }, 
        data: { label: (
            <div style={{ ...scholarlyNode, width: '200px' }}>
                <div style={headerStyle('#ef4444')}>User Query</div>
                <div style={{...bodyStyle, fontWeight: '500'}}>
                    "Find Kent's AI notes"
                </div>
            </div>
        ) }, 
        style: { ...scholarlyNode, border: 'none', background: 'none', boxShadow: 'none' },
    },

    // --- D-RAG FORMALIZATION (Green Group) ---
    { 
        id: 'opt_log', 
        position: { x: 50, y: 160 }, 
        data: { label: (
            <div style={{ ...scholarlyNode }}>
                <div style={headerStyle('#4caf50')}>Query Formulation</div>
                <div style={bodyStyle}>Assemble raw string <b>q</b></div>
            </div>
        ) }, 
        style: { ...scholarlyNode, border: 'none', background: 'none', boxShadow: 'none' }
    },
    { 
        id: 'sym_ext', 
        position: { x: 240, y: 160 }, 
        data: { label: (
            <div style={{ ...scholarlyNode }}>
                <div style={headerStyle('#4caf50')}>Symbolic Extractor</div>
                <div style={bodyStyle}>
                    <div style={{ fontSize: '24px' }}>🧠</div>
                    <div style={{ fontFamily: 'monospace', fontSize: '10px', background: '#f1f5f9', padding: '4px', borderRadius: '4px' }}>
                        {`{owner: 'kent', topic: 'AI'}`}
                    </div>
                </div>
            </div>
        ) }, 
        style: { ...scholarlyNode, border: 'none', background: 'none', boxShadow: 'none' }
    },
    { 
        id: 'rag_gate', 
        position: { x: 240, y: 300 }, 
        data: { label: (
            <div style={{ ...scholarlyNode }}>
                <div style={headerStyle('#ef4444')}>Deterministic Gate</div>
                <div style={bodyStyle}>
                   <div style={{ fontSize: '20px' }}>🛑</div>
                   <div style={{ fontSize: '10px' }}>Indicator Function <b>I(q)</b></div>
                </div>
            </div>
        ) }, 
        style: { ...scholarlyNode, border: 'none', background: 'none', boxShadow: 'none' }
    },
    { 
        id: 'agent', 
        position: { x: 50, y: 300 }, 
        data: { label: (
            <div style={{ ...scholarlyNode }}>
                <div style={headerStyle('#6366f1')}>Target LLM</div>
                <div style={bodyStyle}>
                   <div style={{ fontSize: '24px' }}>🤖</div>
                   <div style={{ fontSize: '11px', fontWeight: 'bold' }}>Agentic Controller</div>
                </div>
            </div>
        ) }, 
        style: { ...scholarlyNode, border: 'none', background: 'none', boxShadow: 'none' }
    },

    // --- EVOLUTION (Yellow Group) ---
    { 
        id: 'ddl_mab', 
        position: { x: 480, y: 160 }, 
        data: { label: (
             <div style={{ ...scholarlyNode }}>
                <div style={headerStyle('#f59e0b')}>Information Gain</div>
                <div style={bodyStyle}>
                   <div style={{ fontSize: '24px' }}>📊</div>
                   <div style={{ fontSize: '11px' }}>Track Entropy ROI</div>
                </div>
            </div>
        ) }, 
        style: { ...scholarlyNode, border: 'none', background: 'none', boxShadow: 'none' }
    },
    { 
        id: 'ddl_brains', 
        position: { x: 690, y: 160 }, 
        data: { label: (
            <div style={{ ...scholarlyNode, border: '2px dashed #94a3b8' }}>
                <div style={headerStyle('#94a3b8')}>LLM Dimension Pool</div>
                <div style={bodyStyle}>
                   <div style={{ fontSize: '24px' }}>💭</div>
                </div>
            </div>
        ) }, 
        style: { ...scholarlyNode, border: 'none', background: 'none', boxShadow: 'none' }
    },
    { 
        id: 'evo_table', 
        position: { x: 480, y: 280 }, 
        data: { label: (
            <div style={{ ...scholarlyNode, width: '390px' }}>
                <div style={headerStyle('#fca5a5')}>Schema Evolution</div>
                <div style={{ padding: '8px', fontSize: '11px' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'center' }}>
                        <tbody>
                            <tr style={{ borderBottom: '1px solid #e2e8f0', background: '#f8fafc' }}>
                                <td style={{ padding: '6px', fontWeight: 'bold', textAlign: 'left' }}>Dimensions:</td>
                                <td style={{ padding: '6px', color: '#64748b' }}>Project</td>
                                <td style={{ padding: '6px', color: '#64748b' }}>Owner</td>
                                <td style={{ padding: '6px', background: '#dcfce7', border: '1px solid #86efac', borderRadius: '4px', color: '#166534', fontWeight: 'bold' }}>Topic</td>
                            </tr>
                            <tr>
                                <td style={{ padding: '6px', fontWeight: 'bold', textAlign: 'left' }}>Entropy ROI:</td>
                                <td style={{ padding: '6px' }}>[0.2]</td>
                                <td style={{ padding: '6px' }}>[0.1]</td>
                                <td style={{ padding: '6px', color: '#166534', fontWeight: 'bold' }}>[0.85]</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        ) },
        style: { ...scholarlyNode, border: 'none', background: 'none', boxShadow: 'none' }
    },

    // --- RETRIEVAL & STORAGE (Blue Group) ---
    {
        id: 'db_table',
        position: { x: 500, y: 530 },
        data: { label: (
            <div style={{ ...scholarlyNode, width: '360px' }}>
                <div style={headerStyle('#3b82f6')}>🗄️ LanceDB Vector Store</div>
                <div style={{ padding: '8px', fontSize: '11px' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                            <tr style={{ borderBottom: '2px solid #cbd5e1', background: '#f1f5f9' }}>
                                <th style={{ padding: '6px' }}>Vector</th>
                                <th style={{ padding: '6px' }}>Text</th>
                                <th style={{ padding: '6px', color: '#1d4ed8' }}>Owner</th>
                                <th style={{ padding: '6px', color: '#1d4ed8' }}>Topic</th>
                            </tr>
                        </thead>
                        <tbody style={{ textAlign: 'center' }}>
                            <tr style={{ borderBottom: '1px solid #e2e8f0' }}>
                                <td style={{ padding: '6px' }}>[0.1, ..]</td>
                                <td style={{ padding: '6px' }}>"Notes"</td>
                                <td style={{ padding: '6px', color: '#1d4ed8' }}>Kent</td>
                                <td style={{ padding: '6px', color: '#1d4ed8', fontWeight: 'bold' }}>AI</td>
                            </tr>
                            <tr>
                                <td style={{ padding: '6px' }}>[0.9, ..]</td>
                                <td style={{ padding: '6px' }}>"Call"</td>
                                <td style={{ padding: '6px', color: '#64748b' }}>Admin</td>
                                <td style={{ padding: '6px', color: '#64748b' }}>Sales</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        ) },
        style: { ...scholarlyNode, border: 'none', background: 'none', boxShadow: 'none' }
    },
    { 
        id: 'eval_responses', 
        position: { x: 50, y: 510 }, 
        data: { label: (
            <div style={{ textAlign: 'left', fontSize: '11px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <div style={{ ...scholarlyNode, width: '320px' }}>
                    <div style={{ ...headerStyle('#cbd5e1'), color: '#475569', display: 'flex', justifyContent: 'space-between' }}>
                        <span>Distractor Context v_d</span>
                        <span style={{ background: 'white', padding: '2px 6px', borderRadius: '12px' }}>Rank 12</span>
                    </div>
                    <div style={{ padding: '12px', color: '#64748b' }}>
                        "Call with admin about sales..."
                    </div>
                </div>

                <div style={{ ...scholarlyNode, width: '320px', border: '2px solid #22c55e' }}>
                     <div style={{ ...headerStyle('#22c55e'), display: 'flex', justifyContent: 'space-between' }}>
                        <span>Primary Context v_d</span>
                        <span style={{ background: '#dcfce7', color: '#15803d', padding: '2px 6px', borderRadius: '12px' }}>Rank 1</span>
                    </div>
                    <div style={{ padding: '12px', fontWeight: 'bold' }}>
                        "Kent's AI notes from Friday..."
                    </div>
                </div>
            </div>
        ) }, 
        style: { ...scholarlyNode, background: 'transparent', border: 'none', boxShadow: 'none', width: '320px' }
    },
];

const edgeOpts = { 
    type: 'default', // Straight edges look cleaner for structured technical diagrams
    markerEnd: { type: MarkerType.ArrowClosed, color: colors.edge },
    style: { strokeWidth: 2, stroke: colors.edge } 
};

const initialEdges = [
    // Task entry point
    { id: 'e-task-ext', source: 'task', target: 'sym_ext', ...edgeOpts, label: 'Incoming Context', labelBgPadding: [6, 4], labelBgStyle: { fill: '#fff', color: '#333' } },

    // D-RAG Process (Left -> Down)
    { id: 'e-task-opt', source: 'task', target: 'opt_log', ...edgeOpts },
    { id: 'e-opt-sym', source: 'opt_log', target: 'sym_ext', ...edgeOpts },
    { id: 'e-sym-gate', source: 'sym_ext', target: 'rag_gate', ...edgeOpts },
    { id: 'e-gate-db', source: 'rag_gate', target: 'db_table', ...edgeOpts, style: { strokeWidth: 2, stroke: '#3b82f6' }, markerEnd: { type: MarkerType.ArrowClosed, color: '#3b82f6' }, label: 'Subspace M\n(WHERE topic=AI)', labelBgPadding: [6, 4], labelBgStyle: { fill: '#eff6ff', opacity: 0.9, stroke: '#bfdbfe' }, labelStyle: { fill: '#1d4ed8', fontWeight: 'bold', fontSize: 11} },
    
    // Agent Connection
    { id: 'e-opt-agt', source: 'opt_log', target: 'agent', ...edgeOpts },
    { id: 'e-gate-agt', source: 'rag_gate', target: 'agent', ...edgeOpts },

    // Evolution Process (Top Right)
    { id: 'e-sym-mab', source: 'sym_ext', target: 'ddl_mab', ...edgeOpts },
    { id: 'e-mab-evo', source: 'ddl_mab', target: 'evo_table', ...edgeOpts },
    { id: 'e-brains-mab', source: 'ddl_brains', target: 'ddl_mab', ...edgeOpts, label: 'Candidate Dims', labelBgPadding: [4, 4], labelBgStyle: { fill: '#fff' }, labelStyle: { fontSize: 11 } },
    { id: 'e-evo-brains', source: 'evo_table', target: 'ddl_brains', ...edgeOpts },
    { id: 'e-evo-db', source: 'evo_table', target: 'db_table', ...edgeOpts, style: { strokeWidth: 2, stroke: '#eab308', strokeDasharray: '5,5' }, markerEnd: { type: MarkerType.ArrowClosed, color: '#eab308' }, label: 'Update DB Schema', labelBgPadding: [6, 4], labelBgStyle: { fill: '#fefce8', opacity: 0.9, stroke: '#fef08a' }, labelStyle: { fill: '#a16207', fontWeight: 'bold', fontSize: 11} },

    // Return to Agent (Bottom)
    { id: 'e-db-eval', source: 'db_table', target: 'eval_responses', ...edgeOpts, label: 'Hybrid Scoring', labelBgPadding: [6, 4], labelBgStyle: { fill: '#fff' }, labelStyle: { fontSize: 11, fontWeight: 'bold', fill: '#475569' } },
    { id: 'e-eval-agt', source: 'eval_responses', target: 'agent', ...edgeOpts, style: { strokeWidth: 2, stroke: '#22c55e' }, markerEnd: { type: MarkerType.ArrowClosed, color: '#22c55e' }, label: 'Inject R(q,d)', labelBgPadding: [6, 4], labelBgStyle: { fill: '#dcfce7', stroke: '#86efac' }, labelStyle: { fill: '#15803d', fontWeight: 'bold', fontSize: 11 } },
];

export default function DRagFlowChart() {
    return (
        <div style={{ width: '100%', height: '800px', border: '1px solid #e2e8f0', borderRadius: '12px', margin: '40px 0', background: '#fafafa', position: 'relative', overflow: 'hidden', fontFamily: 'system-ui, sans-serif' }}>
             {/* Note banner reflecting the ByteByteGo aesthetic title style */}
             <div style={{ position: 'absolute', top: '16px', right: '16px', zIndex: 10, background: 'white', padding: '8px 16px', borderRadius: '24px', border: '2px solid #cbd5e1', boxShadow: '0 4px 6px rgba(0,0,0,0.05)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{ width: '24px', height: '24px', background: '#10b981', borderRadius: '4px' }}></div>
                <span style={{ fontWeight: 'bold', fontSize: '16px', color: '#334155' }}>Nanobot Architecture</span>
            </div>
            
            <ReactFlow
                nodes={initialNodes}
                edges={initialEdges}
                fitView
                fitViewOptions={{ padding: 0.1 }}
                minZoom={0.1}
                attributionPosition="bottom-right"
            >
                <Controls />
            </ReactFlow>
        </div>
    );
}

