import React, { useState } from 'react';
import { 
  Database, 
  Filter, 
  Info, 
  ArrowUpRight, 
  Layers, 
  Share2, 
  Check, 
  Code2
} from 'lucide-react';
import SpatialCard from '../components/SpatialCard';
import { MOCK_GRAPH_DATA } from '../data/mockData';

export default function KnowledgeGraphView() {
  const [selectedNode, setSelectedNode] = useState(MOCK_GRAPH_DATA.nodes[0]);
  const [filterType, setFilterType] = useState('ALL');

  const filterOptions = ['ALL', 'Program', 'Table', 'Script', 'Package', 'BusinessRule'];

  const filteredNodes = filterType === 'ALL' 
    ? MOCK_GRAPH_DATA.nodes 
    : MOCK_GRAPH_DATA.nodes.filter(n => n.type === filterType);

  const getNodeColor = (type) => {
    switch(type) {
      case 'Program': return '#00f2fe';
      case 'Table': return '#10b981';
      case 'Script': return '#38bdf8';
      case 'Package': return '#c084fc';
      case 'BusinessRule': return '#f59e0b';
      default: return '#94a3b8';
    }
  };

  return (
    <div className="graph-view-container">
      {/* Top Controls & Telemetry Bar */}
      <div className="graph-top-bar glass-panel">
        <div className="graph-title-group">
          <div className="icon-badge-box">
            <Database size={18} className="pill-icon-cyan" />
          </div>
          <div>
            <h2 className="graph-view-title">Neo4j Aura Graph Topology</h2>
            <p className="graph-view-sub">Cross-system lineage & entity relationship network</p>
          </div>
        </div>

        {/* Node Category Filters */}
        <div className="graph-filter-pills">
          {filterOptions.map((type) => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`filter-pill ${filterType === type ? 'filter-pill-active' : ''}`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* Main Graph Grid: Interactive Canvas + Inspector Panel */}
      <div className="graph-main-layout">
        {/* Spatial 3D Network Canvas */}
        <div className="glass-panel graph-canvas-panel">
          <div className="canvas-header-overlay">
            <div className="live-graph-badge">
              <span className="pulse-dot pulse-cyan" />
              <span>LIVE GRAPH EXPLORER</span>
            </div>
            <div className="canvas-legend">
              <span className="legend-item"><span className="legend-dot" style={{ background: '#00f2fe' }} /> COBOL</span>
              <span className="legend-item"><span className="legend-dot" style={{ background: '#10b981' }} /> Table</span>
              <span className="legend-item"><span className="legend-dot" style={{ background: '#38bdf8' }} /> SQL</span>
              <span className="legend-item"><span className="legend-dot" style={{ background: '#c084fc' }} /> SSIS</span>
              <span className="legend-item"><span className="legend-dot" style={{ background: '#f59e0b' }} /> Rule</span>
            </div>
          </div>

          {/* Interactive SVG Network Map */}
          <svg className="spatial-network-svg" viewBox="0 0 800 440">
            <defs>
              <linearGradient id="edgeGlow" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#00f2fe" stopOpacity="0.6" />
                <stop offset="100%" stopColor="#9d4edd" stopOpacity="0.6" />
              </linearGradient>
              <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="4" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>

            {/* Render Links */}
            {MOCK_GRAPH_DATA.links.map((link, idx) => {
              const sourceNode = MOCK_GRAPH_DATA.nodes.find(n => n.id === link.source);
              const targetNode = MOCK_GRAPH_DATA.nodes.find(n => n.id === link.target);
              if (!sourceNode || !targetNode) return null;

              const isConnected = selectedNode && (selectedNode.id === sourceNode.id || selectedNode.id === targetNode.id);

              return (
                <g key={idx}>
                  <line
                    x1={sourceNode.x}
                    y1={sourceNode.y}
                    x2={targetNode.x}
                    y2={targetNode.y}
                    stroke={isConnected ? "url(#edgeGlow)" : "rgba(148, 163, 184, 0.45)"}
                    strokeWidth={isConnected ? "2.5" : "1.4"}
                    strokeDasharray={isConnected ? "4 2" : "none"}
                    className={isConnected ? "animated-edge" : ""}
                  />
                  <text
                    x={(sourceNode.x + targetNode.x) / 2}
                    y={(sourceNode.y + targetNode.y) / 2 - 6}
                    fill={isConnected ? "#0284c7" : "#64748b"}
                    fontSize="9.5"
                    fontFamily="JetBrains Mono"
                    fontWeight="600"
                    textAnchor="middle"
                  >
                    {link.label}
                  </text>
                </g>
              );
            })}

            {/* Render Nodes */}
            {filteredNodes.map((node) => {
              const isSelected = selectedNode?.id === node.id;
              const color = getNodeColor(node.type);

              return (
                <g 
                  key={node.id} 
                  transform={`translate(${node.x}, ${node.y})`}
                  onClick={() => setSelectedNode(node)}
                  className="graph-node-group"
                  style={{ cursor: 'pointer' }}
                >
                  {/* Outer pulse ring for selected node */}
                  {isSelected && (
                    <circle
                      r="26"
                      fill="none"
                      stroke={color}
                      strokeWidth="2"
                      opacity="0.8"
                      className="selected-node-pulse"
                    />
                  )}
                  {/* Glow backdrop */}
                  <circle
                    r="18"
                    fill={color}
                    opacity={isSelected ? "0.3" : "0.15"}
                    filter="url(#glow)"
                  />
                  {/* Core circle (Crisp White with colored ring) */}
                  <circle
                    r="14"
                    fill="#ffffff"
                    stroke={color}
                    strokeWidth={isSelected ? "3" : "2"}
                  />
                  <text
                    y="28"
                    fill={isSelected ? "#0f172a" : "#334155"}
                    fontSize="11"
                    fontFamily="Outfit"
                    fontWeight={isSelected ? "800" : "600"}
                    textAnchor="middle"
                  >
                    {node.label}
                  </text>
                  <text
                    y="39"
                    fill={color}
                    fontSize="8.5"
                    fontFamily="JetBrains Mono"
                    fontWeight="700"
                    textAnchor="middle"
                  >
                    :{node.type}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>

        {/* Spatial Node Inspector Sidebar */}
        <div className="glass-panel node-inspector-panel">
          <div className="inspector-header">
            <div className="badge badge-cyan">Entity Inspector</div>
            <span className="live-indicator">Neo4j Aura Node</span>
          </div>

          {selectedNode ? (
            <div className="inspector-body">
              <h3 className="inspector-node-name">{selectedNode.label}</h3>
              <div className="inspector-meta-row">
                <span className="meta-label">Node Label</span>
                <span className="meta-val font-mono">:{selectedNode.type}</span>
              </div>
              <div className="inspector-meta-row">
                <span className="meta-label">Architecture Tier</span>
                <span className="meta-val">{selectedNode.system}</span>
              </div>
              <div className="inspector-meta-row">
                <span className="meta-label">Graph Status</span>
                <span className="meta-val text-emerald">
                  <Check size={13} style={{ display: 'inline', marginRight: 4 }} />
                  Indexed & Verified
                </span>
              </div>

              <div className="inspector-divider" />

              <h4 className="inspector-subtitle">Active Lineage Connections</h4>
              <div className="inspector-relations-list">
                {MOCK_GRAPH_DATA.links
                  .filter(l => l.source === selectedNode.id || l.target === selectedNode.id)
                  .map((link, idx) => (
                    <div key={idx} className="relation-item">
                      <span className="relation-type font-mono">{link.label}</span>
                      <span className="relation-target">
                        {link.source === selectedNode.id ? `➔ ${link.target}` : `⬅ from ${link.source}`}
                      </span>
                    </div>
                  ))}
              </div>

              <div className="inspector-divider" />

              <button 
                className="btn btn-glass btn-sm w-full"
                onClick={() => setCustomCypher(`MATCH (n:${selectedNode.type} {id: '${selectedNode.id}'})-[r]-(m)\nRETURN n, r, m;`)}
              >
                <Terminal size={14} /> Generate Cypher Traversal
              </button>
            </div>
          ) : (
            <div className="inspector-empty">
              Select any node in the spatial canvas to inspect properties and lineage.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
