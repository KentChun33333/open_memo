import React from 'react';
import { ReactFlow, Controls, Background, MarkerType } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const colors = {
    bgOpt: '#e8f5e9',       // Light green background
    borderOpt: '#4caf50',   // Green border
    bgRag: '#e3f2fd',       // Light blue background
    borderRag: '#2196f3',   // Blue border
    bgEvo: '#fffbeb',       // Light yellow
    borderEvo: '#fcd34d',   // Yellow border
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
        id: 'g_past',
        position: { x: 20, y: 120 },
        data: { label: <GroupLabel title="T_record < T_promotion (Legacy)" bg={colors.borderRag} color="#1565c0" /> },
        style: groupStyle(colors.bgRag, colors.borderRag, 260, 220),
        type: 'default',
        draggable: false, selectable: false
    },
    {
        id: 'g_present',
        position: { x: 320, y: 120 },
        data: { label: <GroupLabel title="T_watermark to T_promotion" bg={colors.borderEvo} color="#d97706" /> },
        style: groupStyle(colors.bgEvo, colors.borderEvo, 340, 220),
        type: 'default',
        draggable: false, selectable: false
    },
    {
        id: 'g_future',
        position: { x: 700, y: 120 },
        data: { label: <GroupLabel title="Continuous Processing" bg={colors.borderOpt} color="#388e3c" /> },
        style: groupStyle(colors.bgOpt, colors.borderOpt, 300, 220),
        type: 'default',
        draggable: false, selectable: false
    },

    // --- TIMELINE AXIS ---
    { 
        id: 'timeline_start', 
        position: { x: -20, y: 380 }, 
        data: { label: 'Past (Database Creation)' }, 
        style: { border: 'none', background: 'none', fontSize: '10px', color: '#94a3b8', fontWeight: 'bold' } 
    },
    { 
        id: 'timeline_end', 
        position: { x: 960, y: 380 }, 
        data: { label: 'Future (New Documents)' }, 
        style: { border: 'none', background: 'none', fontSize: '10px', color: '#94a3b8', fontWeight: 'bold' } 
    },

    // --- NODES ---
    { 
        id: 'db_old', 
        position: { x: 60, y: 170 }, 
        data: { label: (
            <div style={{ ...scholarlyNode, width: '180px' }}>
                <div style={headerStyle('#64748b')}>Legacy Records</div>
                <div style={bodyStyle}>
                   <div style={{ fontSize: '11px' }}>Dim X: NULL / ""</div>
                </div>
            </div>
        ) }, 
        style: { ...scholarlyNode, border: 'none', background: 'none', boxShadow: 'none' }
    },
    { 
        id: 'daemon', 
        position: { x: 400, y: 170 }, 
        data: { label: (
            <div style={{ ...scholarlyNode, width: '180px', border: '2px solid #f59e0b' }}>
                <div style={headerStyle('#f59e0b')}>Async Backfill Daemon</div>
                <div style={bodyStyle}>
                   <div style={{ fontSize: '24px' }}>⚙️</div>
                   <div style={{ fontSize: '10px', fontWeight: 'bold', color: '#b45309' }}>LLM Batch Processing</div>
                </div>
            </div>
        ) }, 
        style: { ...scholarlyNode, border: 'none', background: 'none', boxShadow: 'none' }
    },
    { 
        id: 'db_new', 
        position: { x: 760, y: 170 }, 
        data: { label: (
            <div style={{ ...scholarlyNode, width: '180px' }}>
                <div style={headerStyle('#10b981')}>D-RAG Validated DB</div>
                <div style={bodyStyle}>
                   <div style={{ fontSize: '11px', color: '#047857', fontWeight: 'bold' }}>Dim X: "Populated"</div>
                </div>
            </div>
        ) }, 
        style: { ...scholarlyNode, border: 'none', background: 'none', boxShadow: 'none' }
    },

    // --- MILESTONES / EVENTS ---
    { 
        id: 't_watermark', 
        position: { x: 350, y: 400 }, 
        data: { label: (
            <div style={{ padding: '4px', background: '#fef3c7', border: '1px solid #d97706', borderRadius: '4px', fontSize: '10px', color: '#92400e', fontWeight: 'bold' }}>
                T_watermark (Polling)
            </div>
        ) }, 
        style: { border: 'none', background: 'none', boxShadow: 'none' }
    },
    { 
        id: 't_promotion', 
        position: { x: 620, y: 400 }, 
        data: { label: (
             <div style={{ padding: '4px', background: '#fee2e2', border: '1px solid #dc2626', borderRadius: '4px', fontSize: '10px', color: '#991b1b', fontWeight: 'bold' }}>
                T_promotion (Schema Evolves)
            </div>
        ) }, 
        style: { border: 'none', background: 'none', boxShadow: 'none' }
    },
];

const edgeOpts = { 
    type: 'smoothstep', 
    markerEnd: { type: MarkerType.ArrowClosed, color: colors.edge },
    style: { strokeWidth: 2, stroke: colors.edge } 
};

const initialEdges = [
    // Timeline backbone
    { id: 'e-time', source: 'timeline_start', target: 'timeline_end', type: 'straight', style: { strokeWidth: 4, stroke: '#cbd5e1', strokeDasharray: '4,4' } },
    
    // Process flow
    { id: 'e-db-daemon', source: 'db_old', target: 'daemon', ...edgeOpts, label: 'Yield Untagged Records', labelBgPadding: [6, 4], labelBgStyle: { fill: '#fff' } },
    { id: 'e-daemon-new', source: 'daemon', target: 'db_new', ...edgeOpts, label: 'table.update()', labelBgPadding: [6, 4], labelBgStyle: { fill: '#fff' }, style: { strokeWidth: 2, stroke: '#10b981' }, markerEnd: { type: MarkerType.ArrowClosed, color: '#10b981' } },
];

export default function SchemaBackfillFlowChart() {
    return (
        <div style={{ width: '100%', height: '500px', border: '1px solid #e2e8f0', borderRadius: '12px', margin: '40px 0', background: '#fafafa', position: 'relative', overflow: 'hidden', fontFamily: 'system-ui, sans-serif' }}>
             <div style={{ position: 'absolute', top: '16px', right: '16px', zIndex: 10, background: 'white', padding: '8px 16px', borderRadius: '24px', border: '2px solid #cbd5e1', boxShadow: '0 4px 6px rgba(0,0,0,0.05)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{ width: '24px', height: '24px', background: '#f59e0b', borderRadius: '4px' }}></div>
                <span style={{ fontWeight: 'bold', fontSize: '16px', color: '#334155' }}>Asynchronous Schema Remediation</span>
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
                <Background color="#cbd5e1" gap={16} />
            </ReactFlow>
        </div>
    );
}
