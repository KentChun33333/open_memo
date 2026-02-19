import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Breadcrumb from '../components/Breadcrumb'

export default function NoteList() {
    const [notes, setNotes] = useState([])
    const [loading, setLoading] = useState(true)
    const [filter, setFilter] = useState('')

    useEffect(() => {
        fetch('/api/notes')
            .then(r => r.json())
            .then(data => { setNotes(data); setLoading(false) })
            .catch(() => setLoading(false))
    }, [])

    const allTags = [...new Set(notes.flatMap(n => n.tags || []))]
    const filtered = filter
        ? notes.filter(n => n.tags?.includes(filter))
        : notes

    if (loading) return <div className="loading">Loading notes</div>

    return (
        <div className="container">
            <Breadcrumb items={[
                { label: 'Home', to: '/' },
                { label: 'Notes' }
            ]} />

            <div className="section-header">
                <h2>📝 All Notes</h2>
                <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                    {filtered.length} note{filtered.length !== 1 ? 's' : ''}
                </span>
            </div>

            {/* Tag filters */}
            {allTags.length > 0 && (
                <div style={{ marginBottom: 'var(--space-xl)', display: 'flex', gap: 'var(--space-sm)', flexWrap: 'wrap' }}>
                    <button
                        className={`tag ${!filter ? 'active' : ''}`}
                        onClick={() => setFilter('')}
                        style={{
                            cursor: 'pointer', border: 'none',
                            background: !filter ? 'var(--accent)' : 'rgba(99, 102, 241, 0.15)',
                            color: !filter ? 'white' : 'var(--accent)',
                        }}
                    >
                        All
                    </button>
                    {allTags.map(tag => (
                        <button
                            key={tag}
                            className="tag"
                            onClick={() => setFilter(tag === filter ? '' : tag)}
                            style={{
                                cursor: 'pointer', border: 'none',
                                background: tag === filter ? 'var(--accent)' : 'rgba(99, 102, 241, 0.15)',
                                color: tag === filter ? 'white' : 'var(--accent)',
                            }}
                        >
                            {tag}
                        </button>
                    ))}
                </div>
            )}

            <div className="card-grid">
                {filtered.map(note => (
                    <Link key={note.slug} to={`/notes/${note.slug}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                        <div className="card">
                            <h3>{note.title}</h3>
                            <p>{note.excerpt}</p>
                            <div className="meta">
                                <span>📅 {note.date?.trim()}</span>
                                {note.tags?.map(tag => (
                                    <span key={tag} className="tag">{tag}</span>
                                ))}
                            </div>
                        </div>
                    </Link>
                ))}
            </div>
        </div>
    )
}
