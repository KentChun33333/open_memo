import { useState, useEffect, useMemo } from 'react'
import { Link } from 'react-router-dom'
import {
    AreaChart, Area, BarChart, Bar, RadarChart, Radar, PolarGrid,
    PolarAngleAxis, PolarRadiusAxis, XAxis, YAxis, CartesianGrid,
    Tooltip, ResponsiveContainer, Cell, PieChart, Pie
} from 'recharts'

/* ──────── color palette ──────── */

const COLORS = [
    '#6366f1', '#8b5cf6', '#a78bfa', '#c084fc',
    '#10b981', '#14b8a6', '#06b6d4', '#0ea5e9',
    '#f59e0b', '#f43f5e', '#ec4899', '#84cc16',
]

/* ──────── helpers ──────── */

function getMonthlyData(blogs) {
    if (!blogs.length) return []
    const months = {}
    // Scan ALL dates first to get the actual range
    const dates = blogs.filter(b => b.date).map(b => new Date(b.date)).sort((a, b) => a - b)
    if (!dates.length) return []

    // Build months from earliest to latest
    const start = new Date(dates[0].getFullYear(), dates[0].getMonth(), 1)
    const end = new Date(dates[dates.length - 1].getFullYear(), dates[dates.length - 1].getMonth(), 1)
    const cursor = new Date(start)
    while (cursor <= end) {
        const key = cursor.toLocaleDateString('en-US', { year: 'numeric', month: 'short' })
        months[key] = 0
        cursor.setMonth(cursor.getMonth() + 1)
    }

    blogs.forEach(b => {
        if (!b.date) return
        const d = new Date(b.date)
        const key = d.toLocaleDateString('en-US', { year: 'numeric', month: 'short' })
        if (key in months) months[key] = (months[key] || 0) + 1
    })
    return Object.entries(months).map(([month, posts]) => ({ month, posts }))
}

function getTagData(blogs) {
    const tagCount = {}
    blogs.forEach(b => {
        const tags = (b.tags && b.tags.length) ? b.tags : ['untagged']
        tags.forEach(tag => { tagCount[tag] = (tagCount[tag] || 0) + 1 })
    })
    return Object.entries(tagCount)
        .sort((a, b) => b[1] - a[1])
        .map(([name, value], i) => ({ name, value, color: COLORS[i % COLORS.length] }))
}

function getRadarData(blogs) {
    const tagCount = {}
    blogs.forEach(b => {
        (b.tags || []).forEach(tag => { tagCount[tag] = (tagCount[tag] || 0) + 1 })
    })
    const entries = Object.entries(tagCount).sort((a, b) => b[1] - a[1]).slice(0, 8)
    const max = entries.length ? Math.max(...entries.map(e => e[1])) : 1
    return entries.map(([domain, count]) => ({ domain, count, fullMark: max }))
}

function getContentTimeline(blogs, mindmaps) {
    // Aggregate all content by date
    const dateMap = {}
    blogs.forEach(b => {
        if (!b.date) return
        const key = b.date
        if (!dateMap[key]) dateMap[key] = { date: key, blogs: 0, mindmaps: 0 }
        dateMap[key].blogs++
    })
    return Object.values(dateMap).sort((a, b) => a.date.localeCompare(b.date))
}

function getWritingStreak(blogs) {
    if (!blogs.length) return 0
    const uniqueDates = [...new Set(
        blogs.filter(b => b.date).map(b => b.date)
    )].sort().reverse()
    if (!uniqueDates.length) return 0
    let streak = 1
    for (let i = 1; i < uniqueDates.length; i++) {
        const prev = new Date(uniqueDates[i - 1])
        const curr = new Date(uniqueDates[i])
        const diffDays = (prev - curr) / (1000 * 60 * 60 * 24)
        if (diffDays <= 14) streak++ // count within 2 weeks as continuous
        else break
    }
    return streak
}

/* ──────── custom tooltip ──────── */

function ChartTooltip({ active, payload, label }) {
    if (!active || !payload?.length) return null
    return (
        <div className="chart-tooltip">
            <p className="chart-tooltip-label">{label}</p>
            {payload.map((p, i) => (
                <p key={i} style={{ color: p.color || p.fill }}>
                    {p.name}: <strong>{p.value}</strong>
                </p>
            ))}
        </div>
    )
}

function PieTooltip({ active, payload }) {
    if (!active || !payload?.length) return null
    const d = payload[0]
    return (
        <div className="chart-tooltip">
            <p style={{ color: d.payload.color }}>
                <strong>{d.name}</strong>: {d.value} post{d.value !== 1 ? 's' : ''}
            </p>
        </div>
    )
}

/* ──────── stat card ──────── */

function StatCard({ icon, label, value, sub, color, onClick, active }) {
    return (
        <div
            className={`stat-card ${active ? 'stat-card-active' : ''} ${onClick ? 'stat-card-clickable' : ''}`}
            style={{ '--stat-accent': color }}
            onClick={onClick}
        >
            <div className="stat-icon">{icon}</div>
            <div className="stat-info">
                <span className="stat-value">{value}</span>
                <span className="stat-label">{label}</span>
                {sub && <span className="stat-sub">{sub}</span>}
            </div>
        </div>
    )
}

/* ──────── domain pill ──────── */

function DomainPill({ name, count, color, active, onClick }) {
    return (
        <button
            className={`domain-pill ${active ? 'active' : ''}`}
            style={{ '--pill-color': color }}
            onClick={onClick}
        >
            <span className="domain-pill-dot" style={{ background: color }} />
            <span className="domain-pill-name">{name}</span>
            <span className="domain-pill-count">{count}</span>
        </button>
    )
}

/* ──────── page ──────── */

export default function Home() {
    const [blogs, setBlogs] = useState([])
    const [mindmaps, setMindmaps] = useState([])
    const [loading, setLoading] = useState(true)
    const [activeDomain, setActiveDomain] = useState(null)

    useEffect(() => {
        Promise.all([
            fetch('/api/blogs').then(r => r.json()),
            fetch('/api/mindmaps').then(r => r.json()),
        ])
            .then(([b, m]) => { setBlogs(b); setMindmaps(m) })
            .catch(() => { })
            .finally(() => setLoading(false))
    }, [])

    // Filter blogs by active domain
    const filteredBlogs = useMemo(() => {
        if (!activeDomain) return blogs
        if (activeDomain === 'untagged') return blogs.filter(b => !b.tags?.length)
        return blogs.filter(b => b.tags?.includes(activeDomain))
    }, [blogs, activeDomain])

    const monthlyData = useMemo(() => getMonthlyData(filteredBlogs), [filteredBlogs])
    const tagData = useMemo(() => getTagData(blogs), [blogs])
    const radarData = useMemo(() => getRadarData(blogs), [blogs])
    const timeline = useMemo(() => getContentTimeline(filteredBlogs, mindmaps), [filteredBlogs, mindmaps])
    const uniqueTags = useMemo(() => new Set(blogs.flatMap(b => b.tags || [])).size, [blogs])
    const streak = useMemo(() => getWritingStreak(blogs), [blogs])

    const handleDomainClick = (name) => {
        setActiveDomain(prev => prev === name ? null : name)
    }

    if (loading) return <div className="loading">Loading dashboard…</div>

    return (
        <div className="dashboard">
            {/* Header */}
            <div className="dashboard-header">
                <div>
                    <h1 className="dashboard-title">Dashboard</h1>
                    <p className="dashboard-subtitle">
                        Your knowledge growth at a glance
                        {activeDomain && (
                            <span className="filter-badge">
                                Filtered: <strong>{activeDomain}</strong>
                                <button onClick={() => setActiveDomain(null)} className="filter-clear">✕</button>
                            </span>
                        )}
                    </p>
                </div>
            </div>

            {/* Stat Cards */}
            <div className="stat-grid">
                <StatCard
                    icon="📝" label="Blog Posts" value={filteredBlogs.length}
                    sub={activeDomain ? `of ${blogs.length} total` : `across ${uniqueTags} domains`}
                    color="var(--accent)"
                />
                <StatCard
                    icon="🧠" label="Mind Maps" value={mindmaps.length}
                    sub={`${mindmaps.reduce((s, m) => s + (m.node_count || 0), 0)} total nodes`}
                    color="var(--success)"
                />
                <StatCard
                    icon="🏷️" label="Domains" value={uniqueTags}
                    sub="unique tag topics"
                    color="var(--warning)"
                />
                <StatCard
                    icon="🔥" label="Active Days" value={streak}
                    sub="unique writing sessions"
                    color="#f43f5e"
                />
            </div>

            {/* Domain Filter Bar */}
            <div className="domain-bar">
                <h3 className="chart-title">🏷️ Explore by Domain</h3>
                <div className="domain-pills">
                    {tagData.map(d => (
                        <DomainPill
                            key={d.name}
                            name={d.name}
                            count={d.value}
                            color={d.color}
                            active={activeDomain === d.name}
                            onClick={() => handleDomainClick(d.name)}
                        />
                    ))}
                </div>
            </div>

            {/* Charts Row */}
            <div className="chart-row">
                {/* Monthly Activity */}
                <div className="chart-card chart-card-wide">
                    <h3 className="chart-title">
                        📈 Content Timeline
                        {activeDomain && <span className="chart-filter-hint">— showing "{activeDomain}"</span>}
                    </h3>
                    <ResponsiveContainer width="100%" height={280}>
                        <AreaChart data={monthlyData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                            <defs>
                                <linearGradient id="gradientPosts" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="0%" stopColor="#6366f1" stopOpacity={0.4} />
                                    <stop offset="100%" stopColor="#6366f1" stopOpacity={0.05} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                            <XAxis dataKey="month" stroke="#6c6c8a" fontSize={12} />
                            <YAxis stroke="#6c6c8a" fontSize={12} allowDecimals={false} />
                            <Tooltip content={<ChartTooltip />} />
                            <Area
                                type="monotone" dataKey="posts" name="Posts"
                                stroke="#6366f1" strokeWidth={2.5}
                                fill="url(#gradientPosts)"
                                dot={{ fill: '#6366f1', r: 5, stroke: '#1a1a2e', strokeWidth: 2 }}
                                activeDot={{ r: 7, stroke: '#fff', strokeWidth: 2 }}
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>

                {/* Domain Distribution Pie */}
                <div className="chart-card">
                    <h3 className="chart-title">🧩 Domain Distribution</h3>
                    <ResponsiveContainer width="100%" height={280}>
                        <PieChart>
                            <Pie
                                data={tagData}
                                cx="50%" cy="50%"
                                innerRadius="45%" outerRadius="75%"
                                paddingAngle={3}
                                dataKey="value"
                                stroke="none"
                                style={{ cursor: 'pointer' }}
                                onClick={(d) => handleDomainClick(d.name)}
                            >
                                {tagData.map((entry, i) => (
                                    <Cell
                                        key={i}
                                        fill={entry.color}
                                        opacity={activeDomain && activeDomain !== entry.name ? 0.3 : 1}
                                    />
                                ))}
                            </Pie>
                            <Tooltip content={<PieTooltip />} />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Second Row: Radar + Activity Timeline */}
            <div className="chart-row">
                {/* Radar */}
                <div className="chart-card">
                    <h3 className="chart-title">🕸️ Domain Depth</h3>
                    {radarData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={280}>
                            <RadarChart outerRadius="65%" data={radarData}>
                                <PolarGrid stroke="rgba(255,255,255,0.1)" />
                                <PolarAngleAxis
                                    dataKey="domain" stroke="#a0a0c0" fontSize={11}
                                    tick={{ fill: '#a0a0c0', fontSize: 11 }}
                                />
                                <PolarRadiusAxis stroke="#6c6c8a" fontSize={10} />
                                <Radar
                                    name="Posts" dataKey="count"
                                    stroke="#8b5cf6" fill="#8b5cf6"
                                    fillOpacity={0.3} strokeWidth={2}
                                />
                                <Tooltip content={<ChartTooltip />} />
                            </RadarChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="chart-empty">
                            <p>Add tags to your blogs to see domain depth</p>
                        </div>
                    )}
                </div>

                {/* Activity Bars */}
                <div className="chart-card chart-card-wide">
                    <h3 className="chart-title">
                        📊 Writing Activity by Date
                        {activeDomain && <span className="chart-filter-hint">— showing "{activeDomain}"</span>}
                    </h3>
                    <ResponsiveContainer width="100%" height={280}>
                        <BarChart data={timeline} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                            <XAxis dataKey="date" stroke="#6c6c8a" fontSize={11} />
                            <YAxis stroke="#6c6c8a" fontSize={12} allowDecimals={false} />
                            <Tooltip content={<ChartTooltip />} />
                            <Bar
                                dataKey="blogs" name="Blog Posts"
                                fill="#6366f1" radius={[4, 4, 0, 0]}
                                maxBarSize={50}
                            />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Recent Activity */}
            <div className="dashboard-recent">
                {filteredBlogs.length > 0 && (
                    <section>
                        <div className="section-header">
                            <h3>📝 {activeDomain ? `"${activeDomain}" Posts` : 'Recent Posts'}</h3>
                            <Link to="/blogs">View all →</Link>
                        </div>
                        <div className="card-grid card-grid-2">
                            {filteredBlogs.slice(0, 4).map(blog => (
                                <Link key={blog.slug} to={`/blogs/${blog.slug}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                                    <div className="card card-compact">
                                        <h4>{blog.title}</h4>
                                        <div className="meta">
                                            <span>📅 {blog.date}</span>
                                            {blog.tags?.slice(0, 3).map(tag => (
                                                <span key={tag} className="tag">{tag}</span>
                                            ))}
                                        </div>
                                    </div>
                                </Link>
                            ))}
                        </div>
                    </section>
                )}

                {mindmaps.length > 0 && (
                    <section style={{ marginTop: 'var(--space-xl)' }}>
                        <div className="section-header">
                            <h3>🧠 Mind Maps</h3>
                            <Link to="/mindmaps">View all →</Link>
                        </div>
                        <div className="card-grid card-grid-3">
                            {mindmaps.map(mm => (
                                <Link key={mm.id} to={`/mindmaps/${mm.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                                    <div className="card card-compact">
                                        <h4>{mm.title}</h4>
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
        </div>
    )
}
