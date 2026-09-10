import React, { useState, useEffect } from 'react';
import { 
  GitMerge, 
  CheckCircle2, 
  Cpu, 
  Binary, 
  ShieldCheck, 
  Boxes, 
  Terminal, 
  ArrowRight,
  RefreshCw,
  Zap,
  Play,
  Square,
  RotateCw,
  Database,
  Radio,
  FileCode,
  Layers,
  Activity
} from 'lucide-react';
import { SOURCE_FILES } from '../data/mockData';

export default function PipelineView() {
  // Layer 2: Knowledge Engineering State
  const [keStatus, setKeStatus] = useState('READY'); // READY, RUNNING, COMPLETED, STOPPED
  const [keProgress, setKeProgress] = useState(0);
  const [keStep, setKeStep] = useState('Ready for Knowledge Extraction');
  const [keScope, setKeScope] = useState('All Source Files (Full Repository)');
  const [keForce, setKeForce] = useState(false);

  // Layer 3: Knowledge Graph & Vector Store State
  const [l3Status, setL3Status] = useState('READY');
  const [neo4jStatus, setNeo4jStatus] = useState('COMPLETED');
  const [neo4jProgress, setNeo4jProgress] = useState(100);
  const [neo4jStep, setNeo4jStep] = useState('Nodes & lineage updated');

  const [pineconeStatus, setPineconeStatus] = useState('COMPLETED');
  const [pineconeProgress, setPineconeProgress] = useState(100);
  const [pineconeStep, setPineconeStep] = useState('Vectors indexed in Pinecone');

  const [l3Mode, setL3Mode] = useState('Ingest Both (Neo4j Graph + Pinecone Vector)');
  const [discoverLinks, setDiscoverLinks] = useState(true);
  const [recreateNamespaces, setRecreateNamespaces] = useState(false);

  // Terminal Log Lines State
  const [logs, setLogs] = useState([
    { type: 'yellow', text: '• Initialized: KAIRIX Pipeline Orchestrator v2.0' },
    { type: 'cyan', text: '• Parsed: 21 enterprise artifacts across COBOL, SQL, and SSIS' },
    { type: 'green', text: '• Saved: 21 canonical JSON knowledge packages in output/knowledge/' },
    { type: 'purple', text: '• [Neo4j] Aura Cloud synchronized (1,006 entities, 2,822 relationships)' },
    { type: 'emerald', text: '• [Pinecone] 1,400 dense vector chunks indexed with cosine similarity' },
    { type: 'normal', text: 'Pipeline ready for on-demand execution or incremental update.' }
  ]);

  // Handle Layer 2 Run
  const handleRunLayer2 = () => {
    setKeStatus('RUNNING');
    setKeProgress(10);
    setKeStep('Initializing Tree-sitter & SQLGlot AST parsers...');

    addLog('cyan', `• Processing Layer 2 Knowledge Engineering: ${keScope}`);
    addLog('yellow', '• Loading AST grammar bundles for COBOL, T-SQL, and SSIS XML...');

    setTimeout(() => {
      setKeProgress(40);
      setKeStep('Extracting business rules & mathematical rating formulas...');
      addLog('cyan', '• Analyzing EARNPREM.CBL proration clauses (Lines 587–594)...');
    }, 600);

    setTimeout(() => {
      setKeProgress(75);
      setKeStep('Validating Pydantic schemas & reconciling LLM findings...');
      addLog('cyan', '• Reconciling ConditionalSplit rules BR-07 / BR-08 from Extract_Premium.dtsx...');
    }, 1200);

    setTimeout(() => {
      setKeProgress(100);
      setKeStatus('COMPLETED');
      setKeStep('Ready: 21 knowledge packages generated');
      addLog('green', '• Saved: output/knowledge/ packages generated successfully (100% deterministic)');
    }, 1800);
  };

  const handleStopLayer2 = () => {
    setKeStatus('STOPPED');
    setKeStep('Execution stopped by user');
    addLog('red', '• Layer 2 Knowledge Engineering Agent process stopped by user.');
  };

  // Handle Layer 3 Run
  const handleRunLayer3 = () => {
    setL3Status('RUNNING');
    setNeo4jStatus('RUNNING');
    setPineconeStatus('RUNNING');
    setNeo4jProgress(20);
    setPineconeProgress(15);
    setNeo4jStep('Connecting to Neo4j Aura Bolt endpoint...');
    setPineconeStep('Connecting to Pinecone serverless index...');

    addLog('purple', '• [Neo4j] Opening Aura Cloud Bolt session (neo4j+s://03f0aac2.databases.neo4j.io)...');
    addLog('emerald', '• [Pinecone] Connecting to index "kairix-index" (dimension: 384)...');

    setTimeout(() => {
      setNeo4jProgress(60);
      setPineconeProgress(55);
      setNeo4jStep('Merging AST nodes and discovering cross-system links...');
      setPineconeStep('Embedding code chunks via sentence-transformers...');
      addLog('purple', '• [Neo4j] Discovered cross-system link: EARNPREM.CBL -> Extract_Premium.dtsx -> PolicyCenter.sql');
      addLog('emerald', '• [Pinecone] Upserting 1,400 dense vector chunks into namespace "kairix-code"...');
    }, 800);

    setTimeout(() => {
      setNeo4jProgress(100);
      setPineconeProgress(100);
      setL3Status('COMPLETED');
      setNeo4jStatus('COMPLETED');
      setPineconeStatus('COMPLETED');
      setNeo4jStep('Nodes & lineage updated (1,006 nodes, 2,822 edges)');
      setPineconeStep('Vectors indexed in Pinecone (1,400 vectors)');
      addLog('green', '• Layer 3 Ingestion completed successfully in parallel.');
    }, 1600);
  };

  const handleStopLayer3 = () => {
    setL3Status('STOPPED');
    setNeo4jStatus('STOPPED');
    setPineconeStatus('STOPPED');
    setNeo4jStep('Stopped by user');
    setPineconeStep('Stopped by user');
    addLog('red', '• Layer 3 Ingestion terminated.');
  };

  const handleStopAll = () => {
    handleStopLayer2();
    handleStopLayer3();
  };

  const addLog = (type, text) => {
    setLogs(prev => [...prev, { type, text }]);
  };

  return (
    <div className="pipeline-container">
      {/* Top Header & Global Actions matching Streamlit */}
      <div className="pipeline-top-header">
        <div>
          <h1 className="pipeline-title">Pipeline Execution &amp; Control Center</h1>
          <p className="pipeline-subtitle">
            Trigger and monitor deterministic AST extraction, Neo4j Knowledge Graph ingestion, and Pinecone semantic vector indexing.
          </p>
        </div>

        <div className="pipeline-global-actions">
          <button 
            className="btn btn-secondary"
            onClick={() => {
              addLog('normal', `• Status refreshed at ${new Date().toLocaleTimeString()}`);
            }}
          >
            <RotateCw size={14} /> Refresh Status
          </button>
          <button 
            className="btn btn-danger"
            onClick={handleStopAll}
          >
            <Square size={14} /> Stop All
          </button>
        </div>
      </div>

      {/* Two Dedicated Symmetrical Pipeline Cards matching Streamlit */}
      <div className="pipeline-operation-cards-grid">
        {/* ========================================================================= */}
        {/* CARD 1: LAYER 2 KNOWLEDGE ENGINEERING AGENT                               */}
        {/* ========================================================================= */}
        <div className="pipeline-card card-layer2">
          <div className="card-top-row">
            <span className="card-subtitle-tag text-blue">Pipeline 1 • Layer 2</span>
            <span className={`status-badge-pill ${keStatus.toLowerCase()}`}>
              {keStatus === 'RUNNING' && <span className="live-spinner-dot" />}
              {keStatus === 'RUNNING' ? `RUNNING (${keProgress}%)` : keStatus}
            </span>
          </div>

          <h3 className="card-main-title">Layer 2: Knowledge Engineering Agent</h3>
          <p className="card-desc-text">
            Runs deterministic parsing, AST symbol extraction, line evidence, and LLM business rule extraction across COBOL, SQL, and SSIS.
          </p>

          {/* Status Box */}
          <div className="pipeline-status-box">
            {keStatus === 'RUNNING' ? (
              <div className="status-box-running">
                <div className="progress-bar-track">
                  <div className="progress-bar-fill fill-blue" style={{ width: `${keProgress}%` }} />
                </div>
                <span className="progress-step-text text-blue font-mono">{keStep}</span>
              </div>
            ) : keStatus === 'COMPLETED' ? (
              <div className="status-box-completed">
                <span className="check-icon text-emerald">✓</span>
                <div>
                  <div className="status-main-text text-emerald">Ready: 21 knowledge packages generated</div>
                  <div className="status-sub-text">Deterministic AST symbols, evidence, &amp; summaries cached</div>
                </div>
              </div>
            ) : keStatus === 'STOPPED' ? (
              <div className="status-box-stopped">
                <span className="stop-icon text-rose">⏹</span>
                <div>
                  <div className="status-main-text text-rose">Execution stopped by user</div>
                  <div className="status-sub-text">Pipeline process terminated</div>
                </div>
              </div>
            ) : (
              <div className="status-box-ready">
                <span className="ready-icon text-cyan">⚡</span>
                <div>
                  <div className="status-main-text text-cyan">Ready for Knowledge Extraction</div>
                  <div className="status-sub-text">Extracts symbols, rules &amp; evidence across COBOL, SQL &amp; SSIS</div>
                </div>
              </div>
            )}
          </div>

          {/* Controls Form */}
          <div className="pipeline-card-controls">
            <div className="form-group">
              <label className="field-label">Target Scope:</label>
              <select
                className="form-select font-mono"
                value={keScope}
                onChange={(e) => setKeScope(e.target.value)}
                disabled={keStatus === 'RUNNING'}
              >
                <option value="All Source Files (Full Repository)">All Source Files (Full Repository)</option>
                {SOURCE_FILES.map((f, idx) => (
                  <option key={idx} value={f.name}>
                    [{f.type}] {f.name}
                  </option>
                ))}
              </select>
            </div>

            <label className="custom-checkbox-label">
              <input
                type="checkbox"
                checked={keForce}
                onChange={(e) => setKeForce(e.target.checked)}
                disabled={keStatus === 'RUNNING'}
              />
              <span>Force re-extract files (bypass local cache)</span>
            </label>

            <div className="pipeline-card-action-row">
              {keStatus === 'RUNNING' ? (
                <>
                  <button className="btn btn-primary flex-1" disabled>
                    <Activity size={15} className="spin-icon" /> Extracting Layer 2...
                  </button>
                  <button className="btn btn-danger" onClick={handleStopLayer2}>
                    <Square size={14} /> Stop
                  </button>
                </>
              ) : (
                <button className="btn btn-primary w-full" onClick={handleRunLayer2}>
                  <Play size={15} /> Run Knowledge Engineering Agent
                </button>
              )}
            </div>
          </div>
        </div>

        {/* ========================================================================= */}
        {/* CARD 2: LAYER 3 GRAPH & VECTOR STORE INGESTION                            */}
        {/* ========================================================================= */}
        <div className="pipeline-card card-layer3">
          <div className="card-top-row">
            <span className="card-subtitle-tag text-purple">Pipeline 2 • Layer 3</span>
            <span className={`status-badge-pill ${l3Status.toLowerCase()}`}>
              {l3Status === 'RUNNING' && <span className="live-spinner-dot" />}
              {l3Status === 'RUNNING' ? 'RUNNING (PARALLEL)' : l3Status}
            </span>
          </div>

          <h3 className="card-main-title">Layer 3: Knowledge Graph &amp; Vector Store Ingestion</h3>
          <p className="card-desc-text">
            Loads canonical packages into Neo4j Knowledge Graph with cross-file lineage and embeds source chunks into Pinecone namespaces.
          </p>

          {/* Dual Split Mini-Panels matching Streamlit */}
          <div className="dual-status-grid">
            {/* Neo4j Mini Panel */}
            <div className="mini-panel neo4j-mini-panel">
              <div className="mini-panel-header">
                <span className="mini-panel-title text-blue">
                  <Database size={13} /> Neo4j Graph
                </span>
                <span className={`mini-badge ${neo4jStatus.toLowerCase()}`}>
                  {neo4jStatus === 'RUNNING' ? `${neo4jProgress}%` : neo4jStatus}
                </span>
              </div>
              {neo4jStatus === 'RUNNING' ? (
                <div className="progress-bar-track">
                  <div className="progress-bar-fill fill-blue" style={{ width: `${neo4jProgress}%` }} />
                </div>
              ) : null}
              <div className="mini-step-text font-mono text-blue">{neo4jStep}</div>
            </div>

            {/* Pinecone Mini Panel */}
            <div className="mini-panel pinecone-mini-panel">
              <div className="mini-panel-header">
                <span className="mini-panel-title text-emerald">
                  <Radio size={13} /> Pinecone DB
                </span>
                <span className={`mini-badge ${pineconeStatus.toLowerCase()}`}>
                  {pineconeStatus === 'RUNNING' ? `${pineconeProgress}%` : pineconeStatus}
                </span>
              </div>
              {pineconeStatus === 'RUNNING' ? (
                <div className="progress-bar-track">
                  <div className="progress-bar-fill fill-green" style={{ width: `${pineconeProgress}%` }} />
                </div>
              ) : null}
              <div className="mini-step-text font-mono text-emerald">{pineconeStep}</div>
            </div>
          </div>

          {/* Controls Form */}
          <div className="pipeline-card-controls">
            <div className="form-group">
              <label className="field-label">Layer 3 Ingestion Scope:</label>
              <select
                className="form-select font-mono"
                value={l3Mode}
                onChange={(e) => setL3Mode(e.target.value)}
                disabled={l3Status === 'RUNNING'}
              >
                <option value="Ingest Both (Neo4j Graph + Pinecone Vector)">Ingest Both (Neo4j Graph + Pinecone Vector)</option>
                <option value="Neo4j Knowledge Graph Only">Neo4j Knowledge Graph Only</option>
                <option value="Pinecone Vector Store Only">Pinecone Vector Store Only</option>
              </select>
            </div>

            <div className="form-row-2col">
              <label className="custom-checkbox-label">
                <input
                  type="checkbox"
                  checked={discoverLinks}
                  onChange={(e) => setDiscoverLinks(e.target.checked)}
                  disabled={l3Status === 'RUNNING'}
                />
                <span>Discover cross-file links</span>
              </label>

              <label className="custom-checkbox-label">
                <input
                  type="checkbox"
                  checked={recreateNamespaces}
                  onChange={(e) => setRecreateNamespaces(e.target.checked)}
                  disabled={l3Status === 'RUNNING'}
                />
                <span>Recreate namespaces</span>
              </label>
            </div>

            <div className="pipeline-card-action-row">
              {l3Status === 'RUNNING' ? (
                <>
                  <button className="btn btn-primary flex-1" disabled>
                    <Activity size={15} className="spin-icon" /> Ingesting Neo4j &amp; Pinecone...
                  </button>
                  <button className="btn btn-danger" onClick={handleStopLayer3}>
                    <Square size={14} /> Stop
                  </button>
                </>
              ) : (
                <button className="btn btn-primary w-full" onClick={handleRunLayer3}>
                  <Play size={15} /> Ingest Both (Neo4j Graph + Pinecone Vector)
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* REAL-TIME MONOSPACE TERMINAL CONSOLE matching Streamlit                   */}
      {/* ========================================================================= */}
      <div className="pipeline-terminal-wrapper">
        <div className="terminal-header-bar">
          <div className="terminal-window-dots">
            <span className="dot dot-red" />
            <span className="dot dot-yellow" />
            <span className="dot dot-green" />
            <span className="terminal-title">Pipeline Execution Log Console</span>
          </div>
          <span className="terminal-live-badge">Live Stream</span>
        </div>

        <div className="terminal-viewport font-mono">
          {logs.map((line, idx) => (
            <div key={idx} className={`terminal-log-line ${line.type}`}>
              {line.text}
            </div>
          ))}
        </div>
      </div>

      {/* ========================================================================= */}
      {/* SOURCE FILES PROCESSING STATUS TABLE matching Streamlit                  */}
      {/* ========================================================================= */}
      <div className="glass-panel files-status-table-panel">
        <div className="files-status-header">
          <h3 className="table-title">Source Files Processing Status ({SOURCE_FILES.length} Files)</h3>
          <span className="table-desc">Status of AST knowledge packages and Neo4j graph nodes per source file.</span>
        </div>

        <div className="status-table-container">
          <table className="files-status-table font-mono">
            <thead>
              <tr>
                <th>Technology</th>
                <th>Source File</th>
                <th>Lines</th>
                <th>Knowledge Package</th>
                <th>Graph Lineage</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {SOURCE_FILES.map((f, idx) => (
                <tr key={idx}>
                  <td>
                    <span className={`tech-pill ${f.type.toLowerCase()}`}>
                      {f.type}
                    </span>
                  </td>
                  <td className="font-bold">{f.name}</td>
                  <td>{f.lines || 300}</td>
                  <td>
                    <span className="status-cell-tag completed">
                      ✓ Generated &amp; Cached
                    </span>
                  </td>
                  <td>
                    <span className="status-cell-tag completed">
                      ✓ Linked in Neo4j
                    </span>
                  </td>
                  <td>
                    <button 
                      className="btn-table-action"
                      onClick={() => {
                        addLog('cyan', `• Triggering re-extraction for [${f.type}] ${f.name}...`);
                        setTimeout(() => {
                          addLog('green', `• Successfully updated knowledge package for ${f.name}`);
                        }, 500);
                      }}
                    >
                      <RotateCw size={12} /> Re-extract
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
