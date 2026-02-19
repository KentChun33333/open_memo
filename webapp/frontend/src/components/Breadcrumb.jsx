import { Link } from 'react-router-dom'

export default function Breadcrumb({ items }) {
    return (
        <nav className="breadcrumb">
            {items.map((item, i) => (
                <span key={i}>
                    {i > 0 && <span className="separator"> / </span>}
                    {item.to ? (
                        <Link to={item.to}>{item.label}</Link>
                    ) : (
                        <span>{item.label}</span>
                    )}
                </span>
            ))}
        </nav>
    )
}
