import { useState, useEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import mermaid from 'mermaid'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import Breadcrumb from '../components/Breadcrumb'
import GiscusComments from '../components/GiscusComments'
import logo from '../assets/logo.gif'

// Mermaid renderer component
function Mermaid({ chart }) {
    const ref = useRef(null)

    useEffect(() => {
        if (ref.current && chart) {
            mermaid.initialize({
                startOnLoad: true,
                theme: 'dark',
                securityLevel: 'loose',
                fontFamily: 'var(--font-family)',
            })
            mermaid.contentLoaded()
        }
    }, [chart])

    return (
        <div className="mermaid-container">
            <div className="mermaid" ref={ref}>
                {chart}
            </div>
        </div>
    )
}

export default function NotePost() {
    const { slug } = useParams()
    const [note, setNote] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetch(`/api/notes/${slug}`)
            .then(r => { if (!r.ok) throw new Error('Not found'); return r.json() })
            .then(data => { setNote(data); setLoading(false) })
            .catch(() => setLoading(false))
    }, [slug])

    if (loading) return <div className="loading">Loading note</div>
    if (!note) return <div className="container" style={{ padding: '4rem 2rem', textAlign: 'center' }}>
        <h2>Note not found</h2>
        <p style={{ color: 'var(--text-muted)' }}>The note "{slug}" doesn't exist.</p>
    </div>

    return (
        <div className="blog-post">
            <Breadcrumb items={[
                { label: 'Home', to: '/' },
                { label: 'Notes', to: '/notes' },
                { label: note.title }
            ]} />

            <h1 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <img src={logo} alt="avatar" style={{ width: '40px', height: '40px', borderRadius: '50%', objectFit: 'cover', flexShrink: 0, border: '2px solid var(--accent)' }} />
                {note.title}
            </h1>
            <div className="post-meta">
                📅 {note.date}
                {note.tags?.length > 0 && (
                    <span> · {note.tags.map(t => <span key={t} className="tag" style={{ marginLeft: '0.5rem' }}>{t}</span>)}</span>
                )}
            </div>

            <div className="blog-content">
                <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                        code({ node, inline, className, children, ...props }) {
                            const match = /language-(\w+)/.exec(className || '')
                            const lang = match ? match[1] : ''

                            if (!inline && lang === 'mermaid') {
                                return <Mermaid chart={String(children).replace(/\n$/, '')} />
                            }

                            return !inline && match ? (
                                <SyntaxHighlighter
                                    style={oneDark}
                                    language={lang}
                                    PreTag="div"
                                    {...props}
                                >
                                    {String(children).replace(/\n$/, '')}
                                </SyntaxHighlighter>
                            ) : (
                                <code className={className} {...props}>
                                    {children}
                                </code>
                            )
                        }
                    }}
                >
                    {note.raw}
                </ReactMarkdown>
            </div>

            <GiscusComments term={`note-${slug}`} />
        </div>
    )
}
