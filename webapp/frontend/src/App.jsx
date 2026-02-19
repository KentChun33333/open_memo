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
