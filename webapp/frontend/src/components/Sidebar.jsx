import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import logo from '../assets/logo.jpeg'

const navItems = [
    {
        label: 'Consciousness',
        to: '/consciousness',
        icon: (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2v8" />
                <path d="m16 4-4 4-4-4" />
                <path d="m7 12 5 5 5-5" />
                <path d="M12 22v-5" />
                <circle cx="12" cy="12" r="10" />
            </svg>
        ),
    },
    {
        label: 'Dashboard',
        to: '/',
        icon: (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="3" width="7" height="7" rx="1" />
                <rect x="14" y="3" width="7" height="7" rx="1" />
                <rect x="3" y="14" width="7" height="7" rx="1" />
                <rect x="14" y="14" width="7" height="7" rx="1" />
            </svg>
        ),
        exact: true,
    },
    {
        label: 'Blogs',
        to: '/blogs',
        icon: (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
            </svg>
        ),
    },
    {
        label: 'Mind Maps',
        to: '/mindmaps',
        icon: (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="3" />
                <path d="M12 2v4" /><path d="M12 18v4" />
                <path d="M4.93 4.93l2.83 2.83" /><path d="M16.24 16.24l2.83 2.83" />
                <path d="M2 12h4" /><path d="M18 12h4" />
                <path d="M4.93 19.07l2.83-2.83" /><path d="M16.24 7.76l2.83-2.83" />
            </svg>
        ),
        matchPrefix: true,
    },
    {
        label: 'Nanobot',
        to: '/nanobot',
        icon: (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 5c-1.5-2-4-2-6 0" />
                <path d="M18 5c-1.5-2-4-2-6 0" />
                <path d="M5 11c-1 0-2 .5-2 2s1 2 2 2" />
                <path d="M19 11c1 0 2 .5 2 2s-1 2-2 2" />
                <path d="M6 8a6 6 0 0 0 12 0c0 8-3 13-6 13S6 16 6 8z" />
                <circle cx="10" cy="10" r="1" fill="currentColor" />
                <circle cx="14" cy="10" r="1" fill="currentColor" />
            </svg>
        ),
    },
]

const bottomItems = [
    {
        label: 'Login',
        to: '/login',
        icon: (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
                <polyline points="10 17 15 12 10 7" />
                <line x1="15" y1="12" x2="3" y2="12" />
            </svg>
        ),
    },
]

export default function Sidebar({ collapsed, onToggle }) {
    const location = useLocation()

    const isActive = (item) => {
        if (item.exact) return location.pathname === item.to
        if (item.matchPrefix) return location.pathname.startsWith(item.to)
        return location.pathname === item.to || location.pathname.startsWith(item.to + '/')
    }

    return (
        <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
            {/* Brand */}
            <div className="sidebar-brand">
                <Link to="/">
                    <img src={logo} alt="Logo" className="sidebar-logo-img" />
                    {!collapsed && (
                        <span className="sidebar-title">
                            <span className="accent">Open</span>Memo
                        </span>
                    )}
                </Link>
            </div>

            {/* Navigation */}
            <nav className="sidebar-nav">
                <div className="sidebar-section">
                    {!collapsed && <span className="sidebar-section-label">Navigation</span>}
                    <ul>
                        {navItems.map(item => (
                            <li key={item.to}>
                                <Link
                                    to={item.to}
                                    className={`sidebar-link ${isActive(item) ? 'active' : ''}`}
                                    title={collapsed ? item.label : undefined}
                                >
                                    <span className="sidebar-icon">{item.icon}</span>
                                    {!collapsed && <span className="sidebar-label">{item.label}</span>}
                                </Link>
                            </li>
                        ))}
                    </ul>
                </div>
            </nav>

            {/* Bottom section */}
            <div className="sidebar-bottom">
                <ul>
                    {bottomItems.map(item => (
                        <li key={item.to}>
                            <Link
                                to={item.to}
                                className={`sidebar-link ${isActive(item) ? 'active' : ''}`}
                                title={collapsed ? item.label : undefined}
                            >
                                <span className="sidebar-icon">{item.icon}</span>
                                {!collapsed && <span className="sidebar-label">{item.label}</span>}
                            </Link>
                        </li>
                    ))}
                </ul>

                {/* Collapse toggle */}
                <button
                    className="sidebar-toggle"
                    onClick={onToggle}
                    title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
                >
                    <svg
                        width="18" height="18" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
                        style={{ transform: collapsed ? 'rotate(180deg)' : 'none', transition: 'transform 250ms ease' }}
                    >
                        <polyline points="11 17 6 12 11 7" />
                        <polyline points="18 17 13 12 18 7" />
                    </svg>
                    {!collapsed && <span>Collapse</span>}
                </button>
            </div>
        </aside>
    )
}
