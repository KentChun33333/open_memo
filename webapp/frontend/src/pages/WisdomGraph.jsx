import { useState, useEffect, useRef } from 'react'
import * as d3 from 'd3'
import { useNavigate } from 'react-router-dom'
import Breadcrumb from '../components/Breadcrumb'

export default function WisdomGraph() {
    const svgRef = useRef(null)
    const [blogs, setBlogs] = useState([])
    const [loading, setLoading] = useState(true)
    const navigate = useNavigate()

    useEffect(() => {
        fetch('/api/blogs')
            .then(r => r.json())
            .then(data => {
                setBlogs(data)
                setLoading(false)
            })
            .catch(() => setLoading(false))
    }, [])

    useEffect(() => {
        if (!blogs.length || !svgRef.current) return

        // 1. Prepare Data
        const nodes = [{ id: 'ROOT', label: 'Wisdom Root', type: 'root', radius: 15 }]
        const links = []

        const tags = [...new Set(blogs.flatMap(b => b.tags || []))]

        // Add Category Nodes
        tags.forEach(tag => {
            nodes.push({ id: `tag-${tag}`, label: tag, type: 'tag', radius: 10 })
            links.push({ source: 'ROOT', target: `tag-${tag}` })
        })

        // Add Blog Nodes
        blogs.forEach(blog => {
            nodes.push({ id: blog.slug, label: blog.title, type: 'blog', radius: 6 })
            if (blog.tags && blog.tags.length > 0) {
                blog.tags.forEach(tag => {
                    links.push({ source: `tag-${tag}`, target: blog.slug })
                })
            } else {
                links.push({ source: 'ROOT', target: blog.slug })
            }
        })

        // 2. Setup D3
        const width = svgRef.current.clientWidth
        const height = 600
        const svg = d3.select(svgRef.current)
            .attr('viewBox', [0, 0, width, height])
            .attr('style', 'max-width: 100%; height: auto;')

        svg.selectAll('*').remove()

        const g = svg.append('g')

        // Zoom & Pan
        svg.call(d3.zoom()
            .extent([[0, 0], [width, height]])
            .scaleExtent([0.5, 4])
            .on('zoom', ({ transform }) => g.attr('transform', transform)))

        const simulation = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(links).id(d => d.id).distance(80))
            .force('charge', d3.forceManyBody().strength(-150))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('x', d3.forceX(width / 2).strength(0.1))
            .force('y', d3.forceY(height / 2).strength(0.1))

        const link = g.append('g')
            .attr('stroke', 'var(--border)')
            .attr('stroke-opacity', 0.6)
            .selectAll('line')
            .data(links)
            .join('line')
            .attr('stroke-width', 1)

        const node = g.append('g')
            .attr('stroke', 'var(--bg-card)')
            .attr('stroke-width', 2)
            .selectAll('g')
            .data(nodes)
            .join('g')
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended))
            .on('click', (event, d) => {
                if (d.type === 'blog') navigate(`/blogs/${d.id}`)
            })
            .style('cursor', d => d.type === 'blog' ? 'pointer' : 'default')

        node.append('circle')
            .attr('r', d => d.radius)
            .attr('fill', d => {
                if (d.type === 'root') return 'var(--accent)'
                if (d.type === 'tag') return '#10b981'
                return 'var(--text-primary)'
            })
            .attr('filter', 'drop-shadow(0 0 8px rgba(99, 102, 241, 0.4))')

        node.append('text')
            .text(d => d.label)
            .attr('x', d => d.radius + 5)
            .attr('y', 4)
            .attr('fill', 'var(--text-primary)')
            .attr('font-size', d => d.type === 'blog' ? '10px' : '14px')
            .attr('font-weight', d => d.type === 'blog' ? 'normal' : 'bold')
            .style('pointer-events', 'none')
            .style('text-shadow', '0 2px 4px rgba(0,0,0,0.5)')

        simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y)

            node
                .attr('transform', d => `translate(${d.x},${d.y})`)
        })

        function dragstarted(event) {
            if (!event.active) simulation.alphaTarget(0.3).restart()
            event.subject.fx = event.subject.x
            event.subject.fy = event.subject.y
        }

        function dragged(event) {
            event.subject.fx = event.x
            event.subject.fy = event.y
        }

        function dragended(event) {
            if (!event.active) simulation.alphaTarget(0)
            event.subject.fx = null
            event.subject.fy = null
        }

        return () => simulation.stop()
    }, [blogs, navigate])

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

            <div className="card" style={{ flex: 1, position: 'relative', overflow: 'hidden', padding: 0, background: 'rgba(10, 11, 30, 0.4)' }}>
                <svg ref={svgRef} style={{ width: '100%', height: '100%', display: 'block' }} />

                {loading && (
                    <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', color: 'var(--text-muted)' }}>
                        Building constellation…
                    </div>
                )}
            </div>
        </div>
    )
}
