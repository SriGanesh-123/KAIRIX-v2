import React, { useState, useEffect, useMemo } from 'react';
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
  Maximize2,
  RefreshCw,
  AlertTriangle,
  Sparkles
} from 'lucide-react';
import GraphView from '../components/GraphView';
import { getNodeColor } from '../utils/graphTheme';
import { useGraphData } from '../hooks/useGraphData';
import { SOURCE_FILES } from '../data/mockData';

const SCHEMA_LEGEND = [
  { name: "Program (COBOL)", border: "#1D4ED8", bg: "#DBEAFE" },
  { name: "Package (SSIS)", border: "#047857", bg: "#D1FAE5" },
  { name: "Table / View (SQL)", border: "#6D28D9", bg: "#EDE9FE" },
  { name: "Column / Field", border: "#0891B2", bg: "#CFFAFE" },
  { name: "Business Rule", border: "#D97706", bg: "#FEF3C7" },
  { name: "Transformation", border: "#EA580C", bg: "#FFEDD5" },
];

export default function KnowledgeGraphView() {
  const {
    nodes,
    links,
    schema,
    isLoading,
    error,
    loadingProgress,
    reloadGraph,
    expandNodeNeighbors,
  } = useGraphData();

  const [viewLayer, setViewLayer] = useState('architecture'); // 'architecture' (clean ~471 nodes) | 'full' (all 1,827 AST nodes)
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedScope, setSelectedScope] = useState('Full System Graph (All 21 Files)');
  const [filterType, setFilterType] = useState('(All Types)');
  const [searchQuery, setSearchQuery] = useState('');
  const [lineageFocusId, setLineageFocusId] = useState(null);
  const [copiedCypher, setCopiedCypher] = useState(false);
  const [isPaused, setIsPaused] = useState(false);

  // Set default selected node once nodes load
  useEffect(() => {
    if (!selectedNode && nodes.length > 0) {
      // Prefer an interesting entity like EARNPREM.CBL or CALCULATE-EARNED if present
      const preferred = nodes.find(n => n.label?.includes('EARNPREM') || n.label?.includes('PREMCALC')) || nodes[0];
      setSelectedNode(preferred);
    }
  }, [nodes, selectedNode]);

  const scopeOptions = [
    'Full System Graph (All 21 Files)',
    'COBOL Mainframe (All Programs)',
    'SSIS ETL Pipeline (All Packages)',
    'SQL PolicyCenter & ClaimCenter (All Scripts)',
    ...SOURCE_FILES.map(f => `File: ${f.name}`)
  ];

  // Derive dynamic type filter options from schema labels + standard labels
  const typeOptions = useMemo(() => {
    const base = ['(All Types)'];
    const labelSet = new Set(['Program', 'Package', 'Table', 'Column', 'BusinessRule', 'Transformation']);
    if (schema?.labels) {
      for (const l of schema.labels) labelSet.add(l);
    }
    return [...base, ...Array.from(labelSet)];
  }, [schema]);

  // Compute count of architectural nodes (Artifacts, Rules, Transforms, CodeBlocks, Tables)
  const archCount = useMemo(() => {
    return nodes.filter(n => 
      n.type === 'Artifact' || n.labels?.includes('Artifact') ||
      n.type === 'BusinessRule' || n.labels?.includes('BusinessRule') ||
      n.type === 'Transformation' || n.labels?.includes('Transformation') ||
      n.type === 'CodeBlock' || n.labels?.includes('CodeBlock') ||
      n.type === 'Table' || n.labels?.includes('Table') ||
      n.type === 'View' || n.labels?.includes('View')
    ).length;
  }, [nodes]);

  // Refresh graph to default
  const handleRefreshGraph = () => {
    setLineageFocusId(null);
    setSearchQuery('');
    setFilterType('(All Types)');
    setSelectedScope('Full System Graph (All 21 Files)');
    setViewLayer('architecture');
    if (nodes.length > 0) setSelectedNode(nodes[0]);
    reloadGraph();
  };

  // Filter visible nodes based on Scope, Type, Lineage Focus, Search, and Abstraction Layer
  const visibleNodes = useMemo(() => {
    return nodes.filter(n => {
      // Lineage neighborhood focus takes precedence
      if (lineageFocusId) {
        const isSelf = n.id === lineageFocusId;
        const isNeighbor = links.some(l => {
          const s = typeof l.source === 'object' ? l.source.id : l.source;
          const t = typeof l.target === 'object' ? l.target.id : l.target;
          return (s === lineageFocusId && t === n.id) || (t === lineageFocusId && s === n.id);
        });
        return isSelf || isNeighbor;
      }

      // Filter by Node Type / Label
      if (filterType !== '(All Types)') {
        const nodeTypeMatches = n.type?.toLowerCase() === filterType.toLowerCase() ||
          (n.labels && n.labels.some(lbl => lbl.toLowerCase() === filterType.toLowerCase()));
        if (!nodeTypeMatches) return false;
      }

      // Scope filters
      const sys = (n.system || '').toLowerCase();
      const lbl = (n.label || '').toLowerCase();
      const typ = (n.type || '').toLowerCase();

      if (selectedScope.includes('COBOL') && !(sys.includes('cobol') || typ === 'program' || n.labels?.includes('COBOL') || n.file?.toLowerCase().endsWith('.cbl'))) {
        return false;
      }
      if (selectedScope.includes('SQL') && !(sys.includes('sql') || typ === 'table' || typ === 'script' || n.labels?.includes('Table') || n.file?.toLowerCase().endsWith('.sql'))) {
        return false;
      }
      if (selectedScope.includes('SSIS') && !(sys.includes('ssis') || typ === 'package' || n.labels?.includes('Package') || n.file?.toLowerCase().endsWith('.dtsx'))) {
        return false;
      }
      if (selectedScope.startsWith('File: ')) {
        const targetFile = selectedScope.replace('File: ', '').trim().toLowerCase();
        const matchesFile = (n.file || '').toLowerCase().includes(targetFile) || lbl.includes(targetFile);
        if (!matchesFile) return false;
      }

      // Search query (overrides abstraction layer so searched AST items are always discovered)
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        return lbl.includes(q) || 
               typ.includes(q) || 
               sys.includes(q) ||
               (n.file || '').toLowerCase().includes(q) ||
               (n.id || '').toLowerCase().includes(q);
      }

      // Abstraction Layer Filter:
      // When in 'architecture' mode (and not drilled into a specific single file),
      // keep only high-level architecture: Artifacts (files), BusinessRules, Transformations, CodeBlocks, and Tables/Views.
      // This filters out 1,200 micro-AST variables so the architecture is immediately clean, readable, and structured.
      if (viewLayer === 'architecture' && !selectedScope.startsWith('File: ')) {
        const isCoreArtifact = n.type === 'Artifact' || n.labels?.includes('Artifact');
        const isRule = n.type === 'BusinessRule' || n.labels?.includes('BusinessRule');
        const isTransform = n.type === 'Transformation' || n.labels?.includes('Transformation');
        const isBlock = n.type === 'CodeBlock' || n.labels?.includes('CodeBlock');
        const isTable = n.type === 'Table' || n.labels?.includes('Table') || n.type === 'View' || n.labels?.includes('View');
        const isBridge = (n.degree && n.degree >= 2);

        if (!isCoreArtifact && !isRule && !isTransform && !isBlock && !isTable && !isBridge) {
          return false;
        }
      }

      return true;
    });
  }, [nodes, links, lineageFocusId, filterType, selectedScope, searchQuery, viewLayer]);

  // Derive visible links whose source and target both exist in visibleNodes
  const visibleLinks = useMemo(() => {
    const visibleNodeIds = new Set(visibleNodes.map(n => n.id));
    return links.filter(l => {
      const s = typeof l.source === 'object' ? l.source.id : l.source;
      const t = typeof l.target === 'object' ? l.target.id : l.target;
      return visibleNodeIds.has(s) && visibleNodeIds.has(t);
    });
  }, [visibleNodes, links]);

  // Connected edges for selected node
  const connectedEdges = useMemo(() => {
    if (!selectedNode) return [];
    return links.filter(l => {
      const s = typeof l.source === 'object' ? l.source.id : l.source;
      const t = typeof l.target === 'object' ? l.target.id : l.target;
      return s === selectedNode.id || t === selectedNode.id;
    });
  }, [selectedNode, links]);

  // Exact search node match for centering
  const searchMatchId = useMemo(() => {
    if (!searchQuery.trim()) return null;
    const q = searchQuery.toLowerCase();
    const exact = visibleNodes.find(n => n.label?.toLowerCase() === q || n.id?.toLowerCase() === q);
    if (exact) return exact.id;
    const partial = visibleNodes.find(n => n.label?.toLowerCase().includes(q));
    return partial?.id || null;
  }, [searchQuery, visibleNodes]);

  const handleCopyCypher = () => {
    if (!selectedNode) return;
    const cypher = `MATCH (n {name: '${selectedNode.label}'})-[r]-(target)\nRETURN n, r, target LIMIT 25;`;
    navigator.clipboard.writeText(cypher);
    setCopiedCypher(true);
    setTimeout(() => setCopiedCypher(false), 2000);
  };

  const handleExpandNode = async (nodeId) => {
    await expandNodeNeighbors(nodeId);
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

        <button className="btn btn-secondary btn-refresh-graph" onClick={handleRefreshGraph} disabled={isLoading}>
          <RotateCcw size={14} className={isLoading ? "spin-icon" : ""} /> 
          <span>{isLoading ? 'Loading Aura...' : 'Refresh Graph'}</span>
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

      {/* Abstraction View Layer Segmented Control */}
      <div className="kg-view-layer-selector">
        <div className="view-layer-tabs">
          <button 
            type="button"
            className={`view-layer-tab ${viewLayer === 'architecture' ? 'active' : ''}`}
            onClick={() => setViewLayer('architecture')}
            title="Clean, high-level architecture with programs, ETL packages, business rules, and transformations"
          >
            <Sparkles size={14} className="tab-icon" />
            <span className="tab-title">Architecture & Rules</span>
            <span className="tab-badge">{archCount > 0 ? `${archCount} Nodes` : '471'}</span>
          </button>
          <button 
            type="button"
            className={`view-layer-tab ${viewLayer === 'full' ? 'active' : ''}`}
            onClick={() => setViewLayer('full')}
            title="Complete compiler AST graph including granular variables, statements, loops, and branches"
          >
            <Layers size={14} className="tab-icon" />
            <span className="tab-title">Full AST Graph (All Nodes)</span>
            <span className="tab-badge">{nodes.length > 0 ? `${nodes.length.toLocaleString()}` : '1,827'}</span>
          </button>
        </div>
        <div className="view-layer-hint">
          {viewLayer === 'architecture' ? (
            <span>✨ Showing high-level topology: Programs, SSIS packages, SQL scripts, business rules & transformations</span>
          ) : (
            <span>🔬 Showing deep compiler AST: All codeblocks, statements, branches, loops & variables</span>
          )}
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
        {/* Left Side: Interactive Force-Directed Canvas */}
        <div className="kg-canvas-container glass-panel">
          <div className="canvas-header-bar">
            <div className="canvas-header-left">
              <span className="kg-live-badge">
                <span className="kg-live-dot" />
                Neo4j Aura Live
              </span>
              <span className="canvas-stats font-mono">
                Displaying {visibleNodes.length.toLocaleString()} Nodes • {visibleLinks.length.toLocaleString()} Relationships
                {nodes.length > 0 && ` (Total: ${nodes.length.toLocaleString()} nodes in DB)`}
              </span>
            </div>
            {lineageFocusId && (
              <button 
                className="btn-clear-focus"
                onClick={() => setLineageFocusId(null)}
              >
                Clear Lineage Focus (Show All)
              </button>
            )}
          </div>

          {/* Progressive Streaming Loading Banner */}
          {isLoading && nodes.length > 0 && (
            <div className="kg-progressive-load-strip font-mono">
              <span>Streaming graph: {loadingProgress.loadedNodes.toLocaleString()} / {loadingProgress.totalNodes.toLocaleString()} nodes ({loadingProgress.percentage}%)</span>
              <div className="kg-mini-progress">
                <div className="kg-mini-fill" style={{ width: `${loadingProgress.percentage}%` }} />
              </div>
            </div>
          )}

          {/* Canvas or Initial Loading / Error States */}
          {isLoading && nodes.length === 0 ? (
            <div className="kg-loading-overlay">
              <div className="kg-spinner" />
              <h4 className="kg-loading-title">Connecting to Neo4j Aura Cloud...</h4>
              <p className="kg-loading-subtitle">Querying AST nodes, business rules, and multi-tier lineage</p>
              <div className="kg-progress-bar-track">
                <div 
                  className="kg-progress-bar-fill" 
                  style={{ width: `${loadingProgress.percentage}%` }} 
                />
              </div>
              <div className="kg-progress-text font-mono">
                {loadingProgress.phase}
              </div>
            </div>
          ) : error && nodes.length === 0 ? (
            <div className="kg-error-overlay">
              <AlertTriangle size={36} className="text-amber" />
              <h4>Neo4j Aura Connection Error</h4>
              <p className="error-message-text">{error}</p>
              <button className="btn btn-primary" onClick={reloadGraph}>
                <RotateCcw size={14} /> Retry Connection
              </button>
            </div>
          ) : (
            <GraphView
              nodes={visibleNodes}
              links={visibleLinks}
              selectedNode={selectedNode}
              onSelectNode={setSelectedNode}
              onExpandNode={handleExpandNode}
              lineageFocusId={lineageFocusId}
              focusSearchId={searchMatchId}
              isPaused={isPaused}
              onTogglePause={setIsPaused}
            />
          )}
        </div>

        {/* Right Side: Neo4j Bloom-styled Node Details Inspector */}
        <div className="kg-inspector-panel glass-panel">
          {selectedNode ? (
            <div className="inspector-content">
              {/* Header with Label & Type */}
              <div className="inspector-header">
                <div>
                  <span className="inspector-tag-pill" style={{ background: getNodeColor(selectedNode.type) }}>
                    {selectedNode.type || 'Entity'}
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
                Neo4j ID: <code>{selectedNode.id}</code>
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
                    {selectedNode.file && (
                      <tr>
                        <td className="prop-key">source_file</td>
                        <td className="prop-val text-cyan">{selectedNode.file}</td>
                      </tr>
                    )}
                    {selectedNode.system && (
                      <tr>
                        <td className="prop-key">system_layer</td>
                        <td className="prop-val">{selectedNode.system}</td>
                      </tr>
                    )}
                    {selectedNode.degree !== undefined && (
                      <tr>
                        <td className="prop-key">connected_degree</td>
                        <td className="prop-val text-emerald">{selectedNode.degree} links</td>
                      </tr>
                    )}
                    {/* Render any additional dynamic Neo4j properties */}
                    {Object.entries(selectedNode.properties || {})
                      .filter(([k]) => !['name', 'label', 'type', 'id', 'system', 'system_layer', 'source_file', 'file'].includes(k))
                      .slice(0, 10)
                      .map(([k, v]) => (
                        <tr key={k}>
                          <td className="prop-key">{k}</td>
                          <td className="prop-val text-purple">
                            {typeof v === 'object' ? JSON.stringify(v) : String(v)}
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>

              {/* Connected Relationships List */}
              <div className="inspector-section">
                <div className="inspector-section-title">
                  Connected Lineage Edges ({connectedEdges.length})
                </div>
                <div className="connected-edges-list">
                  {connectedEdges.length === 0 ? (
                    <div className="empty-edges-notice font-mono">No connected edges in current scope</div>
                  ) : (
                    connectedEdges.slice(0, 25).map((edge, idx) => {
                      const s = typeof edge.source === 'object' ? edge.source.id : edge.source;
                      const t = typeof edge.target === 'object' ? edge.target.id : edge.target;
                      const isOutgoing = s === selectedNode.id;
                      const otherNodeId = isOutgoing ? t : s;
                      const otherNode = nodes.find(n => n.id === otherNodeId);

                      return (
                        <div key={idx} className="edge-item font-mono">
                          <span className={`edge-direction-badge ${isOutgoing ? 'outgoing' : 'incoming'}`}>
                            {isOutgoing ? 'OUTGOING ➔' : 'INCOMING ⬅'}
                          </span>
                          <span className="edge-name-text">[:{edge.label || edge.type || 'CONNECTS_TO'}]</span>
                          <span 
                            className="edge-target-text" 
                            onClick={() => otherNode && setSelectedNode(otherNode)}
                            title="Click to select target node"
                          >
                            {otherNode?.label || otherNodeId}
                          </span>
                        </div>
                      );
                    })
                  )}
                  {connectedEdges.length > 25 && (
                    <div className="more-edges-indicator font-mono">
                      + {connectedEdges.length - 25} more relationships
                    </div>
                  )}
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
