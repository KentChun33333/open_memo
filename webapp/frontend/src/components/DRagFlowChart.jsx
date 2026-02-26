import React, { useMemo } from 'react';
import { ReactFlow, Controls, Background, MarkerType } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

// Academic/Paper pastel color palette (matching the reference image vibe)
const colors = {
    groupOpt: '#fff9c4',   // Pastel yellow/cream
    borderOpt: '#fbc02d',  
    groupRag: '#e0f7fa',   // Pastel cyan/blue
    borderRag: '#4dd0e1',
    groupEvo: '#e8f5e9',   // Pastel green
    borderEvo: '#81c784',
    nodeBg: '#ffffff',
    text: '#333333',
    edge: '#607d8b'
};

const scholarlyNode = {
    padding: '10px 14px',
    borderRadius: '8px',
    fontSize: '13px',
    fontFamily: 'system-ui, -apple-system, sans-serif',
    fontWeight: '500',
    background: colors.nodeBg,
    color: colors.text,
    border: '1px solid #78909c',
    boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
    width: '180px',
    textAlign: 'center',
};

const groupStyle = (bgColor, borderColor, w, h) => ({
    width: w,
    height: h,
    backgroundColor: bgColor,
    border: `2px solid ${borderColor}`,
    borderRadius: '12px',
    zIndex: -1,
});

// Title placed cleanly in top-left
const GroupLabel = ({ title, subtitle }) => (
    <div style={{ position: 'absolute', top: 12, left: 16, textAlign: 'left' }}>
        <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#2c3e50' }}>{title}</div>
        {subtitle && <div style={{ fontSize: '12px', color: '#546e7a', fontStyle: 'italic', marginTop: '2px' }}>{subtitle}</div>}
    </div>
);

const initialNodes = [
    // --- MAIN VISUAL REGIONS (GROUPS) ---
    {
        id: 'g_init',
        position: { x: 20, y: 120 },
        data: { label: <GroupLabel title="D-RAG Formalization" subtitle="Information Extraction & Routing" /> },
        style: groupStyle(colors.groupOpt, colors.borderOpt, 420, 320),
        type: 'default',
        draggable: false, selectable: false
    },
    {
        id: 'g_evo',
        position: { x: 460, y: 120 },
        data: { label: <GroupLabel title="Meta-Dimensions Evolution" subtitle="Asynchronous Schema Mutation" /> },
        style: groupStyle(colors.groupEvo, colors.borderEvo, 440, 320),
        type: 'default',
        draggable: false, selectable: false
    },
    {
        id: 'g_select',
        position: { x: 20, y: 460 },
        data: { label: <GroupLabel title="Deterministic Selection" subtitle="Hybrid Subspace Retrieval" /> },
        style: groupStyle(colors.groupRag, colors.borderRag, 880, 280),
        type: 'default',
        draggable: false, selectable: false
    },

    // --- ACTORS & TOP LEVEL ---
    { 
        id: 'task', 
        position: { x: 130, y: 10 }, 
        data: { label: <div style={{ fontSize: '14px' }}><div style={{ background: '#ffebee', color: '#c62828', borderRadius: '12px', padding: '2px 8px', display: 'inline-block', marginBottom: '6px', border: '1px solid #ef9a9a' }}><b>Task 🎯</b></div><br/>User App Query</div> }, 
        style: { ...scholarlyNode, borderRadius: '12px', width: '200px', background: '#fffafa' },
    },

    // --- D-RAG FORMALIZATION (Yellow Group) ---
    { 
        id: 'opt_log', 
        position: { x: 50, y: 200 }, 
        data: { label: <div>📝 <b>Query Formulation</b><br/><span style={{fontSize: 10, color: '#666'}}>Assemble raw string q</span></div> }, 
        style: scholarlyNode
    },
    { 
        id: 'sym_ext', 
        position: { x: 240, y: 200 }, 
        data: { label: <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}><img src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🧠</text></svg>" width="32" height="32" /><b style={{ marginTop: '4px' }}>Symbolic Target Extractor</b></div> }, 
        style: scholarlyNode
    },
    { 
        id: 'rag_gate', 
        position: { x: 240, y: 340 }, 
        data: { label: <div>🛑 <b>Deterministic Gate</b><br/><span style={{fontSize: 10, color: '#666'}}>Indicator Function I(q)</span></div> }, 
        style: { ...scholarlyNode, border: '2px solid #ef5350', background: '#ffebee' }
    },
    { 
        id: 'agent', 
        position: { x: 50, y: 340 }, 
        data: { label: <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}><div style={{ fontSize: '24px', marginRight: '8px' }}>🤖</div><div><b>Target LLM:</b><br/><span style={{fontSize: 10, color: '#666'}}>Agentic Controller</span></div></div> }, 
        style: { ...scholarlyNode, border: '2px solid #5c6bc0', background: '#e8eaf6' }
    },

    // --- EVOLUTION (Green Group) ---
    { 
        id: 'ddl_mab', 
        position: { x: 480, y: 200 }, 
        data: { label: <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}><div style={{ fontSize: '24px' }}>🎰</div><b style={{ marginTop: '4px' }}>Information Gain<br/>(Entropy ROI)</b></div> }, 
        style: scholarlyNode
    },
    { 
        id: 'ddl_brains', 
        position: { x: 690, y: 200 }, 
        data: { label: <div style={{ border: '1px dashed #9e9e9e', padding: '8px', borderRadius: '4px' }}><b>LLM Dimension Pool</b><br/><div style={{fontSize: '20px', marginTop: '4px'}}>🗣️ 💭</div></div> }, 
        style: { ...scholarlyNode, border: '1px dashed #78909c' }
    },
    { 
        id: 'evo_table', 
        position: { x: 480, y: 320 }, 
        data: { label: (
            <div style={{ textAlign: 'left', fontSize: '11px' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fff' }}>
                    <tbody>
                        <tr style={{ borderBottom: '1px solid #ccc' }}>
                            <td style={{ padding: '4px', fontWeight: 'bold' }}>Dimensions:</td>
                            <td style={{ padding: '4px', color: '#1976d2' }}>Proj</td>
                            <td style={{ padding: '4px', color: '#1976d2' }}>Owner</td>
                            <td style={{ padding: '4px', background: '#e3f2fd', border: '1px solid #2196f3', borderRadius: '4px', color: '#1565c0', fontWeight: 'bold' }}>Ticker</td>
                        </tr>
                        <tr>
                            <td style={{ padding: '4px', fontWeight: 'bold' }}>Entropy ROI:</td>
                            <td style={{ padding: '4px' }}>[0.2]</td>
                            <td style={{ padding: '4px' }}>[0.1]</td>
                            <td style={{ padding: '4px', color: '#388e3c', fontWeight: 'bold' }}>[0.9]</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        )
        },
        style: { ...scholarlyNode, width: '390px', padding: '10px' }
    },

    // --- RETRIEVAL & STORAGE (Blue Group) ---
    {
        id: 'db_table',
        position: { x: 500, y: 550 },
        data: { label: (
            <div style={{ textAlign: 'left', fontSize: '12px' }}>
                <div style={{ fontWeight: 'bold', marginBottom: '6px', textAlign: 'center' }}>🗄️ LanceDB: Workspace Memory</div>
                <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fff' }}>
                    <thead>
                        <tr style={{ borderBottom: '1px solid #ccc', background: '#f5f5f5' }}>
                            <th style={{ padding: '4px' }}>Vector</th>
                            <th style={{ padding: '4px' }}>Text</th>
                            <th style={{ padding: '4px', color: '#d32f2f' }}>D_Project</th>
                            <th style={{ padding: '4px', color: '#d32f2f' }}>D_Ticker</th>
                        </tr>
                    </thead>
                    <tbody style={{ textAlign: 'center', color: '#555' }}>
                        <tr style={{ borderBottom: '1px solid #eee' }}>
                            <td style={{ padding: '2px' }}>[0.1, ..]</td>
                            <td style={{ padding: '2px' }}>"Notes"</td>
                            <td style={{ padding: '2px', color: '#d32f2f' }}>Alpha</td>
                            <td style={{ padding: '2px', color: '#d32f2f', fontWeight: 'bold' }}>LEU</td>
                        </tr>
                        <tr>
                            <td style={{ padding: '2px' }}>[0.9, ..]</td>
                            <td style={{ padding: '2px' }}>"Call"</td>
                            <td style={{ padding: '2px', color: '#d32f2f' }}>Beta</td>
                            <td style={{ padding: '2px', color: '#d32f2f' }}>NVDA</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        )
        },
        style: { ...scholarlyNode, width: '360px', padding: '12px', border: '2px solid #ffb74d' }
    },
    { 
        id: 'eval_responses', 
        position: { x: 50, y: 530 }, 
        data: { label: (
            <div style={{ textAlign: 'left', fontSize: '11px', display: 'flex', flexDirection: 'column', gap: '12px', padding: '16px 0' }}>
                <div style={{ background: '#fff', border: '1px solid #ccc', padding: '12px', borderRadius: '4px', position: 'relative' }}>
                    <div style={{ background: '#ffb74d', color: '#fff', padding: '2px 8px', borderRadius: '12px', display: 'inline-block', position: 'absolute', top: '-10px', left: '10px', fontWeight: 'bold' }}>Scoring</div>
                    <div style={{ position: 'absolute', top: '-10px', right: '10px', background: '#fff', border: '1px solid #ccc', padding: '2px 4px', fontSize: '10px' }}>Rank 12</div>
                    <div>Distractor Context v_d<br/>"Call with client about Beta."</div>
                </div>
                <div style={{ background: '#fff', border: '2px solid #4ade80', padding: '12px', borderRadius: '4px', position: 'relative', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
                    <div style={{ background: '#ffb74d', color: '#fff', padding: '2px 8px', borderRadius: '12px', display: 'inline-block', position: 'absolute', top: '-10px', left: '10px', fontWeight: 'bold' }}>Scoring</div>
                    <div style={{ position: 'absolute', top: '-10px', right: '10px', background: '#ecfdf5', border: '1px solid #10b981', padding: '2px 4px', fontSize: '10px', color: '#047857', fontWeight: 'bold' }}>Rank 1</div>
                    <div>Primary Context v_d<br/>"Nuclear notes for LEU..."</div>
                </div>
            </div>
        ) }, 
        style: { ...scholarlyNode, width: '320px', background: 'transparent', border: 'none', boxShadow: 'none' }
    },
];

const edgeOpts = { 
    type: 'smoothstep', 
    markerEnd: { type: MarkerType.ArrowClosed, color: colors.edge },
    style: { strokeWidth: 2, stroke: colors.edge } 
};

// Removed sourceHandle / targetHandle from edges so they correctly render with default nodes.
const initialEdges = [
    // Task entry point
    { id: 'e-task-ext', source: 'task', target: 'sym_ext', ...edgeOpts, label: 'Incoming Context', labelBgPadding: [6, 4], labelBgStyle: { fill: '#fff', color: '#666', border: '1px solid #eee' } },

    // D-RAG Process (Left -> Down)
    { id: 'e-task-opt', source: 'task', target: 'opt_log', ...edgeOpts },
    { id: 'e-opt-sym', source: 'opt_log', target: 'sym_ext', ...edgeOpts },
    { id: 'e-sym-gate', source: 'sym_ext', target: 'rag_gate', ...edgeOpts },
    { id: 'e-gate-db', source: 'rag_gate', target: 'db_table', type: 'smoothstep', ...edgeOpts, style: { strokeWidth: 2, stroke: '#ef5350' }, markerEnd: { type: MarkerType.ArrowClosed, color: '#ef5350' }, label: 'Subspace Partition\n(D_Ticker=LEU)', labelBgPadding: [6, 4], labelBgStyle: { fill: '#ffebee', opacity: 0.9, stroke: '#ef9a9a' }, labelStyle: { fill: '#c62828', fontWeight: 'bold', fontSize: 11} },
    
    // Agent Connection
    { id: 'e-opt-agt', source: 'opt_log', target: 'agent', ...edgeOpts },
    { id: 'e-gate-agt', source: 'rag_gate', target: 'agent', ...edgeOpts },

    // Evolution Process (Top Right)
    { id: 'e-sym-mab', source: 'sym_ext', target: 'ddl_mab', ...edgeOpts, type: 'step' },
    { id: 'e-mab-evo', source: 'ddl_mab', target: 'evo_table', ...edgeOpts },
    { id: 'e-brains-mab', source: 'ddl_brains', target: 'ddl_mab', ...edgeOpts, label: 'Evolve schema dims', labelBgPadding: [4, 4], labelBgStyle: { fill: '#fff' }, labelStyle: { fontSize: 11 } },
    { id: 'e-evo-brains', source: 'evo_table', target: 'ddl_brains', type: 'smoothstep', ...edgeOpts, label: 'Mutate pools', labelBgPadding: [4, 4], labelBgStyle: { fill: '#fff' }, labelStyle: { fontSize: 11 } },
    { id: 'e-evo-db', source: 'evo_table', target: 'db_table', type: 'smoothstep', ...edgeOpts, style: { strokeWidth: 2, stroke: '#388e3c', strokeDasharray: '5,5' }, markerEnd: { type: MarkerType.ArrowClosed, color: '#388e3c' }, label: 'Update DB Schema', labelBgPadding: [6, 4], labelBgStyle: { fill: '#e8f5e9', opacity: 0.9, stroke: '#a5d6a7' }, labelStyle: { fill: '#2e7d32', fontWeight: 'bold', fontSize: 11} },

    // Return to Agent (Bottom)
    { id: 'e-db-eval', source: 'db_table', target: 'eval_responses', type: 'smoothstep', ...edgeOpts, label: 'Sim(v_q, v_d)', labelBgPadding: [6, 4], labelBgStyle: { fill: '#f8fafc', stroke: '#cbd5e1' }, labelStyle: { fontSize: 11, fontWeight: 'bold', fill: '#475569' } },
    { id: 'e-eval-agt', source: 'eval_responses', target: 'agent', type: 'smoothstep', ...edgeOpts, style: { strokeWidth: 2, stroke: '#85144b' }, markerEnd: { type: MarkerType.ArrowClosed, color: '#85144b' }, label: 'Inject R(q,d)', labelBgPadding: [6, 4], labelBgStyle: { fill: '#fff', stroke: '#fbcfe8' }, labelStyle: { fill: '#d53f8c', fontWeight: 'bold', fontSize: 11 } },
];

export default function DRagFlowChart() {
    return (
        <div style={{ width: '100%', height: '800px', border: '1px solid #cfd8dc', borderRadius: '8px', margin: '40px 0', background: '#fafafa', position: 'relative', overflow: 'hidden' }}>
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
