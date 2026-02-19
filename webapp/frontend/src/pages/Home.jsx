import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

export default function Home() {
    const [blogs, setBlogs] = useState([])
    const [mindmaps, setMindmaps] = useState([])

    useEffect(() => {
        fetch('/api/blogs').then(r => r.json()).then(setBlogs).catch(() => { })
        fetch('/api/mindmaps').then(r => r.json()).then(setMindmaps).catch(() => { })
    }, [])

    return (
        <div className="container">
            <section className="hero">
                <h1>OpenMemo</h1>
                <p>
                    A knowledge garden for learning memos, technical blogs, and interactive mind maps
                    — powered by Markdown and Git.
                </p>
                <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                    <Link to="/blogs" className="btn btn-primary" style={{ width: 'auto' }}>
                        📖 Browse Blogs
                    </Link>
                </div>
            </section>

            {/* Recent Blogs */}
            {blogs.length > 0 && (
                <section style={{ marginBottom: 'var(--space-3xl)' }}>
                    <div className="section-header">
                        <h2>📝 Recent Blogs</h2>
                        <Link to="/blogs">View all →</Link>
                    </div>
                    <div className="card-grid">
                        {blogs.slice(0, 3).map(blog => (
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
                </section>
            )}

            {/* Mind Maps */}
            {mindmaps.length > 0 && (
                <section style={{ marginBottom: 'var(--space-3xl)' }}>
                    <div className="section-header">
                        <h2>🧠 Mind Maps</h2>
                    </div>
                    <div className="card-grid">
                        {mindmaps.map(mm => (
                            <Link key={mm.id} to={`/mindmaps/${mm.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                                <div className="card">
                                    <h3>{mm.title}</h3>
                                    <p>{mm.description}</p>
                                    <div className="meta">
                                        <span>🔗 {mm.node_count} nodes</span>
                                    </div>
                                </div>
                            </Link>
                        ))}
                    </div>
                </section>
            )}
        </div>
    )
}
