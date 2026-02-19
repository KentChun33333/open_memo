import { Link, useLocation } from 'react-router-dom'

export default function Navbar() {
    const location = useLocation()

    const isActive = (path) => {
        if (path === '/') return location.pathname === '/'
        return location.pathname.startsWith(path)
    }

    return (
        <nav className="navbar">
            <Link to="/" className="navbar-brand">
                📝 <span>Open</span>Memo
            </Link>
            <ul className="navbar-links">
                <li><Link to="/" className={isActive('/') ? 'active' : ''}>Home</Link></li>
                <li><Link to="/blogs" className={isActive('/blogs') ? 'active' : ''}>Blogs</Link></li>
                <li><Link to="/login" className={isActive('/login') ? 'active' : ''}>Login</Link></li>
            </ul>
        </nav>
    )
}
