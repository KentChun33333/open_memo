import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Breadcrumb from '../components/Breadcrumb'

export default function MindMapList() {
    const [mindmaps, setMindmaps] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetch('/api/mindmaps')
            .then(r => r.json())
            .then(data => { setMindmaps(data); setLoading(false) })
            .catch(() => setLoading(false))
    }, [])

    if (loading) return <div className="loading">Loading mind maps…</div>

    return (
        <div className="container">
            <Breadcrumb items={[
                { label: 'Home', to: '/' },
                { label: 'Mind Maps' }
            ]} />

            <div className="section-header">
                <h2>🧠 Mind Maps</h2>
                <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                    {mindmaps.length} map{mindmaps.length !== 1 ? 's' : ''}
                </span>
            </div>

            <div className="card-grid">
                {mindmaps.map(mm => (
                    <Link key={mm.id} to={`/mindmaps/${mm.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                        <div className="card">
                            <h3>{mm.title}</h3>
                            <p>{mm.description}</p>
                            <div className="meta">
                                <span>📅 {mm.date || 'Unknown date'}</span>
                                <span style={{ marginLeft: '1rem' }}>🔗 {mm.node_count} nodes</span>
                            </div>
                        </div>
                    </Link>
                ))}
            </div>

            {mindmaps.length === 0 && (
                <div style={{ textAlign: 'center', padding: 'var(--space-3xl)', color: 'var(--text-muted)' }}>
                    <p>No mind maps found.</p>
                </div>
            )}
        </div>
    )
}
