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

const mdxModules = import.meta.glob('../../../content/blogs/*.mdx')

export default function BlogPost() {
    const { slug } = useParams()
    const [post, setPost] = useState(null)
    const [MdxComponent, setMdxComponent] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        setLoading(true)

        // 1. Fetch metadata from API to ensure it exists and get title/tags
        fetch(`/api/blogs/${slug}`)
            .then(r => { if (!r.ok) throw new Error('Not found'); return r.json() })
            .then(data => { setPost(data) })
            .catch(() => { }) // We'll handle 'not found' below if neither API nor MDX exists

        // 2. Try loading the local MDX file dynamically
        const mdxPath = `../../../content/blogs/${slug}.mdx`
        if (mdxModules[mdxPath]) {
            mdxModules[mdxPath]()
                .then(mod => {
                    setMdxComponent(() => mod.default)
                    setLoading(false)
                })
                .catch(err => {
                    console.error("MDX load error:", err)
                    setLoading(false)
                })
        } else {
            // If no MDX found, we'll just wait for the API fetch to complete (which is fast)
            // But we should stop the loader
            setTimeout(() => setLoading(false), 500)
        }
    }, [slug])

    if (loading) return <div className="loading">Loading post</div>
    if (!post && !MdxComponent) return <div className="container" style={{ padding: '4rem 2rem', textAlign: 'center' }}>
        <h2>Post not found</h2>
        <p style={{ color: 'var(--text-muted)' }}>The blog post "{slug}" doesn't exist.</p>
    </div>

    return (
        <div className="blog-post">
            <Breadcrumb items={[
                { label: 'Home', to: '/' },
                { label: 'Blogs', to: '/blogs' },
                { label: post?.title || slug }
            ]} />

            {post && (
                <>
                    <h1 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <img src={logo} alt="avatar" style={{ width: '40px', height: '40px', borderRadius: '50%' }} />
                        {post.title}
                    </h1>
                    <div className="post-meta">
                        📅 {post.date}
                        {post.tags?.length > 0 && (
                            <span> · {post.tags.map(t => <span key={t} className="tag" style={{ marginLeft: '0.5rem' }}>{t}</span>)}</span>
                        )}
                    </div>
                </>
            )}

            <div className="blog-content">
                {MdxComponent ? (
                    <div className="mdx-content">
                        <MdxComponent />
                    </div>
                ) : (
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
                        {post?.raw || ''}
                    </ReactMarkdown>
                )}
            </div>

            <GiscusComments term={slug} />
        </div>
    )
}
