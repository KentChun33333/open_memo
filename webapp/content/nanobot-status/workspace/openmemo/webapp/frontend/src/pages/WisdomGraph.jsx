import Breadcrumb from '../components/Breadcrumb'
import WisdomGraphWidget from '../components/WisdomGraphWidget'

export default function WisdomGraph() {
    return (
        <div className="container" style={{ height: 'calc(100vh - 100px)', display: 'flex', flexDirection: 'column' }}>
            <Breadcrumb items={[
                { label: 'Home', to: '/' },
                { label: 'Wisdom Map' }
            ]} />

            <div className="section-header">
                <h2>🌌 Wisdom Constellation</h2>
                <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                    Visualizing semantic connections between your thoughts.
                </span>
            </div>

            <WisdomGraphWidget mode="full" height={800} />
        </div>
    )
}
