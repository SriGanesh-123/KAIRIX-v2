import React, { useRef, useState, useEffect, useCallback, useMemo } from 'react';
import { Network, DataSet } from 'vis-network/standalone';
import 'vis-network/styles/vis-network.css';
import { 
  Maximize2, 
  ZoomIn, 
  ZoomOut, 
  Zap, 
  ZapOff,
  Sparkles,
  RotateCcw
} from 'lucide-react';

import { NODE_PALETTE, EDGE_PALETTE } from '../utils/graphTheme';

function escapeHtml(text) {
  if (text === null || text === undefined) return '';
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

export default function GraphView({
  nodes = [],
  links = [],
  selectedNode = null,
  onSelectNode = () => {},
  onExpandNode = () => {},
  lineageFocusId = null,
  focusSearchId = null,
  isPaused = false,
  onTogglePause = () => {},
}) {
  const containerRef = useRef(null);
  const networkRef = useRef(null);
  const nodesDataSetRef = useRef(null);
  const edgesDataSetRef = useRef(null);
  const [physicsActive, setPhysicsActive] = useState(!isPaused);
  const [isStabilizing, setIsStabilizing] = useState(false);

  // Helper to build intelligent, human-readable node display and styling
  const buildNodePayload = useCallback((n, isSelected) => {
    const rawId = String(n.id || 'unknown');
    const rawLabel = String(n.label || n.properties?.name || n.properties?.id || rawId);
    
    // Determine node type
    let nodeType = n.type || (n.labels && n.labels[0]) || 'Entity';
    const lowerFile = String(n.file || n.properties?.source_file || n.properties?.file_name || '').toLowerCase();
    const lowerLabel = rawLabel.toLowerCase();

    if (nodeType === 'Artifact' || lowerLabel.endsWith('.cbl') || lowerLabel.endsWith('.cob') || lowerFile.endsWith('.cbl')) {
      if (lowerLabel.endsWith('.dtsx') || lowerFile.endsWith('.dtsx')) nodeType = 'Package';
      else if (lowerLabel.endsWith('.sql') || lowerFile.endsWith('.sql')) nodeType = 'Table';
      else if (lowerLabel.endsWith('.cbl') || lowerFile.endsWith('.cbl')) nodeType = 'Program';
      else nodeType = 'Artifact';
    } else if (String(nodeType).toLowerCase().includes('rule') || lowerLabel.startsWith('rule:')) {
      nodeType = 'BusinessRule';
    } else if (String(nodeType).toLowerCase().includes('transform') || lowerLabel.startsWith('transform:')) {
      nodeType = 'Transformation';
    }

    // Build intelligent, clean display label
    let displayLabel = rawLabel;
    if (rawLabel.startsWith('RULE:')) {
      const parts = rawLabel.split(':');
      displayLabel = `Rule ${parts[2] || parts[1] || '0'}`;
    } else if (rawLabel.startsWith('TRANSFORM:')) {
      const parts = rawLabel.split(':');
      displayLabel = `T: ${parts[2] || parts[1] || '1'}`;
    } else if (rawLabel.startsWith('BRANCH:')) {
      const parts = rawLabel.split(':');
      displayLabel = `Branch L${parts[2] || parts[1] || ''}`;
    } else if (rawLabel.startsWith('LOOP:')) {
      const parts = rawLabel.split(':');
      displayLabel = `Loop L${parts[2] || parts[1] || ''}`;
    } else if (rawLabel.startsWith('STMT:')) {
      const parts = rawLabel.split(':');
      displayLabel = `${parts[2] || 'Stmt'} L${parts[3] || ''}`;
    } else if (n.properties?.name) {
      displayLabel = n.properties.name;
    }

    if (displayLabel.length > 22) {
      displayLabel = `${displayLabel.slice(0, 20)}...`;
    }

    const colorCfg = NODE_PALETTE[nodeType] || NODE_PALETTE.Entity;
    const isProgramOrPackage = nodeType === 'Artifact' || nodeType === 'Program' || nodeType === 'Package' || nodeType === 'Table';
    const baseSize = isProgramOrPackage ? 30 : (nodeType === 'BusinessRule' || nodeType === 'Transformation' ? 24 : 17);
    const nodeSize = isSelected ? baseSize + 6 : baseSize;

    // Rich HTML Tooltip matching Streamlit Neo4j Bloom panel
    const descVal = n.properties?.description || n.properties?.purpose || n.description || '';
    const exprVal = n.properties?.expression || n.properties?.formula || n.expression || '';
    const ruleIdVal = n.properties?.rule_id || n.rule_id || '';

    const tooltipEl = document.createElement('div');
    tooltipEl.innerHTML = `
      <div style="background:#181C24; border:1px solid #38BDF8; border-radius:8px; padding:9px 13px; color:#F1F5F9; font-family:-apple-system,sans-serif; max-width:320px; box-shadow:0 8px 24px rgba(0,0,0,0.55);">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
          <span style="background:${colorCfg.border}; color:#FFFFFF; font-size:10px; font-weight:700; padding:2px 8px; border-radius:10px;">${escapeHtml(nodeType)}</span>
          <span style="color:#64748B; font-family:monospace; font-size:9.5px;">${escapeHtml(rawId.slice(0, 16))}</span>
        </div>
        <div style="font-weight:700; color:#FFFFFF; font-size:13px; margin-bottom:2px; word-break:break-word;">${escapeHtml(rawLabel)}</div>
        ${n.file ? `<div style="color:#94A3B8; font-size:11px; margin-bottom:4px;">Source: <span style="color:#38BDF8; font-family:monospace;">${escapeHtml(n.file)}</span></div>` : ''}
        ${descVal ? `<div style="color:#CBD5E1; font-size:11px; margin-bottom:4px; line-height:1.4;">${escapeHtml(descVal.slice(0, 160))}</div>` : ''}
        ${exprVal ? `
          <div style="background:#0F172A; border-left:3px solid #F59E0B; border-radius:4px; padding:5px 8px; margin-top:4px;">
            <div style="color:#F59E0B; font-weight:700; font-size:9.5px; margin-bottom:2px;">⚡ LOGIC ${ruleIdVal ? `(${escapeHtml(ruleIdVal)})` : ''}</div>
            <div style="font-family:monospace; font-size:10.5px; color:#FEF3C7; word-break:break-all;">${escapeHtml(exprVal)}</div>
          </div>
        ` : ''}
      </div>
    `;

    return {
      id: rawId,
      label: displayLabel,
      title: tooltipEl,
      size: nodeSize,
      shape: 'dot',
      color: {
        background: isSelected ? '#FDE047' : colorCfg.bg,
        border: isSelected ? '#CA8A04' : colorCfg.border,
        highlight: { background: colorCfg.highlight, border: '#0284C7' },
        hover: { background: colorCfg.highlight, border: '#0284C7' },
      },
      font: {
        color: '#0F172A',
        size: isProgramOrPackage ? 13 : 11,
        face: 'Inter, -apple-system, sans-serif',
        strokeWidth: 3,
        strokeColor: '#FFFFFF',
      },
      borderWidth: isSelected ? 3.5 : 2.0,
      rawNode: n,
    };
  }, []);

  // Main Vis.js Network lifecycle: creates or updates the network smoothly
  useEffect(() => {
    if (!containerRef.current || !nodes.length) return;

    const selectedId = selectedNode?.id || lineageFocusId || null;
    const formattedNodes = nodes.map(n => buildNodePayload(n, String(n.id) === String(selectedId)));
    const validNodeIds = new Set(formattedNodes.map(n => n.id));
    const formattedEdges = [];
    const seenEdges = new Set();

    for (let i = 0; i < links.length; i++) {
      const l = links[i];
      const srcId = String(typeof l.source === 'object' ? l.source.id : l.source);
      const tgtId = String(typeof l.target === 'object' ? l.target.id : l.target);
      const relType = String(l.type || l.label || 'RELATES_TO');

      if (validNodeIds.has(srcId) && validNodeIds.has(tgtId)) {
        const edgeKey = `${srcId}->${tgtId}:${relType}`;
        if (!seenEdges.has(edgeKey)) {
          seenEdges.add(edgeKey);
          const cfg = EDGE_PALETTE[relType] || EDGE_PALETTE.DEFAULT;
          const isConnectedToFocus = selectedId && (srcId === String(selectedId) || tgtId === String(selectedId));

          formattedEdges.push({
            id: `edge_${i}`,
            from: srcId,
            to: tgtId,
            label: relType,
            color: {
              color: isConnectedToFocus ? '#0284C7' : cfg.color,
              highlight: '#0284C7',
              hover: '#0284C7',
            },
            arrows: { to: { enabled: true, scaleFactor: 0.75 } },
            font: {
              color: '#1E293B',
              size: 10,
              align: 'middle',
              strokeWidth: 3,
              strokeColor: '#FFFFFF',
              background: 'rgba(255, 255, 255, 0.92)',
              face: 'JetBrains Mono, monospace, sans-serif',
            },
            width: isConnectedToFocus ? 2.5 : cfg.width,
            smooth: { enabled: true, type: 'continuous', roundness: 0.15 },
          });
        }
      }
    }

    const isLarge = formattedNodes.length > 150;
    const options = {
      layout: {
        improvedLayout: !isLarge,
        randomSeed: 42,
      },
      physics: {
        enabled: physicsActive,
        solver: 'barnesHut',
        barnesHut: {
          gravitationalConstant: isLarge ? -4000 : -2800,
          centralGravity: isLarge ? 0.08 : 0.15,
          springLength: isLarge ? 140 : 100,
          springConstant: isLarge ? 0.025 : 0.04,
          damping: 0.18,
          avoidOverlap: 0.85,
        },
        maxVelocity: 30,
        minVelocity: 1.0,
        stabilization: {
          enabled: true,
          iterations: 35,
          updateInterval: 10,
          fit: true,
        },
      },
      interaction: {
        hover: true,
        hoverConnectedEdges: true,
        selectConnectedEdges: true,
        navigationButtons: false,
        keyboard: false,
        zoomView: true,
        dragView: true,
        dragNodes: true,
        tooltipDelay: 50,
        hideEdgesOnDrag: isLarge,
        hideEdgesOnZoom: isLarge,
      },
    };

    if (!networkRef.current) {
      setIsStabilizing(true);
      nodesDataSetRef.current = new DataSet(formattedNodes);
      edgesDataSetRef.current = new DataSet(formattedEdges);

      const net = new Network(
        containerRef.current,
        { nodes: nodesDataSetRef.current, edges: edgesDataSetRef.current },
        options
      );

      net.on('click', (params) => {
        if (params.nodes && params.nodes.length > 0) {
          const clickedId = params.nodes[0];
          const directMatch = nodes.find(n => String(n.id) === String(clickedId));
          if (directMatch) onSelectNode(directMatch);
        } else {
          onSelectNode(null);
        }
      });

      net.on('doubleClick', (params) => {
        if (params.nodes && params.nodes.length > 0) {
          const clickedId = params.nodes[0];
          if (onExpandNode) onExpandNode(clickedId);
        }
      });

      net.once('stabilizationIterationsDone', () => {
        setIsStabilizing(false);
        net.fit({ animation: { duration: 450 } });
      });

      networkRef.current = net;
    } else {
      // Data update: swap datasets and fit cleanly
      nodesDataSetRef.current.clear();
      nodesDataSetRef.current.add(formattedNodes);
      edgesDataSetRef.current.clear();
      edgesDataSetRef.current.add(formattedEdges);
      networkRef.current.setOptions(options);

      setTimeout(() => {
        if (networkRef.current) {
          networkRef.current.fit({ animation: { duration: 400 } });
        }
      }, 100);
    }
  }, [nodes, links, buildNodePayload, onSelectNode, onExpandNode]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (networkRef.current) {
        networkRef.current.destroy();
        networkRef.current = null;
      }
    };
  }, []);

  // Center on node if search target changes
  useEffect(() => {
    const focusTarget = focusSearchId || selectedNode?.id;
    if (!focusTarget || !networkRef.current) return;

    try {
      networkRef.current.focus(String(focusTarget), {
        scale: 1.15,
        animation: { duration: 500, easingFunction: 'easeInOutQuad' },
      });
      networkRef.current.selectNodes([String(focusTarget)]);
    } catch {
      // Ignored
    }
  }, [focusSearchId, selectedNode?.id]);

  // Controls Handlers
  const handleZoomToFit = useCallback(() => {
    if (networkRef.current) {
      networkRef.current.fit({ animation: { duration: 400 } });
    }
  }, []);

  const handleZoomIn = useCallback(() => {
    if (networkRef.current) {
      const curScale = networkRef.current.getScale();
      networkRef.current.moveTo({ scale: curScale * 1.35, animation: { duration: 250 } });
    }
  }, []);

  const handleZoomOut = useCallback(() => {
    if (networkRef.current) {
      const curScale = networkRef.current.getScale();
      networkRef.current.moveTo({ scale: curScale / 1.35, animation: { duration: 250 } });
    }
  }, []);

  const handleTogglePhysics = useCallback(() => {
    setPhysicsActive(prev => {
      const next = !prev;
      if (networkRef.current) {
        networkRef.current.setOptions({ physics: { enabled: next } });
      }
      if (onTogglePause) onTogglePause(!next);
      return next;
    });
  }, [onTogglePause]);

  return (
    <div 
      className="live-graph-canvas-wrapper" 
      style={{ 
        width: '100%', 
        height: '600px', 
        minHeight: '600px',
        position: 'relative',
        background: '#F8FAFC',
        borderRadius: '12px',
        overflow: 'hidden',
        border: '1px solid #D5DFEB',
      }}
    >
      {/* Vis.js network mount target */}
      <div 
        ref={containerRef} 
        style={{ 
          width: '100%', 
          height: '100%', 
          position: 'absolute', 
          top: 0, 
          left: 0, 
          right: 0, 
          bottom: 0 
        }} 
      />

      {/* Stabilization loading spinner overlay */}
      {isStabilizing && (
        <div style={{
          position: 'absolute',
          top: '14px',
          left: '14px',
          background: 'rgba(255, 255, 255, 0.92)',
          backdropFilter: 'blur(6px)',
          border: '1px solid #CBD5E1',
          padding: '6px 12px',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '12px',
          fontWeight: '600',
          color: '#1D4ED8',
          zIndex: 10,
          boxShadow: '0 2px 8px rgba(0,0,0,0.06)'
        }}>
          <span className="kg-live-dot" style={{ background: '#2563EB' }} />
          <span>Stabilizing graph layout...</span>
        </div>
      )}

      {/* Floating Canvas Controls Overlay matching Streamlit */}
      <div className="graph-controls-floating-bar">
        <button 
          className="btn-graph-tool" 
          onClick={handleZoomIn} 
          title="Zoom In (+)"
        >
          <ZoomIn size={14} />
        </button>
        <button 
          className="btn-graph-tool" 
          onClick={handleZoomOut} 
          title="Zoom Out (-)"
        >
          <ZoomOut size={14} />
        </button>
        <button 
          className="btn-graph-tool" 
          onClick={handleZoomToFit} 
          title="Fit to Screen (Center)"
        >
          <Maximize2 size={14} />
        </button>
        <button 
          className={`btn-graph-tool ${!physicsActive ? 'tool-active' : ''}`} 
          onClick={handleTogglePhysics} 
          title={physicsActive ? "Pause Physics Simulation" : "Resume Physics Simulation"}
        >
          {physicsActive ? <Zap size={14} className="text-amber" /> : <ZapOff size={14} />}
        </button>
      </div>

      {/* Floating interactive hint pill */}
      <div className="graph-interactive-hint">
        <Sparkles size={12} className="text-cyan" />
        <span>Click node to inspect • Double-click to expand • Scroll to zoom • Drag to pan</span>
      </div>
    </div>
  );
}
