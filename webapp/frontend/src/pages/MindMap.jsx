import { useState, useEffect, useCallback, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
    ReactFlow,
    Background,
    Controls,
    useNodesState,
    useEdgesState,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import Breadcrumb from '../components/Breadcrumb'

/* ---- Custom Node ---- */
function MindMapNode({ data }) {
    const borderColor = data.style?.color || 'var(--accent)'
    return (
        <div
            className="mindmap-node"
            style={{ borderLeftColor: borderColor, borderLeftWidth: 3 }}
        >
            <div className="node-label">{data.label}</div>
            {data.description && <div className="node-desc">{data.description}</div>}
            {data.targetFile && (
                <div style={{ marginTop: 4, fontSize: '0.7rem', color: 'var(--accent)' }}>
                    🔗 Click to open
                </div>
            )}
        </div>
    )
}

const nodeTypes = { mindmap: MindMapNode }

/* ---- Layout: simple tree positioning ---- */
function layoutNodes(nodes, edges) {
    const children = {}
    const nodeMap = {}
    nodes.forEach(n => { nodeMap[n.id] = n; children[n.id] = [] })
    edges.forEach(e => {
        if (children[e.source]) children[e.source].push(e.target)
    })

    // Find roots (nodes that are not a target of any edge)
    const targets = new Set(edges.map(e => e.target))
    const roots = nodes.filter(n => !targets.has(n.id))
    if (roots.length === 0 && nodes.length > 0) roots.push(nodes[0])

    const positioned = new Set()
    const result = []

    function layout(nodeId, x, y, level) {
        if (positioned.has(nodeId)) return { width: 0 }
        positioned.add(nodeId)

        const node = nodeMap[nodeId]
        if (!node) return { width: 0 }

        const kids = children[nodeId] || []
        const childWidth = 220
        const childHeight = 120

        if (kids.length === 0) {
            result.push({ ...node, position: { x, y } })
            return { width: childWidth }
        }

        let totalWidth = 0
        const childInfos = []
        for (const kid of kids) {
            const info = layout(kid, x + totalWidth, y + childHeight, level + 1)
            childInfos.push({ ...info, startX: x + totalWidth })
            totalWidth += info.width + 30
        }
        totalWidth -= 30

        const myX = childInfos.length > 0
            ? childInfos[0].startX + (totalWidth - childWidth) / 2
            : x

        result.push({ ...node, position: { x: myX, y } })
        return { width: Math.max(totalWidth, childWidth) }
    }

    let xOffset = 0
    for (const root of roots) {
        const info = layout(root.id, xOffset, 0, 0)
        xOffset += info.width + 60
    }

    return result
}

/* ---- Flatten recursive JSON → flat nodes + edges ---- */
function flattenMindMap(data) {
    const nodes = []
    const edges = []

    function walk(node) {
        nodes.push({
            id: node.id,
            type: 'mindmap',
            data: {
                label: node.label,
                description: node.description || '',
                targetFile: node.target_file || node.targetFile,
                style: node.style || {},
            },
            position: { x: 0, y: 0 },
        })

        if (node.children) {
            node.children.forEach(child => {
                edges.push({
                    id: `${node.id}-${child.id}`,
                    source: node.id,
                    target: child.id,
                    animated: !!child.targetFile || !!child.target_file,
                })
                walk(child)
            })
        }
    }

    if (data.nodes) data.nodes.forEach(walk)

    // Add explicit edges from the data
    if (data.edges) {
        data.edges.forEach(e => {
            const id = `edge-${e.source}-${e.target}`
            if (!edges.find(ex => ex.source === e.source && ex.target === e.target)) {
                edges.push({
                    id,
                    source: e.source,
                    target: e.target,
                    label: e.label || '',
                    animated: true,
                    style: { stroke: 'var(--accent)' },
                })
            }
        })
    }

    return { nodes, edges }
}

/* ---- Page Component ---- */
export default function MindMapPage() {
    const { id } = useParams()
    const navigate = useNavigate()
    const [mapData, setMapData] = useState(null)
    const [loading, setLoading] = useState(true)
    const [history, setHistory] = useState([])
    const [panel, setPanel] = useState(null)

    const [nodes, setNodes, onNodesChange] = useNodesState([])
    const [edges, setEdges, onEdgesChange] = useEdgesState([])

    const loadMap = useCallback((mapId) => {
        setLoading(true)
        fetch(`/api/mindmaps/${mapId}`)
            .then(r => { if (!r.ok) throw new Error(); return r.json() })
            .then(data => {
                setMapData(data)
                const { nodes: flatNodes, edges: flatEdges } = flattenMindMap(data)
                const positioned = layoutNodes(flatNodes, flatEdges)
                setNodes(positioned)
                setEdges(flatEdges)
                setLoading(false)
            })
            .catch(() => setLoading(false))
    }, [setNodes, setEdges])

    useEffect(() => {
        loadMap(id)
        setHistory([{ id, title: id }])
    }, [id, loadMap])

    const onNodeClick = useCallback((_, node) => {
        const targetFile = node.data.targetFile
        if (!targetFile) {
            // Show description panel
            setPanel({
                title: node.data.label,
                description: node.data.description,
            })
            return
        }

        // Navigate to linked mind map
        if (targetFile.endsWith('.json')) {
            const newId = targetFile.replace('.json', '')
            setHistory(prev => [...prev, { id: newId, title: node.data.label }])
            navigate(`/mindmaps/${newId}`)
        }
    }, [navigate])

    const breadcrumbItems = useMemo(() => [
        { label: 'Home', to: '/' },
        ...history.map((h, i) =>
            i < history.length - 1
                ? { label: h.title, to: `/mindmaps/${h.id}` }
                : { label: mapData?.title || h.title }
        ),
    ], [history, mapData])

    if (loading) return <div className="loading">Loading mind map</div>
    if (!mapData) return <div className="container" style={{ padding: '4rem 2rem', textAlign: 'center' }}>
        <h2>Mind map not found</h2>
    </div>

    return (
        <>
            <Breadcrumb items={breadcrumbItems} />
            <div className="mindmap-container">
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onNodeClick={onNodeClick}
                    nodeTypes={nodeTypes}
                    fitView
                    fitViewOptions={{ padding: 0.2 }}
                    style={{ background: 'var(--bg-primary)' }}
                >
                    <Background color="var(--border)" gap={20} />
                    <Controls />
                </ReactFlow>

                {/* Side panel for node details */}
                <div className={`mindmap-panel ${panel ? 'open' : ''}`}>
                    {panel && (
                        <>
                            <button className="close-btn" onClick={() => setPanel(null)}>×</button>
                            <h3>{panel.title}</h3>
                            <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                                {panel.description}
                            </p>
                        </>
                    )}
                </div>
            </div>
        </>
    )
}
