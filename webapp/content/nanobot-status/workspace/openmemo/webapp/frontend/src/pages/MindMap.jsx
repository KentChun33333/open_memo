import { useState, useEffect, useCallback, useMemo, useRef } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { Markmap } from 'markmap-view'
import { Transformer } from 'markmap-lib'
import Breadcrumb from '../components/Breadcrumb'

const transformer = new Transformer()

/* ---- Convert our JSON tree → Markdown string for Markmap ---- */
function jsonToMarkdown(node, depth = 0) {
    const indent = '  '.repeat(depth)
    const prefix = depth === 0 ? '# ' : '- '
    let md = ''

    // Build the label — add emoji for nodes with links
    let label = node.label
    if (node.targetFile) {
        label = `🔗 ${label}`
    }

    md += `${indent}${prefix}${label}\n`

    // Add description as sub-item if exists (only for deeper nodes)
    if (node.description && depth > 0) {
        md += `${indent}  - _${node.description}_\n`
    }

    // Recurse into children
    if (node.children) {
        node.children.forEach(child => {
            md += jsonToMarkdown(child, depth + 1)
        })
    }

    return md
}

/* ---- Build a lookup map: label → node data (for click handling) ---- */
function buildNodeLookup(node, lookup = {}) {
    lookup[node.label] = node
    if (node.children) {
        node.children.forEach(child => buildNodeLookup(child, lookup))
    }
    return lookup
}

/* ---- Page Component ---- */
export default function MindMapPage() {
    const { id } = useParams()
    const navigate = useNavigate()
    const svgRef = useRef(null)
    const markmapRef = useRef(null)
    const [mapData, setMapData] = useState(null)
    const [loading, setLoading] = useState(true)
    const [history, setHistory] = useState([])
    const [selectedNode, setSelectedNode] = useState(null)
    const nodeLookupRef = useRef({})

    // Load mind map data
    const loadMap = useCallback((mapId) => {
        setLoading(true)
        setSelectedNode(null)
        fetch(`/api/mindmaps/${mapId}`)
            .then(r => { if (!r.ok) throw new Error(); return r.json() })
            .then(data => {
                setMapData(data)
                setLoading(false)
            })
            .catch(() => setLoading(false))
    }, [])

    useEffect(() => {
        loadMap(id)
        setHistory([{ id, title: id }])
    }, [id, loadMap])

    // Render markmap when data changes
    useEffect(() => {
        if (!mapData || !svgRef.current) return

        // Convert JSON → Markdown → Markmap tree
        const rootNode = mapData.nodes?.[0]
        if (!rootNode) return

        // Build lookup for click handling
        nodeLookupRef.current = buildNodeLookup(rootNode)

        const markdown = jsonToMarkdown(rootNode)
        const { root } = transformer.transform(markdown)

        // Clear previous SVG content
        svgRef.current.innerHTML = ''

        // Create markmap instance
        const mm = Markmap.create(svgRef.current, {
            colorFreezeLevel: 2,
            duration: 500,
            maxWidth: 300,
            paddingX: 16,
            spacingHorizontal: 80,
            spacingVertical: 10,
            autoFit: true,
            zoom: true,
            pan: true,
            initialExpandLevel: 3,
        }, root)

        markmapRef.current = mm

        // Fit to view after a brief delay
        setTimeout(() => mm.fit(), 100)

        // Add click handler for navigation
        svgRef.current.addEventListener('click', (e) => {
            const textEl = e.target.closest('text, foreignObject')
            if (!textEl) return

            const content = textEl.textContent?.trim()
            if (!content) return

            // Remove emoji prefix for lookup
            const cleanLabel = content.replace(/^🔗\s*/, '')
            const nodeData = nodeLookupRef.current[cleanLabel]

            if (nodeData?.targetFile) {
                const newId = nodeData.targetFile.replace('.json', '')
                setHistory(prev => [...prev, { id: newId, title: cleanLabel }])
                navigate(`/mindmaps/${newId}`)
            } else if (nodeData) {
                setSelectedNode(nodeData)
            }
        })

        return () => {
            mm.destroy()
        }
    }, [mapData, navigate])

    // Handle window resize
    useEffect(() => {
        const handleResize = () => {
            if (markmapRef.current) {
                markmapRef.current.fit()
            }
        }
        window.addEventListener('resize', handleResize)
        return () => window.removeEventListener('resize', handleResize)
    }, [])

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
                {/* Markmap info bar */}
                <div className="mindmap-toolbar">
                    <h2 className="mindmap-title">
                        {mapData.title}
                        {mapData.date && (
                            <span style={{ fontSize: '1rem', fontWeight: 'normal', color: 'var(--text-muted)', marginLeft: '1rem' }}>
                                📅 {mapData.date}
                            </span>
                        )}
                    </h2>
                    <div className="mindmap-actions">
                        <button
                            className="btn btn-sm"
                            onClick={() => markmapRef.current?.fit()}
                            title="Fit to view"
                        >
                            🔍 Fit
                        </button>
                        <button
                            className="btn btn-sm"
                            onClick={() => {
                                if (markmapRef.current) {
                                    markmapRef.current.rescale(1.3)
                                }
                            }}
                            title="Zoom in"
                        >
                            ➕
                        </button>
                        <button
                            className="btn btn-sm"
                            onClick={() => {
                                if (markmapRef.current) {
                                    markmapRef.current.rescale(0.7)
                                }
                            }}
                            title="Zoom out"
                        >
                            ➖
                        </button>
                    </div>
                </div>

                {/* Markmap SVG container */}
                <svg
                    ref={svgRef}
                    className="mindmap-svg"
                />

                {/* Linked maps legend */}
                {mapData.nodes?.[0]?.children?.some(c => c.targetFile) && (
                    <div className="mindmap-legend">
                        <span className="legend-icon">🔗</span>
                        <span>Click linked nodes to drill down</span>
                    </div>
                )}

                {/* Selected node detail panel */}
                <div className={`mindmap-panel ${selectedNode ? 'open' : ''}`}>
                    {selectedNode && (
                        <>
                            <button className="close-btn" onClick={() => setSelectedNode(null)}>×</button>
                            <h3>{selectedNode.label}</h3>
                            <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6, marginTop: '0.5rem' }}>
                                {selectedNode.description || 'No description available.'}
                            </p>
                            {selectedNode.targetFile && (
                                <Link
                                    to={`/mindmaps/${selectedNode.targetFile.replace('.json', '')}`}
                                    className="btn btn-primary"
                                    style={{ marginTop: '1rem', display: 'inline-flex' }}
                                    onClick={() => {
                                        const newId = selectedNode.targetFile.replace('.json', '')
                                        setHistory(prev => [...prev, { id: newId, title: selectedNode.label }])
                                    }}
                                >
                                    Open linked map →
                                </Link>
                            )}
                            {selectedNode.children && (
                                <div style={{ marginTop: '1rem' }}>
                                    <h4 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                                        Children ({selectedNode.children.length})
                                    </h4>
                                    {selectedNode.children.map(c => (
                                        <div key={c.id} className="panel-child-item">
                                            <strong>{c.label}</strong>
                                            {c.description && <span> — {c.description}</span>}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </>
                    )}
                </div>
            </div>
        </>
    )
}
