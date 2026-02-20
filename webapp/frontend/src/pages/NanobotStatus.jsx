import { useState, useEffect } from 'react'

/* ──────── helpers ──────── */

function cronToHuman(expr) {
    if (!expr) return 'N/A'
    const parts = expr.split(' ')
    if (parts.length !== 5) return expr
    const [min, hour, , ,] = parts
    return `Daily at ${hour.padStart(2, '0')}:${min.padStart(2, '0')}`
}

function formatTimestamp(ms) {
    if (!ms) return '—'
    return new Date(ms).toLocaleString()
}

/* ──────── status badge ──────── */

function StatusBadge({ enabled }) {
    return (
        <span className={`nanobot-badge ${enabled ? 'badge-active' : 'badge-inactive'}`}>
            <span className="badge-dot" />
            {enabled ? 'Active' : 'Disabled'}
        </span>
    )
}

/* ──────── cron jobs widget ──────── */

function CronJobsWidget({ jobs }) {
    if (!jobs.length) {
        return (
            <div className="nanobot-widget">
                <h3 className="nanobot-widget-title">⏰ Cron Jobs</h3>
                <div className="nanobot-empty">No cron jobs configured</div>
            </div>
        )
    }
    return (
        <div className="nanobot-widget">
            <div className="nanobot-widget-header">
                <h3 className="nanobot-widget-title">⏰ Cron Jobs</h3>
                <span className="nanobot-widget-count">{jobs.length} job{jobs.length !== 1 ? 's' : ''}</span>
            </div>
            <div className="nanobot-table-wrap">
                <table className="nanobot-table">
                    <thead>
                        <tr>
                            <th>Status</th>
                            <th>Job Name</th>
                            <th>Schedule</th>
                            <th>Timezone</th>
                            <th>Channel</th>
                            <th>Next Run</th>
                        </tr>
                    </thead>
                    <tbody>
                        {jobs.map(job => (
                            <tr key={job.id}>
                                <td><StatusBadge enabled={job.enabled} /></td>
                                <td className="nanobot-job-name">{job.name}</td>
                                <td>
                                    <span className="nanobot-cron-expr">{job.schedule?.expr}</span>
                                    <span className="nanobot-cron-human">{cronToHuman(job.schedule?.expr)}</span>
                                </td>
                                <td>{job.schedule?.tz || '—'}</td>
                                <td>
                                    <span className="nanobot-channel">
                                        {job.payload?.channel === 'telegram' ? '📱' : '💬'} {job.payload?.channel || '—'}
                                    </span>
                                </td>
                                <td className="nanobot-next-run">{formatTimestamp(job.state?.nextRunAtMs)}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}

/* ──────── memory section card ──────── */

function MemorySection({ title, items, icon, accentColor }) {
    if (!items || !items.length) return null
    return (
        <div className="nanobot-memory-section" style={{ '--section-accent': accentColor }}>
            <h4 className="nanobot-memory-section-title">
                <span>{icon}</span> {title}
            </h4>
            <ul className="nanobot-memory-list">
                {items.map((item, i) => (
                    <li key={i}>{item}</li>
                ))}
            </ul>
        </div>
    )
}

/* ──────── memory widget ──────── */

function MemoryWidget({ memory }) {
    const sections = [
        { key: 'Key Facts', title: 'Key Facts', icon: '🔑', color: '#6366f1' },
        { key: 'Recent Session Goals', title: 'Recent Goals', icon: '🎯', color: '#10b981' },
        { key: 'Long Term Goals', title: 'Long Term Goals', icon: '🚀', color: '#f59e0b' },
        { key: 'Known Issues', title: 'Known Issues', icon: '⚠️', color: '#ef4444' },
    ]

    const hasContent = sections.some(s => memory[s.key]?.length > 0)

    return (
        <div className="nanobot-widget">
            <h3 className="nanobot-widget-title">🧠 Agent Memory</h3>
            {!hasContent ? (
                <div className="nanobot-empty">No memory data available</div>
            ) : (
                <div className="nanobot-memory-grid">
                    {sections.map(s => (
                        <MemorySection
                            key={s.key}
                            title={s.title}
                            items={memory[s.key]}
                            icon={s.icon}
                            accentColor={s.color}
                        />
                    ))}
                </div>
            )}
        </div>
    )
}

/* ──────── parse memory.md ──────── */

function parseMemoryMd(text) {
    const sections = {}
    let current = null
    for (const line of text.split('\n')) {
        const heading = line.match(/^##\s+(.+)$/)
        if (heading) {
            current = heading[1].trim()
            sections[current] = []
            continue
        }
        if (current) {
            const bullet = line.trim().match(/^[-*]\s+(.+)$/)
            if (bullet) sections[current].push(bullet[1].trim())
        }
    }
    return sections
}

/* ──────── page ──────── */

export default function NanobotStatus() {
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        const token = localStorage.getItem('token');
        const headers = {};
        if (token) headers['Authorization'] = `Bearer ${token}`;

        Promise.all([
            fetch('/api/nanobot-status/cron/jobs.json', { headers }).then(r => {
                if (!r.ok) throw new Error(`cron/jobs: HTTP ${r.status}`)
                return r.json()
            }),
            fetch('/api/nanobot-status/workspace/memory/MEMORY.md', { headers }).then(r => {
                if (!r.ok) throw new Error(`workspace/memory: HTTP ${r.status}`)
                return r.text()
            }),
        ])
            .then(([cronData, memoryText]) => {
                setData({
                    cron_jobs: cronData.jobs || [],
                    memory: parseMemoryMd(memoryText),
                })
            })
            .catch(e => setError(e.message))
            .finally(() => setLoading(false))
    }, [])

    if (loading) return <div className="loading">Loading nanobot status…</div>
    if (error) return <div className="nanobot-error">Failed to load status: {error}</div>

    const { cron_jobs = [], memory = {} } = data || {}

    return (
        <div className="dashboard nanobot-dashboard">
            {/* Header */}
            <div className="dashboard-header">
                <div className="nanobot-header-row">
                    <span className="nanobot-avatar">🐈</span>
                    <div>
                        <h1 className="dashboard-title">Nanobot Status</h1>
                        <p className="dashboard-subtitle">
                            Agent health, scheduled jobs, and persistent memory
                        </p>
                    </div>
                </div>
            </div>

            {/* Stat Cards */}
            <div className="stat-grid nanobot-stat-grid">
                <div className="stat-card" style={{ '--stat-accent': '#6366f1' }}>
                    <div className="stat-icon">⏰</div>
                    <div className="stat-info">
                        <span className="stat-value">{cron_jobs.length}</span>
                        <span className="stat-label">Cron Jobs</span>
                        <span className="stat-sub">{cron_jobs.filter(j => j.enabled).length} active</span>
                    </div>
                </div>
                <div className="stat-card" style={{ '--stat-accent': '#10b981' }}>
                    <div className="stat-icon">🧠</div>
                    <div className="stat-info">
                        <span className="stat-value">{Object.keys(memory).length}</span>
                        <span className="stat-label">Memory Sections</span>
                        <span className="stat-sub">{Object.values(memory).flat().length} items</span>
                    </div>
                </div>
                <div className="stat-card" style={{ '--stat-accent': '#f59e0b' }}>
                    <div className="stat-icon">🎯</div>
                    <div className="stat-info">
                        <span className="stat-value">{(memory['Recent Session Goals'] || []).length}</span>
                        <span className="stat-label">Recent Goals</span>
                        <span className="stat-sub">active objectives</span>
                    </div>
                </div>
                <div className="stat-card" style={{ '--stat-accent': '#ef4444' }}>
                    <div className="stat-icon">⚠️</div>
                    <div className="stat-info">
                        <span className="stat-value">{(memory['Known Issues'] || []).length}</span>
                        <span className="stat-label">Known Issues</span>
                        <span className="stat-sub">tracked problems</span>
                    </div>
                </div>
            </div>

            {/* Widgets */}
            <CronJobsWidget jobs={cron_jobs} />
            <MemoryWidget memory={memory} />
        </div>
    )
}
