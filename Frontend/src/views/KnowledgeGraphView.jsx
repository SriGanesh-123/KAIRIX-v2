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
  ShieldCheck
} from 'lucide-react';
import SpatialCard from '../components/SpatialCard';
import { MOCK_GRAPH_DATA } from '../data/mockData';
import { ApiService } from '../services/api';

export default function KnowledgeGraphView() {
  const [nodes, setNodes] = useState(MOCK_GRAPH_DATA.nodes || []);
  const [links, setLinks] = useState(MOCK_GRAPH_DATA.links || []);
  const [selectedNode, setSelectedNode] = useState(MOCK_GRAPH_DATA.nodes?.[0] || null);
  const [filterType, setFilterType] = useState('ALL');
  const [selectedScope, setSelectedScope] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [lineageFocusId, setLineageFocusId] = useState(null);

  const filterOptions = ['ALL', 'Program', 'Table', 'Script', 'Package'];
  const scopeOptions = [
    { id: 'ALL', label: 'Full System Graph (All 21 Files)' },
    { id: 'COBOL', label: 'COBOL Mainframe (All Programs)' },
    { id: 'SQL', label: 'SQL PolicyCenter & Claims (All Views)' },
    { id: 'SSIS', label: 'SSIS ETL Pipeline (All Packages)' }
  ];

  // Sync with live API if available
  useEffect(() => {
    ApiService.getGraph({ preset: filterType === 'ALL' ? null : filterType }).then(res => {
      if (res?.nodes?.length > 0) {
        // Overlay positions if needed
        const positionedNodes = res.nodes.map((n, idx) => {
          const match = (MOCK_GRAPH_DATA.nodes || []).find(m => m.id === n.id || m.label === n.label);
          if (match && match.x && match.y) return { ...n, ...match };
          const angle = (idx / res.nodes.length) * 2 * Math.PI;
          return {
            ...n,
            x: 400 + Math.cos(angle) * 250,
            y: 220 + Math.sin(angle) * 160
          };
        });
        setNodes(positionedNodes);
        if (res.edges?.length > 0) {
          setLinks(res.edges.map(e => ({
            source: e.source,
            target: e.target,
            label: e.label || 'CONNECTS_TO'
          })));
        }
      }
    });
  }, [filterType]);

  // Compute filtered visible nodes
  const visibleNodes = nodes.filter(n => {
    if (lineageFocusId) {
      const isSelf = n.id === lineageFocusId;
      const isNeighbor = links.some(l => 
        (l.source === lineageFocusId && l.target === n.id) ||
        (l.target === lineageFocusId && l.source === n.id)
      );
      return isSelf || isNeighbor;
    }
    if (filterType !== 'ALL' && n.type?.toLowerCase() !== filterType.toLowerCase()) {
      return false;
    }
    if (selectedScope === 'COBOL' && !(n.system?.toLowerCase().includes('cobol') || n.type === 'Program')) return false;
    if (selectedScope === 'SQL' && !(n.system?.toLowerCase().includes('sql') || n.type === 'Script')) return false;
    if (selectedScope === 'SSIS' && !(n.system?.toLowerCase().includes('ssis') || n.type === 'Package')) return false;
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

  // Compute visible edges
  const visibleLinks = links.filter(l => 
    visibleNodeIds.has(l.source) && visibleNodeIds.has(l.target)
  );

  const getNodeColor = (type) => {
    switch(type) {
      case 'Program': return '#0284c7';      /* Deep Cyan */
      case 'Table': return '#059669';        /* Emerald */
      case 'Script': return '#2563eb';       /* Royal Blue */
      case 'Package': return '#7c3aed';      /* Purple */
      case 'BusinessRule': return '#d97706'; /* Amber */
      default: return '#64748b';
    }
  };

  const handleTraceLineage = (nodeId) => {
    setLineageFocusId(nodeId === lineageFocusId ? null : nodeId);
  };

  const handleReset = () => {
    setLineageFocusId(null);
    setSearchQuery('');
    setFilterType('ALL');
    setSelectedScope('ALL');
    setSelectedNode(nodes[0]);
  };

  return (
    <div className="graph-view-container">
      {/* 1. Cloud Banner Header (Neo4j AuraDB Active Connection) */}
      <div className="glass-panel" style={{ padding: '16px 22px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className="pulse-dot pulse-emerald" style={{ width: '10px', height: '10px' }} />
          <div>
            <div style={{ fontWeight: '800', fontSize: '14.5px', color: '#0f172a' }}>
              Neo4j AuraDB Cloud Active
            </div>
            <div style={{ fontSize: '11.5px', color: '#64748b', fontFamily: 'JetBrains Mono' }}>
              Instance: 03f0aac2 • 1,006 Nodes • 2,822 Relationships • neo4j+s://03f0aac2.databases.neo4j.io
            </div>
          </div>
        </div>

        <a 
          href="https://workspace.neo4j.io/workspace/explore?connectURL=neo4j%2Bs%3A%2F%2F03f0aac2.databases.neo4j.io" 
          target="_blank" 
          rel="noopener noreferrer"
          className="btn btn-primary btn-sm"
        >
          <ExternalLink size={13} />
          Open Neo4j Aura Workspace ↗
        </a>
      </div>

      {/* 2. Control Bar: Search + Scope Dropdown + Filter Pills + Reset */}
      <div className="graph-top-bar glass-panel">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1, minWidth: '240px' }}>
          <div style={{ position: 'relative', width: '100%', maxWidth: '280px' }}>
            <Search size={14} style={{ position: 'absolute', left: '12px', top: '12px', color: '#94a3b8' }} />
            <input
              type="text"
              placeholder="Search Node / File..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="investigation-input"
              style={{ paddingLeft: '34px', paddingRight: '12px', height: '38px', fontSize: '13px' }}
            />
          </div>

          <select 
            value={selectedScope} 
            onChange={(e) => setSelectedScope(e.target.value)}
            className="source-file-select"
            style={{ height: '38px', minWidth: '220px', padding: '0 14px', fontSize: '12.5px' }}
          >
            {scopeOptions.map(opt => (
              <option key={opt.id} value={opt.id}>{opt.label}</option>
            ))}
          </select>
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
          <button 
            onClick={handleReset} 
            className="btn btn-glass btn-sm"
            title="Reset Filters & Focus"
          >
            <RotateCcw size={13} /> Reset
          </button>
        </div>
      </div>

      {/* 3. Main Graph Layout: SVG Canvas (70%) + Inspector (30%) */}
      <div className="graph-main-layout">
        {/* Spatial 2D/3D Network Canvas */}
        <div className="glass-panel graph-canvas-panel">
          <div className="canvas-header-overlay">
            <div className="live-graph-badge">
              <span className="pulse-dot pulse-cyan" />
              <span>CANVAS: <b style={{ color: '#2563eb' }}>{visibleNodes.length}</b> NODES • <b style={{ color: '#7c3aed' }}>{visibleLinks.length}</b> RELATIONSHIPS</span>
              {lineageFocusId && (
                <span className="badge badge-purple" style={{ marginLeft: '10px' }}>
                  Lineage Trace Active
                </span>
              )}
            </div>
            <div className="canvas-legend">
              <span className="legend-item"><span className="legend-dot" style={{ background: '#0284c7' }} /> Program</span>
              <span className="legend-item"><span className="legend-dot" style={{ background: '#059669' }} /> Table</span>
              <span className="legend-item"><span className="legend-dot" style={{ background: '#2563eb' }} /> Script</span>
              <span className="legend-item"><span className="legend-dot" style={{ background: '#7c3aed' }} /> Package</span>
              <span className="legend-item"><span className="legend-dot" style={{ background: '#d97706' }} /> Rule</span>
            </div>
          </div>

          {/* Interactive SVG Graph */}
          <svg className="spatial-network-svg" viewBox="0 0 800 450">
            <defs>
              <linearGradient id="edgeGlow" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#2563eb" stopOpacity="0.8" />
                <stop offset="100%" stopColor="#7c3aed" stopOpacity="0.8" />
              </linearGradient>
            </defs>

            {/* Render Links */}
            {visibleLinks.map((link, idx) => {
              const sourceNode = nodes.find(n => n.id === link.source);
              const targetNode = nodes.find(n => n.id === link.target);
              if (!sourceNode || !targetNode) return null;

              const isConnected = selectedNode && (selectedNode.id === sourceNode.id || selectedNode.id === targetNode.id);

              return (
                <g key={`link-${idx}`}>
                  <line
                    x1={sourceNode.x}
                    y1={sourceNode.y}
                    x2={targetNode.x}
                    y2={targetNode.y}
                    stroke={isConnected ? "url(#edgeGlow)" : "rgba(148, 163, 184, 0.4)"}
                    strokeWidth={isConnected ? "2.5" : "1.5"}
                    strokeDasharray={isConnected ? "5 3" : "none"}
                  />
                  <text
                    x={(sourceNode.x + targetNode.x) / 2}
                    y={(sourceNode.y + targetNode.y) / 2 - 6}
                    fill={isConnected ? "#2563eb" : "#64748b"}
                    fontSize="9"
                    fontFamily="JetBrains Mono"
                    fontWeight="700"
                    textAnchor="middle"
                  >
                    {link.label}
                  </text>
                </g>
              );
            })}

            {/* Render Nodes */}
            {visibleNodes.map((node) => {
              const isSelected = selectedNode?.id === node.id;
              const color = getNodeColor(node.type);

              return (
                <g 
                  key={`node-${node.id}`} 
                  transform={`translate(${node.x}, ${node.y})`}
                  onClick={() => setSelectedNode(node)}
                  className="graph-node-group"
                  style={{ cursor: 'pointer' }}
                >
                  {/* Outer pulse ring for selected node */}
                  {isSelected && (
                    <circle
                      r="24"
                      fill="none"
                      stroke={color}
                      strokeWidth="2.5"
                      opacity="0.8"
                    />
                  )}
                  {/* Node shadow/glow */}
                  <circle
                    r="16"
                    fill={color}
                    opacity={isSelected ? "0.3" : "0.15"}
                  />
                  {/* Core circle */}
                  <circle
                    r="13"
                    fill="#ffffff"
                    stroke={color}
                    strokeWidth={isSelected ? "3" : "2"}
                  />
                  {/* Node Label Text */}
                  <text
                    y="27"
                    fill={isSelected ? "#0f172a" : "#334155"}
                    fontSize="11"
                    fontFamily="Outfit"
                    fontWeight={isSelected ? "800" : "600"}
                    textAnchor="middle"
                  >
                    {node.label}
                  </text>
                  <text
                    y="38"
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

        {/* Node Inspector Sidebar Panel */}
        <div className="glass-panel node-inspector-panel">
          <div className="inspector-header">
            <div className="badge badge-cyan">Entity Inspector</div>
            <span className="live-indicator">Neo4j Aura Node</span>
          </div>

          {selectedNode ? (
            <div className="inspector-body">
              <h3 className="inspector-node-name">{selectedNode.label}</h3>

              <div className="inspector-meta-row">
                <span className="meta-label">Node Type</span>
                <span className="badge" style={{ background: '#e0e7ff', color: getNodeColor(selectedNode.type) }}>
                  :{selectedNode.type}
                </span>
              </div>

              <div className="inspector-meta-row">
                <span className="meta-label">Architecture Tier</span>
                <span className="meta-val">{selectedNode.system}</span>
              </div>

              <div className="inspector-meta-row">
                <span className="meta-label">Source File</span>
                <span className="meta-val font-mono">{selectedNode.file}</span>
              </div>

              <div className="inspector-meta-row">
                <span className="meta-label">Business Rules</span>
                <span className="meta-val text-blue font-mono">{selectedNode.rules} Rules</span>
              </div>

              <div className="inspector-meta-row">
                <span className="meta-label">Status</span>
                <span className="meta-val text-emerald">
                  <Check size={13} style={{ display: 'inline', marginRight: 4 }} />
                  Indexed & Active
                </span>
              </div>

              <div className="inspector-divider" />

              <h4 className="inspector-subtitle">Active Lineage Connections</h4>
              <div className="inspector-relations-list">
                {links
                  .filter(l => l.source === selectedNode.id || l.target === selectedNode.id)
                  .map((link, idx) => {
                    const isOutgoing = link.source === selectedNode.id;
                    const neighborId = isOutgoing ? link.target : link.source;
                    const neighborNode = nodes.find(n => n.id === neighborId);

                    return (
                      <div 
                        key={idx} 
                        className="relation-item" 
                        onClick={() => neighborNode && setSelectedNode(neighborNode)}
                        style={{ cursor: 'pointer' }}
                        title="Click to inspect this node"
                      >
                        <span className="relation-type font-mono">{link.label}</span>
                        <span className="relation-target">
                          {isOutgoing ? `➔ ${neighborNode?.label || neighborId}` : `⬅ from ${neighborNode?.label || neighborId}`}
                        </span>
                      </div>
                    );
                  })}
              </div>

              <div className="inspector-divider" />

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '14px' }}>
                <button 
                  className="btn btn-primary btn-sm w-full"
                  onClick={() => handleTraceLineage(selectedNode.id)}
                >
                  <GitFork size={13} />
                  {lineageFocusId === selectedNode.id ? "Show All Nodes" : "Trace Extended Lineage"}
                </button>
              </div>
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
