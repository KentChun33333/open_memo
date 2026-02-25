import { useState, useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Home from './pages/Home'
import BlogList from './pages/BlogList'
import BlogPost from './pages/BlogPost'
import NoteList from './pages/NoteList'
import NotePost from './pages/NotePost'
import MindMapList from './pages/MindMapList'
import MindMap from './pages/MindMap'
import NanobotStatus from './pages/NanobotStatus'
import WisdomGraph from './pages/WisdomGraph'
import Consciousness from './pages/Consciousness'
import Login from './pages/Login'

export default function App() {
    const [collapsed, setCollapsed] = useState(() => {
        return localStorage.getItem('sidebar-collapsed') === 'true'
    })

    useEffect(() => {
        localStorage.setItem('sidebar-collapsed', collapsed)
    }, [collapsed])

    return (
        <div className={`app-layout ${collapsed ? 'sidebar-collapsed' : ''}`}>
            <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(c => !c)} />
            <main className="main-content">
                <div className="mobile-header">
                    <button className="mobile-menu-btn" onClick={() => setCollapsed(!collapsed)}>
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <line x1="3" y1="12" x2="21" y2="12"></line>
                            <line x1="3" y1="6" x2="21" y2="6"></line>
                            <line x1="3" y1="18" x2="21" y2="18"></line>
                        </svg>
                    </button>
                    <span className="mobile-brand"><span className="accent">Open</span>Memo</span>
                </div>
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/blogs" element={<BlogList />} />
                    <Route path="/blogs/:slug" element={<BlogPost />} />
                    <Route path="/notes" element={<NoteList />} />
                    <Route path="/notes/:slug" element={<NotePost />} />
                    <Route path="/mindmaps" element={<MindMapList />} />
                    <Route path="/mindmaps/:id" element={<MindMap />} />
                    <Route path="/nanobot" element={<NanobotStatus />} />
                    <Route path="/wisdom-graph" element={<WisdomGraph />} />
                    <Route path="/consciousness" element={<Consciousness />} />
                    <Route path="/login" element={<Login />} />
                </Routes>
            </main>
        </div>
    )
}
