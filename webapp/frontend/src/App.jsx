import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import BlogList from './pages/BlogList'
import BlogPost from './pages/BlogPost'
import MindMap from './pages/MindMap'
import Login from './pages/Login'

export default function App() {
    return (
        <div className="app">
            <Navbar />
            <main className="main-content">
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/blogs" element={<BlogList />} />
                    <Route path="/blogs/:slug" element={<BlogPost />} />
                    <Route path="/mindmaps/:id" element={<MindMap />} />
                    <Route path="/login" element={<Login />} />
                </Routes>
            </main>
        </div>
    )
}
