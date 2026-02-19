import { useState, useEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import mermaid from 'mermaid'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import Breadcrumb from '../components/Breadcrumb'
import GiscusComments from '../components/GiscusComments'

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

export default function BlogPost() {
    const { slug } = useParams()
    const [post, setPost] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetch(`/api/blogs/${slug}`)
            .then(r => { if (!r.ok) throw new Error('Not found'); return r.json() })
            .then(data => { setPost(data); setLoading(false) })
            .catch(() => setLoading(false))
    }, [slug])

    if (loading) return <div className="loading">Loading post</div>
    if (!post) return <div className="container" style={{ padding: '4rem 2rem', textAlign: 'center' }}>
        <h2>Post not found</h2>
        <p style={{ color: 'var(--text-muted)' }}>The blog post "{slug}" doesn't exist.</p>
    </div>

    return (
        <div className="blog-post">
            <Breadcrumb items={[
                { label: 'Home', to: '/' },
                { label: 'Blogs', to: '/blogs' },
                { label: post.title }
            ]} />

            <h1>{post.title}</h1>
            <div className="post-meta">
                📅 {post.date}
                {post.tags?.length > 0 && (
                    <span> · {post.tags.map(t => <span key={t} className="tag" style={{ marginLeft: '0.5rem' }}>{t}</span>)}</span>
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
                    {post.raw}
                </ReactMarkdown>
            </div>

            <GiscusComments term={slug} />
        </div>
    )
}
