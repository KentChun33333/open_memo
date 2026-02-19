import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Breadcrumb from '../components/Breadcrumb'

export default function BlogList() {
    const [blogs, setBlogs] = useState([])
    const [loading, setLoading] = useState(true)
    const [filter, setFilter] = useState('')

    useEffect(() => {
        fetch('/api/blogs')
            .then(r => r.json())
            .then(data => { setBlogs(data); setLoading(false) })
            .catch(() => setLoading(false))
    }, [])

    const allTags = [...new Set(blogs.flatMap(b => b.tags || []))]
    const filtered = filter
        ? blogs.filter(b => b.tags?.includes(filter))
        : blogs

    if (loading) return <div className="loading">Loading blogs</div>

    return (
        <div className="container">
            <Breadcrumb items={[
                { label: 'Home', to: '/' },
                { label: 'Blogs' }
            ]} />

            <div className="section-header">
                <h2>📝 All Blog Posts</h2>
                <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                    {filtered.length} post{filtered.length !== 1 ? 's' : ''}
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
                {filtered.map(blog => (
                    <Link key={blog.slug} to={`/blogs/${blog.slug}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                        <div className="card">
                            <h3>{blog.title}</h3>
                            <p>{blog.excerpt}</p>
                            <div className="meta">
                                <span>📅 {blog.date}</span>
                                {blog.tags?.map(tag => (
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
