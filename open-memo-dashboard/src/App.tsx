import { useState, useEffect } from 'react';
import './App.css';

interface Doc {
  id: string;
  title: string;
  summary: string;
  keyPoints: string[];
  tags: string[];
  path: string;
}

interface MindMapData {
  id: string;
  title: string;
  content: string;
  nodes: MindMapData[];
}

const sampleDocs: Doc[] = [
  {
    id: 'llm-basics',
    title: 'LLM Basics',
    summary: 'A foundational overview of Large Language Models and their architecture including transformer models, training processes, and limitations.',
    keyPoints: [
      'Transformer architecture with self-attention',
      'Encoder-only, decoder-only, and encoder-decoder types',
      'Pre-training, fine-tuning, and RLHF',
      'Limitations: hallucinations, context windows, biases'
    ],
    tags: ['llm', 'basics', 'architecture'],
    path: 'llm-basics.md'
  },
  {
    id: 'prompt-engineering',
    title: 'Prompt Engineering',
    summary: 'Techniques for effectively communicating with LLMs including chain of thought, few-shot learning, and advanced prompting patterns.',
    keyPoints: [
      'Clarity and specificity in instructions',
      'Chain of thought reasoning',
      'Few-shot learning with examples',
      'Self-consistency and tree of thoughts'
    ],
    tags: ['prompting', 'engineering', 'techniques'],
    path: 'prompt-engineering.md'
  },
  {
    id: 'agent-architecture',
    title: 'Agent Architecture',
    summary: 'Design patterns for building intelligent agents with LLMs including ReAct, plan-and-execute, and hierarchical task networks.',
    keyPoints: [
      'Plan-and-Execute pattern',
      'ReAct (Reasoning + Acting) loop',
      'Memory systems: short-term, long-term, working',
      'Tool integration and external API calls'
    ],
    tags: ['agents', 'architecture', 'patterns'],
    path: 'agent-architecture.md'
  }
];

async function loadMarkdownFile(path: string): Promise<string> {
  try {
    const response = await fetch(`open_memo/${path}`);
    if (!response.ok) {
      throw new Error(`Failed to load ${path}`);
    }
    return await response.text();
  } catch (error) {
    console.error(`Error loading ${path}:`, error);
    return '';
  }
}

function parseMarkdownToMindMap(content: string, filePath: string): MindMapData {
  const lines = content.split('\n');
  let title = 'Untitled';
  let nodes: MindMapData[] = [];
  let currentContentLines: string[] = [];
  let inContent = false;

  for (const line of lines) {
    if (line.startsWith('# ') && line.trim().endsWith('.md')) {
      title = line.substring(2).replace('.md', '').trim();
      inContent = true;
    } else if (line.startsWith('# ') || line.startsWith('## ')) {
      title = line.replace(/^#+\s*/, '').trim();
      inContent = false;
    } else if (line.startsWith('[') && line.includes('](') && line.includes('.md')) {
      const match = line.match(/\[([^\]]+)\]\(([^)]+)\)/);
      if (match) {
        const linkTitle = match[1];
        const linkPath = match[2];
        
        nodes.push({
          id: linkPath.replace('.md', ''),
          title: linkTitle,
          content: '',
          nodes: []
        });
      }
      inContent = false;
    } else if (inContent && line.trim() && !line.startsWith('##')) {
      currentContentLines.push(line);
    }
  }

  return {
    id: filePath.replace('.md', '').replace('node_', ''),
    title,
    content: currentContentLines.join('\n'),
    nodes
  };
}

function App() {
  const [view, setView] = useState<'docs' | 'mind-map'>('docs');
  const [selectedDoc, setSelectedDoc] = useState<Doc | null>(null);
  const [filterTag, setFilterTag] = useState<string>('');
  const [mindMapRoot, setMindMapRoot] = useState<MindMapData | null>(null);
  const [selectedMindMapNode, setSelectedMindMapNode] = useState<MindMapData | null>(null);
  const [mindMapLoading, setMindMapLoading] = useState(true);

  const allTags = Array.from(new Set(sampleDocs.flatMap(doc => doc.tags)));

  const filteredDocs = filterTag
    ? sampleDocs.filter(doc => doc.tags.includes(filterTag))
    : sampleDocs;

  useEffect(() => {
    loadMindMapData();
  }, []);

  async function loadMindMapData() {
    try {
      const overviewContent = await loadMarkdownFile('mind-map/node_overview.md');
      const root = parseMarkdownToMindMap(overviewContent, 'node_overview.md');
      setMindMapRoot(root);
    } catch (error) {
      console.error('Error loading mind map:', error);
    } finally {
      setMindMapLoading(false);
    }
  }

  const handleDocClick = (doc: Doc) => {
    setSelectedDoc(doc);
  };

  const handleNodeClick = (node: MindMapData) => {
    setSelectedMindMapNode(node);
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>🧬 Open Memo Dashboard</h1>
        <div className="view-switcher">
          <button
            className={`view-btn ${view === 'docs' ? 'active' : ''}`}
            onClick={() => {
              setView('docs');
              setSelectedDoc(null);
            }}
          >
            Documents
          </button>
          <button
            className={`view-btn ${view === 'mind-map' ? 'active' : ''}`}
            onClick={() => {
              setView('mind-map');
              setSelectedMindMapNode(null);
            }}
          >
            Mind Map
          </button>
        </div>
      </header>

      {view === 'docs' && (
        <>
          <div className="filter-bar">
            <span>Filter by tag:</span>
            <div className="tag-cloud">
              <button
                className={`tag-btn ${filterTag === '' ? 'active' : ''}`}
                onClick={() => setFilterTag('')}
              >
                All
              </button>
              {allTags.map(tag => (
                <button
                  key={tag}
                  className={`tag-btn ${filterTag === tag ? 'active' : ''}`}
                  onClick={() => setFilterTag(tag)}
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>

          <div className="doc-grid">
            {filteredDocs.map(doc => (
              <div
                key={doc.id}
                className="doc-card"
                onClick={() => handleDocClick(doc)}
              >
                <h3>{doc.title}</h3>
                <p className="doc-summary">{doc.summary}</p>
                <div className="doc-tags">
                  {doc.tags.map(tag => (
                    <span key={tag} className="tag">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {selectedDoc && (
            <div className="modal" onClick={() => setSelectedDoc(null)}>
              <div className="modal-content" onClick={e => e.stopPropagation()}>
                <button className="close-btn" onClick={() => setSelectedDoc(null)}>
                  ✕
                </button>
                <h2>{selectedDoc.title}</h2>
                <p className="doc-summary">{selectedDoc.summary}</p>
                <h4>Key Topics</h4>
                <ul className="key-points">
                  {selectedDoc.keyPoints.map((point, idx) => (
                    <li key={idx}>
                      <span className="step-number">{idx + 1}.</span>
                      {point}
                    </li>
                  ))}
                </ul>
                <div className="doc-meta">
                  <small>Source: {selectedDoc.path}</small>
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {view === 'mind-map' && mindMapLoading && (
        <div className="loading-container">
          <div className="spinner" />
          <p>Loading mind map...</p>
        </div>
      )}

      {view === 'mind-map' && !mindMapLoading && (
        <div className="mind-map-container">
          <h2 className="mind-map-title">{selectedMindMapNode?.title || (mindMapRoot?.title || 'Welcome to Mind Map')}</h2>
          
          {selectedMindMapNode ? (
            <div className="mind-map-details">
              <button 
                className="back-btn"
                onClick={() => setSelectedMindMapNode(null)}
              >
                ← Back to Root
              </button>
              <MindMapNodeComponent 
                node={selectedMindMapNode} 
                onSelect={handleNodeClick}
              />
            </div>
          ) : (
            mindMapRoot && (
              <MindMapNodeComponent 
                node={mindMapRoot} 
                onSelect={handleNodeClick}
              />
            )
          )}
        </div>
      )}
    </div>
  );
}

function MindMapNodeComponent({ node, onSelect, depth = 0 }: { node: MindMapData; onSelect: (node: MindMapData) => void; depth?: number }) {
  const [expanded, setExpanded] = useState(depth < 2);
  
  const indent = Math.min(depth * 20, 100);
  
  return (
    <div 
      className="mind-map-node"
      style={{ paddingLeft: `${indent}px` }}
    >
      <div className="node-header" onClick={() => setExpanded(!expanded)}>
        <div className="node-title">{node.title}</div>
        {node.nodes.length > 0 && (
          <span className="expand-toggle">
            {expanded ? '▼' : '▶'}
          </span>
        )}
      </div>
      
      {node.content && (
        <div className="node-content">{node.content}</div>
      )}
      
      {expanded && node.nodes.length > 0 && (
        <div className="node-children">
          {node.nodes.map((child: MindMapData) => (
            <MindMapNodeComponent 
              key={child.id} 
              node={child} 
              onSelect={onSelect}
              depth={depth + 1} 
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default App;