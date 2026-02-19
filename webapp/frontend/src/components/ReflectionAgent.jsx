import { useState, useEffect } from 'react'

export default function ReflectionAgent() {
    const [reflections, setReflections] = useState(null)
    const [loading, setLoading] = useState(true)
    const [typing, setTyping] = useState(true)

    useEffect(() => {
        fetch('/nanobot-status/reflections.json')
            .then(r => r.json())
            .then(data => {
                setReflections(data)
                setLoading(false)
                // Simulate thinking time for "Wow" factor
                setTimeout(() => setTyping(false), 1500)
            })
            .catch(() => setLoading(false))
    }, [])

    if (loading) return null

    return (
        <div className="reflection-card glassmorphism">
            <div className="reflection-header">
                <div className="reflection-avatar">✨</div>
                <div>
                    <h3 className="reflection-title">Active Consciousness</h3>
                    <p className="reflection-subtitle">Proactive insights from your Nanobot Agent</p>
                </div>
                <div className={`reflection-status ${typing ? 'pulse' : ''}`}>
                    {typing ? 'Thinking...' : 'Active'}
                </div>
            </div>

            <div className="reflection-body">
                {typing ? (
                    <div className="typing-indicator">
                        <span></span><span></span><span></span>
                    </div>
                ) : (
                    <>
                        <div className="reflection-summary">
                            <p>{reflections?.daily_summary}</p>
                        </div>

                        <div className="reflection-section">
                            <h4>🎯 Proactive Questions</h4>
                            <ul className="reflection-list">
                                {reflections?.proactive_questions?.map((q, i) => (
                                    <li key={i} className="reflection-item question">
                                        <a
                                            href={`https://t.me/Clawdbot?text=${encodeURIComponent(q)}`}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="reflection-link"
                                        >
                                            <span className="icon">❓</span> {q}
                                        </a>
                                    </li>
                                ))}
                            </ul>
                        </div>

                        <div className="reflection-section">
                            <h4>🚀 Recommended Actions</h4>
                            <div className="action-item-grid">
                                {reflections?.action_items?.map((a, i) => (
                                    <a
                                        key={i}
                                        href={`https://t.me/Clawdbot?text=${encodeURIComponent(a)}`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="action-pill clickable"
                                    >
                                        <span className="icon">⚡</span> {a}
                                    </a>
                                ))}
                            </div>
                        </div>
                    </>
                )}
            </div>

            <div className="reflection-footer">
                Last updated: {new Date(reflections?.last_updated).toLocaleString()}
            </div>
        </div>
    )
}
