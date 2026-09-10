import React, { useState, useEffect } from 'react';
import { 
  Database, 
  Search, 
  RotateCcw, 
  Check, 
  ExternalLink, 
  GitFork, 
  Layers, 
  Activity,
  ArrowRight,
  ShieldCheck,
  Code,
  Copy,
  Info,
  Maximize2
} from 'lucide-react';
import SpatialCard from '../components/SpatialCard';
import { MOCK_GRAPH_DATA, SOURCE_FILES } from '../data/mockData';
import { ACTUAL_GRAPH_DATA } from '../data/actualData';
import { ApiService } from '../services/api';

const SCHEMA_LEGEND = [
  { name: "Program (COBOL)", border: "#1D4ED8", bg: "#DBEAFE" },
  { name: "Package (SSIS)", border: "#047857", bg: "#D1FAE5" },
  { name: "Table / View (SQL)", border: "#6D28D9", bg: "#EDE9FE" },
  { name: "Column / Field", border: "#0891B2", bg: "#CFFAFE" },
  { name: "Business Rule", border: "#D97706", bg: "#FEF3C7" },
  { name: "Transformation", border: "#EA580C", bg: "#FFEDD5" },
];

export default function KnowledgeGraphView() {
  const [nodes, setNodes] = useState(MOCK_GRAPH_DATA.nodes || []);
  const [links, setLinks] = useState(MOCK_GRAPH_DATA.links || []);
  const [selectedNode, setSelectedNode] = useState(MOCK_GRAPH_DATA.nodes?.[0] || null);
  const [selectedScope, setSelectedScope] = useState('Full System Graph (All 21 Files)');
  const [filterType, setFilterType] = useState('(All Types)');
  const [searchQuery, setSearchQuery] = useState('');
  const [lineageFocusId, setLineageFocusId] = useState(null);
  const [copiedCypher, setCopiedCypher] = useState(false);

  const scopeOptions = [
    'Full System Graph (All 21 Files)',
    'COBOL Mainframe (All Programs)',
    'SSIS ETL Pipeline (All Packages)',
    'SQL PolicyCenter & ClaimCenter (All Scripts)',
    ...SOURCE_FILES.map(f => `File: ${f.name}`)
  ];

  const typeOptions = [
    '(All Types)',
    'Program',
    'Package',
    'Table',
    'Column',
    'BusinessRule',
    'Transformation'
  ];

  // Refresh graph to default
  const handleRefreshGraph = () => {
    setLineageFocusId(null);
    setSearchQuery('');
    setFilterType('(All Types)');
    setSelectedScope('Full System Graph (All 21 Files)');
    setSelectedNode(nodes[0]);
  };

  // Filter visible nodes
  const visibleNodes = nodes.filter(n => {
    if (lineageFocusId) {
      const isSelf = n.id === lineageFocusId;
      const isNeighbor = links.some(l => 
        (l.source === lineageFocusId && l.target === n.id) ||
        (l.target === lineageFocusId && l.source === n.id)
      );
      return isSelf || isNeighbor;
    }

    if (filterType !== '(All Types)' && n.type?.toLowerCase() !== filterType.toLowerCase()) {
      return false;
    }

    if (selectedScope.includes('COBOL') && !(n.system?.toLowerCase().includes('cobol') || n.type === 'Program')) return false;
    if (selectedScope.includes('SQL') && !(n.system?.toLowerCase().includes('sql') || n.type === 'Table' || n.type === 'Script')) return false;
    if (selectedScope.includes('SSIS') && !(n.system?.toLowerCase().includes('ssis') || n.type === 'Package')) return false;
    if (selectedScope.startsWith('File: ')) {
      const targetFile = selectedScope.replace('File: ', '').trim().toLowerCase();
      if (!(n.file?.toLowerCase().includes(targetFile) || n.label?.toLowerCase().includes(targetFile))) return false;
    }

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      return (n.label || '').toLowerCase().includes(q) || 
             (n.type || '').toLowerCase().includes(q) || 
             (n.system || '').toLowerCase().includes(q) ||
             (n.file || '').toLowerCase().includes(q);
    }
    return true;
  });

  const visibleNodeIds = new Set(visibleNodes.map(n => n.id));
  const visibleLinks = links.filter(l => 
    visibleNodeIds.has(l.source) && visibleNodeIds.has(l.target)
  );

  const getNodeColor = (type) => {
    switch(type) {
      case 'Program': return '#1D4ED8';
      case 'Package': return '#047857';
      case 'Table': return '#6D28D9';
      case 'Column': return '#0891B2';
      case 'BusinessRule': return '#D97706';
      case 'Transformation': return '#EA580C';
      default: return '#2563EB';
    }
  };

  // Connected edges for selected node
  const connectedEdges = selectedNode ? links.filter(l => l.source === selectedNode.id || l.target === selectedNode.id) : [];

  const handleCopyCypher = () => {
    if (!selectedNode) return;
    const cypher = `MATCH (n {name: '${selectedNode.label}'})-[r]-(target)\nRETURN n, r, target LIMIT 25;`;
    navigator.clipboard.writeText(cypher);
    setCopiedCypher(true);
    setTimeout(() => setCopiedCypher(false), 2000);
  };

  return (
    <div className="knowledge-graph-page">
      {/* Top Header matching Streamlit */}
      <div className="kg-top-header">
        <div>
          <h1 className="kg-main-title">Knowledge Graph Explorer</h1>
          <p className="kg-main-subtitle">
            Interactive Neo4j graph mapping COBOL programs, SSIS ETL pipelines, SQL schemas, business rules, and cross-system data lineage.
          </p>
        </div>

        <button className="btn btn-secondary btn-refresh-graph" onClick={handleRefreshGraph}>
          <RotateCcw size={14} /> Refresh Graph
        </button>
      </div>

      {/* Node Entity Schema Legend matching Streamlit */}
      <div className="glass-panel schema-legend-panel">
        <div className="schema-legend-title">Neo4j Node Entity Schema</div>
        <div className="schema-legend-pills-row">
          {SCHEMA_LEGEND.map((item, idx) => (
            <span 
              key={idx} 
              className="schema-legend-pill"
              style={{ background: item.bg, borderColor: item.border }}
            >
              <span className="legend-dot" style={{ background: item.border }} />
              <span className="legend-name">{item.name}</span>
            </span>
          ))}
        </div>
      </div>

      {/* Graph Filter & Controls Toolbar matching Streamlit */}
      <div className="kg-controls-toolbar glass-panel">
        <div className="kg-controls-row">
          {/* Scope Dropdown */}
          <div className="kg-control-group flex-2">
            <label className="field-label">Select Graph Scope:</label>
            <select
              className="form-select font-mono"
              value={selectedScope}
              onChange={(e) => setSelectedScope(e.target.value)}
            >
              {scopeOptions.map((opt, idx) => (
                <option key={idx} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          </div>

          {/* Node Type Filter */}
          <div className="kg-control-group flex-1">
            <label className="field-label">Filter Node Type:</label>
            <select
              className="form-select font-mono"
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
            >
              {typeOptions.map((opt, idx) => (
                <option key={idx} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          </div>

          {/* Search Input */}
          <div className="kg-control-group flex-1">
            <label className="field-label">Search Entity / File:</label>
            <div className="search-input-wrap">
              <Search size={14} className="search-icon" />
              <input
                type="text"
                className="form-input search-input"
                placeholder="Search node or variable..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Main Workspace: Interactive Graph Canvas + Bloom-style Inspector */}
      <div className="kg-workspace-grid">
        {/* Left Side: Interactive Canvas */}
        <div className="kg-canvas-container glass-panel">
          <div className="canvas-header-bar">
            <span className="canvas-stats font-mono">
              Displaying {visibleNodes.length} Nodes • {visibleLinks.length} Relationships
            </span>
            {lineageFocusId && (
              <button 
                className="btn-clear-focus"
                onClick={() => setLineageFocusId(null)}
              >
                Clear Lineage Focus (Show All)
              </button>
            )}
          </div>

          {/* Interactive SVG Canvas */}
          <svg className="kg-svg-canvas" viewBox="0 0 850 560">
            <defs>
              <marker id="arrow" viewBox="0 -5 10 10" refX="28" refY="0" markerWidth="6" markerHeight="6" orient="auto">
                <path d="M0,-5L10,0L0,5" fill="#94A3B8" />
              </marker>
              <marker id="arrow-active" viewBox="0 -5 10 10" refX="28" refY="0" markerWidth="6" markerHeight="6" orient="auto">
                <path d="M0,-5L10,0L0,5" fill="#2563EB" />
              </marker>
            </defs>

            {/* Render Links */}
            {visibleLinks.map((link, idx) => {
              const src = visibleNodes.find(n => n.id === link.source);
              const tgt = visibleNodes.find(n => n.id === link.target);
              if (!src || !tgt) return null;

              const isSelectedLink = selectedNode && (link.source === selectedNode.id || link.target === selectedNode.id);
              const midX = (src.x + tgt.x) / 2;
              const midY = (src.y + tgt.y) / 2;

              return (
                <g key={idx} className="graph-link-group">
                  <line
                    x1={src.x}
                    y1={src.y}
                    x2={tgt.x}
                    y2={tgt.y}
                    stroke={isSelectedLink ? '#2563EB' : '#CBD5E1'}
                    strokeWidth={isSelectedLink ? 2.2 : 1.4}
                    strokeDasharray={isSelectedLink ? 'none' : '3 3'}
                    markerEnd={isSelectedLink ? "url(#arrow-active)" : "url(#arrow)"}
                  />
                  {isSelectedLink && link.label && (
                    <text 
                      x={midX} 
                      y={midY - 5} 
                      className="edge-label-text font-mono"
                      textAnchor="middle"
                    >
                      {link.label}
                    </text>
                  )}
                </g>
              );
            })}

            {/* Render Nodes */}
            {visibleNodes.map((node) => {
              const isSelected = selectedNode?.id === node.id;
              const color = getNodeColor(node.type);

              return (
                <g 
                  key={node.id} 
                  className={`graph-node-group ${isSelected ? 'node-selected' : ''}`}
                  onClick={() => setSelectedNode(node)}
                  style={{ cursor: 'pointer' }}
                >
                  {/* Outer pulse circle when selected */}
                  {isSelected && (
                    <circle
                      cx={node.x}
                      cy={node.y}
                      r={30}
                      fill="none"
                      stroke={color}
                      strokeWidth={2.5}
                      opacity={0.6}
                      className="pulse-circle"
                    />
                  )}

                  {/* Base Circle */}
                  <circle
                    cx={node.x}
                    cy={node.y}
                    r={22}
                    fill={color}
                    stroke="#FFFFFF"
                    strokeWidth={3}
                    style={{ filter: 'drop-shadow(0 4px 6px rgba(0,0,0,0.15))' }}
                  />

                  {/* Node Label Text */}
                  <text
                    x={node.x}
                    y={node.y + 36}
                    className="graph-node-label"
                    textAnchor="middle"
                  >
                    {node.label}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>

        {/* Right Side: Neo4j Bloom-styled Node Details Inspector */}
        <div className="kg-inspector-panel glass-panel">
          {selectedNode ? (
            <div className="inspector-content">
              {/* Header with Label & Element ID */}
              <div className="inspector-header">
                <div>
                  <span className="inspector-tag-pill" style={{ background: getNodeColor(selectedNode.type) }}>
                    {selectedNode.type}
                  </span>
                  <h3 className="inspector-node-name">{selectedNode.label}</h3>
                </div>
                <button 
                  className="btn-focus-lineage" 
                  onClick={() => setLineageFocusId(selectedNode.id)}
                  title="Filter graph to show only connected neighborhood"
                >
                  <GitFork size={13} /> Focus Lineage
                </button>
              </div>

              <div className="inspector-element-id font-mono">
                Neo4j Element ID: <code>4:{absHash(selectedNode.id)}-c328-4253:1</code>
              </div>

              {/* Key-Value Properties Table matching Neo4j Bloom */}
              <div className="inspector-section">
                <div className="inspector-section-title">Node Properties</div>
                <table className="inspector-props-table font-mono">
                  <tbody>
                    <tr>
                      <td className="prop-key">name</td>
                      <td className="prop-val">{selectedNode.label}</td>
                    </tr>
                    <tr>
                      <td className="prop-key">type</td>
                      <td className="prop-val">{selectedNode.type}</td>
                    </tr>
                    <tr>
                      <td className="prop-key">file_origin</td>
                      <td className="prop-val text-cyan">{selectedNode.file || selectedNode.label}</td>
                    </tr>
                    <tr>
                      <td className="prop-key">system_layer</td>
                      <td className="prop-val">{selectedNode.system || 'Enterprise Core'}</td>
                    </tr>
                    {selectedNode.lines && (
                      <tr>
                        <td className="prop-key">line_anchor</td>
                        <td className="prop-val text-emerald">{selectedNode.lines}</td>
                      </tr>
                    )}
                    {selectedNode.formula && (
                      <tr>
                        <td className="prop-key">extracted_formula</td>
                        <td className="prop-val text-purple">{selectedNode.formula}</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>

              {/* Connected Relationships List */}
              <div className="inspector-section">
                <div className="inspector-section-title">
                  Connected Lineage Edges ({connectedEdges.length})
                </div>
                <div className="connected-edges-list">
                  {connectedEdges.map((edge, idx) => {
                    const isOutgoing = edge.source === selectedNode.id;
                    const otherNodeId = isOutgoing ? edge.target : edge.source;
                    const otherNode = nodes.find(n => n.id === otherNodeId);

                    return (
                      <div key={idx} className="edge-item font-mono">
                        <span className={`edge-direction-badge ${isOutgoing ? 'outgoing' : 'incoming'}`}>
                          {isOutgoing ? 'OUTGOING ➔' : 'INCOMING ⬅'}
                        </span>
                        <span className="edge-name-text">[:{edge.label || 'CONNECTS_TO'}]</span>
                        <span className="edge-target-text" onClick={() => otherNode && setSelectedNode(otherNode)}>
                          {otherNode?.label || otherNodeId}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="inspector-actions-row">
                <button className="btn btn-secondary flex-1" onClick={handleCopyCypher}>
                  {copiedCypher ? <Check size={14} className="text-emerald" /> : <Copy size={14} />}
                  <span>{copiedCypher ? 'Copied Cypher!' : 'Copy Cypher Query'}</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="inspector-empty-state">
              <Info size={32} className="text-muted" />
              <h4>No Node Selected</h4>
              <p>Click any node on the graph canvas to inspect full Neo4j properties and relationships.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function absHash(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash) + str.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash).toString(16).padStart(8, '0');
}
