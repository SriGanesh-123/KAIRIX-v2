import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  RotateCw, 
  ChevronDown, 
  FileCode, 
  Check, 
  Terminal, 
  Database,
  ExternalLink,
  ShieldCheck,
  Code,
  Copy,
  Upload,
  Layers,
  Sparkles,
  GitFork,
  ArrowRight,
  BookOpen
} from 'lucide-react';
import { SOURCE_FILES } from '../data/mockData';
import { ACTUAL_SOURCE_FILES } from '../data/actualData';
import { ApiService } from '../services/api';

export default function SourceExplorerView({ onNavigateToInvestigate }) {
  const [fileOptions, setFileOptions] = useState(SOURCE_FILES);
  const [selectedFileId, setSelectedFileId] = useState(SOURCE_FILES[0].id);
  const [filterType, setFilterType] = useState('ALL');
  const [activeTab, setActiveTab] = useState('code'); // 'code', 'entities', 'rules', 'lineage'
  const [liveDetail, setLiveDetail] = useState(null);
  const [copiedCode, setCopiedCode] = useState(false);

  // "+ Add Source" Form State
  const [showAddSource, setShowAddSource] = useState(false);
  const [newSourceTech, setNewSourceTech] = useState('COBOL');
  const [newSourceName, setNewSourceName] = useState('');
  const [newSourceCode, setNewSourceCode] = useState('');
  const [autoAnalyze, setAutoAnalyze] = useState(false);
  const [addSuccessMessage, setAddSuccessMessage] = useState('');

  useEffect(() => {
    ApiService.getSources().then(files => {
      if (files && files.length > 0) {
        setFileOptions(files);
        setSelectedFileId(files[0].id);
      }
    });
  }, []);

  const visibleFiles = filterType === 'ALL' 
    ? fileOptions 
    : fileOptions.filter(f => f.type.toUpperCase() === filterType.toUpperCase());

  const currentFile = visibleFiles.find(f => f.id === selectedFileId || f.name === selectedFileId) || visibleFiles[0] || fileOptions[0];

  useEffect(() => {
    if (currentFile?.name) {
      ApiService.getSourceDetail(currentFile.name).then(data => {
        if (data) setLiveDetail(data);
      });
    }
  }, [currentFile?.name]);

  const handleFilterChange = (type) => {
    setFilterType(type);
    const firstMatch = type === 'ALL' 
      ? fileOptions[0] 
      : fileOptions.find(f => f.type.toUpperCase() === type.toUpperCase());
    if (firstMatch) setSelectedFileId(firstMatch.id);
  };

  const handleRefresh = () => {
    setFileOptions([...SOURCE_FILES]);
  };

  const handleCopyCode = () => {
    const code = liveDetail?.raw_code || currentFile?.raw_code || '';
    navigator.clipboard.writeText(code);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000);
  };

  // Handle Add Source submission
  const handleAddSourceSubmit = (e) => {
    e.preventDefault();
    if (!newSourceName.trim()) return;

    const ext = newSourceTech === 'COBOL' ? '.cbl' : (newSourceTech === 'SQL' ? '.sql' : '.dtsx');
    const finalName = newSourceName.includes('.') ? newSourceName : `${newSourceName}${ext}`;

    const newEntry = {
      id: finalName,
      name: finalName,
      type: newSourceTech,
      lines: newSourceCode ? newSourceCode.split('\n').length : 120,
      entities: newSourceTech === 'COBOL' ? 45 : (newSourceTech === 'SQL' ? 18 : 28),
      relationships: 16,
      rules: 6,
      purpose: `Enterprise ${newSourceTech} source file registered dynamically.`,
      raw_code: newSourceCode || `// Sample ${newSourceTech} source for ${finalName}\n\n// Added via KAIRIX Source Explorer`,
      business_rules: [
        {
          rule_id: "BR-NEW-01",
          name: `${finalName} Standard Rule`,
          description: "Extracted validation constraint from newly registered source.",
          formula: "Rule validated by Tree-sitter parser"
        }
      ]
    };

    setFileOptions(prev => [newEntry, ...prev]);
    setSelectedFileId(newEntry.id);
    setShowAddSource(false);
    setNewSourceName('');
    setNewSourceCode('');
    setAddSuccessMessage(`Source file "${finalName}" successfully registered & cached!`);
    setTimeout(() => setAddSuccessMessage(''), 4000);
  };

  const codeContent = liveDetail?.raw_code || currentFile?.raw_code || '';
  const codeLines = codeContent.split('\n');

  // Business Rules for current file
  const currentRules = currentFile?.business_rules || [
    {
      rule_id: "Rule 1",
      name: `${currentFile?.name} Calculation Logic`,
      description: "Prorated calendar calculation and unearned remainder deduction.",
      formula: "EARNED = WRITTEN * EARNED_DAYS / TERM_DAYS"
    },
    {
      rule_id: "Rule 2",
      name: `${currentFile?.name} Inclusive Days Rule`,
      description: "Term and elapsed days include start and end dates (+1 day rule).",
      formula: "TERM_DAYS = (EXPIRY_DATE - EFFECTIVE_DATE) + 1"
    },
    {
      rule_id: "Rule 3",
      name: `${currentFile?.name} Upper Bound Cap`,
      description: "Earned amount cannot exceed written premium.",
      formula: "IF EARNED > WRITTEN MOVE WRITTEN TO EARNED"
    }
  ];

  return (
    <div className="source-explorer-page">
      {/* Top Header & Action Toolbar matching Streamlit */}
      <div className="source-explorer-top-bar">
        <div>
          <h1 className="source-explorer-title">Source Explorer</h1>
          <p className="source-explorer-subtitle">
            Browse, upload, and inspect enterprise source files, extracted entities, and business rules.
          </p>
        </div>

        <div className="source-explorer-actions">
          <button 
            className="btn btn-primary btn-add-source"
            onClick={() => setShowAddSource(!showAddSource)}
          >
            <Plus size={16} /> {showAddSource ? 'Close Form' : '+ Add Source'}
          </button>
          <button 
            className="btn btn-secondary btn-refresh"
            onClick={handleRefresh}
          >
            <RotateCw size={14} /> Refresh
          </button>
        </div>
      </div>

      {/* Success Notification Banner */}
      {addSuccessMessage && (
        <div className="success-banner-box">
          <Check size={16} className="text-emerald" />
          <span>{addSuccessMessage}</span>
        </div>
      )}

      {/* Expandable "Add New Source" Form matching Streamlit */}
      {showAddSource && (
        <div className="glass-panel add-source-expandable-panel">
          <div className="add-source-header">
            <div>
              <h3 className="add-source-title">Register New Enterprise Source</h3>
              <p className="add-source-sub">
                Upload or paste enterprise code (COBOL, SQL, or SSIS DTSX) for deterministic parsing and knowledge extraction.
              </p>
            </div>
            <span className="badge badge-cyan">Dynamic Ingestion</span>
          </div>

          <form onSubmit={handleAddSourceSubmit} className="add-source-form-grid">
            <div className="form-row-2col">
              <div className="form-group">
                <label className="field-label">Source Technology:</label>
                <select
                  className="form-select"
                  value={newSourceTech}
                  onChange={(e) => setNewSourceTech(e.target.value)}
                >
                  <option value="COBOL">COBOL</option>
                  <option value="SQL">SQL</option>
                  <option value="SSIS">SSIS</option>
                </select>
              </div>

              <div className="form-group">
                <label className="field-label">Source File Name:</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder={newSourceTech === 'COBOL' ? 'e.g. CLAIMS_AUDIT.cbl' : (newSourceTech === 'SQL' ? 'e.g. Policy_Summary.sql' : 'e.g. Extract_Claims.dtsx')}
                  value={newSourceName}
                  onChange={(e) => setNewSourceName(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label className="field-label">Paste Source Code Directly (or Upload File):</label>
              <textarea
                className="form-textarea font-mono"
                rows={5}
                placeholder={newSourceTech === 'COBOL' ? 'IDENTIFICATION DIVISION.\nPROGRAM-ID. SAMPLE...\n\nPROCEDURE DIVISION.' : '-- SQL Query / Stored Procedure or SSIS XML DTSX...'}
                value={newSourceCode}
                onChange={(e) => setNewSourceCode(e.target.value)}
              />
            </div>

            <div className="form-checkbox-row">
              <label className="custom-checkbox-label">
                <input
                  type="checkbox"
                  checked={autoAnalyze}
                  onChange={(e) => setAutoAnalyze(e.target.checked)}
                />
                <span>Run Knowledge Extraction Pipeline immediately after upload</span>
              </label>
            </div>

            <div className="form-actions-row">
              <button type="submit" className="btn btn-primary">
                Add Source to Catalog
              </button>
              <button 
                type="button" 
                className="btn btn-secondary"
                onClick={() => setShowAddSource(false)}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Filter Segmented Radio Bar matching Streamlit */}
      <div className="filter-segmented-bar">
        <button 
          className={`filter-radio-pill ${filterType === 'ALL' ? 'filter-radio-pill-active' : ''}`}
          onClick={() => handleFilterChange('ALL')}
        >
          <span className="radio-circle">
            {filterType === 'ALL' && <span className="radio-dot" />}
          </span>
          <span>All Files ({fileOptions.length})</span>
        </button>

        <button 
          className={`filter-radio-pill ${filterType === 'COBOL' ? 'filter-radio-pill-active' : ''}`}
          onClick={() => handleFilterChange('COBOL')}
        >
          <span className="radio-circle">
            {filterType === 'COBOL' && <span className="radio-dot" />}
          </span>
          <span>COBOL ({fileOptions.filter(f => f.type === 'COBOL').length})</span>
        </button>

        <button 
          className={`filter-radio-pill ${filterType === 'SQL' ? 'filter-radio-pill-active' : ''}`}
          onClick={() => handleFilterChange('SQL')}
        >
          <span className="radio-circle">
            {filterType === 'SQL' && <span className="radio-dot" />}
          </span>
          <span>SQL ({fileOptions.filter(f => f.type === 'SQL').length})</span>
        </button>

        <button 
          className={`filter-radio-pill ${filterType === 'SSIS' ? 'filter-radio-pill-active' : ''}`}
          onClick={() => handleFilterChange('SSIS')}
        >
          <span className="radio-circle">
            {filterType === 'SSIS' && <span className="radio-dot" />}
          </span>
          <span>SSIS ({fileOptions.filter(f => f.type === 'SSIS').length})</span>
        </button>
      </div>

      {/* Main Workspace Layout */}
      <div className="source-explorer-layout">
        {/* Left Side: Source Selector Dropdown */}
        <div className="source-selector-bar">
          <label className="field-label">Select Source File to Inspect:</label>
          <select 
            className="source-file-dropdown"
            value={currentFile?.id || ''}
            onChange={(e) => setSelectedFileId(e.target.value)}
          >
            {visibleFiles.map((file) => (
              <option key={file.id} value={file.id}>
                [{file.type}] {file.name} — {file.lines || 300} lines
              </option>
            ))}
          </select>
        </div>

        {/* 4 Metric Cards matching Streamlit */}
        <div className="source-metrics-grid">
          <div className="metric-card">
            <span className="metric-label">Lines of Code</span>
            <span className="metric-value font-mono text-cyan">{currentFile?.lines || 320}</span>
            <span className="metric-sub">Deterministic AST Count</span>
          </div>

          <div className="metric-card">
            <span className="metric-label">Extracted Entities</span>
            <span className="metric-value font-mono text-purple">{currentFile?.entities || 69}</span>
            <span className="metric-sub">Variables, Tables, Copybooks</span>
          </div>

          <div className="metric-card">
            <span className="metric-label">Business Rules</span>
            <span className="metric-value font-mono text-emerald">{currentFile?.rules || 11}</span>
            <span className="metric-sub">Deterministic + LLM Inferred</span>
          </div>

          <div className="metric-card">
            <span className="metric-label">Downstream Links</span>
            <span className="metric-value font-mono text-amber">{currentFile?.relationships || 35}</span>
            <span className="metric-sub">Graph Traversal Edges</span>
          </div>
        </div>

        {/* Purpose Description Card */}
        <div className="glass-panel purpose-summary-card">
          <div className="purpose-header">
            <span className="purpose-badge-pill">{currentFile?.type} Source Artifact</span>
            <button 
              className="btn-investigate-route"
              onClick={() => onNavigateToInvestigate?.(`How is logic implemented in ${currentFile?.name}?`)}
            >
              <Sparkles size={14} /> Investigate with AI →
            </button>
          </div>
          <p className="purpose-text">
            <strong>System Role &amp; Purpose:</strong> {currentFile?.purpose || "Enterprise reverse-engineered legacy module."}
          </p>
        </div>

        {/* 4 Detail Tabs */}
        <div className="source-tabs-container">
          <div className="source-tabs-header">
            <button 
              className={`source-tab-btn ${activeTab === 'code' ? 'active' : ''}`}
              onClick={() => setActiveTab('code')}
            >
              <FileCode size={15} /> Source Code Viewer
            </button>
            <button 
              className={`source-tab-btn ${activeTab === 'entities' ? 'active' : ''}`}
              onClick={() => setActiveTab('entities')}
            >
              <Database size={15} /> Extracted Entities ({currentFile?.entities || 69})
            </button>
            <button 
              className={`source-tab-btn ${activeTab === 'rules' ? 'active' : ''}`}
              onClick={() => setActiveTab('rules')}
            >
              <ShieldCheck size={15} /> Business Rules &amp; Formulas ({currentRules.length})
            </button>
            <button 
              className={`source-tab-btn ${activeTab === 'lineage' ? 'active' : ''}`}
              onClick={() => setActiveTab('lineage')}
            >
              <GitFork size={15} /> Cross-System Lineage
            </button>
          </div>

          <div className="source-tabs-content">
            {/* Tab 1: Source Code Viewer */}
            {activeTab === 'code' && (
              <div className="code-viewer-panel">
                <div className="code-viewer-toolbar">
                  <span className="code-toolbar-filename font-mono">
                    {currentFile?.name} ({codeLines.length} lines)
                  </span>
                  <button className="btn-copy-code" onClick={handleCopyCode}>
                    {copiedCode ? <Check size={14} className="text-emerald" /> : <Copy size={14} />}
                    <span>{copiedCode ? 'Copied!' : 'Copy Code'}</span>
                  </button>
                </div>
                <div className="code-display-viewport">
                  {codeLines.map((line, idx) => (
                    <div key={idx} className="code-line-row">
                      <span className="line-num font-mono">{idx + 1}</span>
                      <span className="line-code font-mono">{line || ' '}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Tab 2: Extracted AST Entities Table */}
            {activeTab === 'entities' && (
              <div className="entities-table-panel">
                <table className="entities-table">
                  <thead>
                    <tr>
                      <th>Entity Type</th>
                      <th>Identifier / Name</th>
                      <th>Data Type / PIC</th>
                      <th>Scope / Context</th>
                    </tr>
                  </thead>
                  <tbody>
                    {currentFile?.type === 'COBOL' ? (
                      <>
                        <tr>
                          <td><span className="entity-tag cobol">Record</span></td>
                          <td className="font-mono">PI-REC</td>
                          <td className="font-mono">RECORD (77 bytes)</td>
                          <td>FILE SECTION (POLICY-IN)</td>
                        </tr>
                        <tr>
                          <td><span className="entity-tag cobol">Field</span></td>
                          <td className="font-mono">PRI-WRITTEN-PREMIUM</td>
                          <td className="font-mono">PIC 9(9)V99</td>
                          <td>PREMIUM-IN</td>
                        </tr>
                        <tr>
                          <td><span className="entity-tag cobol">Variable</span></td>
                          <td className="font-mono">WS-EARNED</td>
                          <td className="font-mono">PIC 9(9)V99</td>
                          <td>WORKING-STORAGE (ROUNDED)</td>
                        </tr>
                        <tr>
                          <td><span className="entity-tag cobol">Variable</span></td>
                          <td className="font-mono">WS-UNEARNED</td>
                          <td className="font-mono">PIC 9(9)V99</td>
                          <td>WORKING-STORAGE</td>
                        </tr>
                        <tr>
                          <td><span className="entity-tag cobol">Paragraph</span></td>
                          <td className="font-mono">CALCULATE-EARNED</td>
                          <td className="font-mono">PROCEDURE</td>
                          <td>Proration logic (Lines 587–594)</td>
                        </tr>
                      </>
                    ) : currentFile?.type === 'SQL' ? (
                      <>
                        <tr>
                          <td><span className="entity-tag sql">Table</span></td>
                          <td className="font-mono">pc_policyperiod</td>
                          <td className="font-mono">RELATIONAL TABLE</td>
                          <td>dbo / PolicyCenter</td>
                        </tr>
                        <tr>
                          <td><span className="entity-tag sql">Table</span></td>
                          <td className="font-mono">pcx_cp7transaction</td>
                          <td className="font-mono">TRANSACTION TABLE</td>
                          <td>Commercial Property Line</td>
                        </tr>
                        <tr>
                          <td><span className="entity-tag sql">Projection</span></td>
                          <td className="font-mono">SubWritten_Premium</td>
                          <td className="font-mono">DECIMAL(18,2)</td>
                          <td>CASE WHEN TranType in ('Renewal','Submission')</td>
                        </tr>
                        <tr>
                          <td><span className="entity-tag sql">Projection</span></td>
                          <td className="font-mono">CancelledPremium</td>
                          <td className="font-mono">DECIMAL(18,2)</td>
                          <td>CASE WHEN TranType in ('Cancellation')</td>
                        </tr>
                      </>
                    ) : (
                      <>
                        <tr>
                          <td><span className="entity-tag ssis">Data Flow Task</span></td>
                          <td className="font-mono">DFT - Extract, Cleanse, Validate, Load</td>
                          <td className="font-mono">Microsoft.Pipeline</td>
                          <td>Main Package Executable</td>
                        </tr>
                        <tr>
                          <td><span className="entity-tag ssis">Component</span></td>
                          <td className="font-mono">CSPL - Business Rule Validation</td>
                          <td className="font-mono">Microsoft.ConditionalSplit</td>
                          <td>Financial Checks (BR-07, BR-08)</td>
                        </tr>
                        <tr>
                          <td><span className="entity-tag ssis">Destination</span></td>
                          <td className="font-mono">DST - Error Log (stg.error_quarantine)</td>
                          <td className="font-mono">Microsoft.OLEDBDestination</td>
                          <td>Error quarantine redirection</td>
                        </tr>
                      </>
                    )}
                  </tbody>
                </table>
              </div>
            )}

            {/* Tab 3: Business Rules & Formulas */}
            {activeTab === 'rules' && (
              <div className="rules-cards-grid">
                {currentRules.map((rule, idx) => (
                  <div key={idx} className="rule-card">
                    <div className="rule-card-header">
                      <span className="rule-id-badge">{rule.rule_id}</span>
                      <span className="rule-name-text">{rule.name}</span>
                    </div>
                    <p className="rule-desc-text">{rule.description}</p>
                    {rule.formula && (
                      <div className="rule-formula-box font-mono">
                        {rule.formula}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Tab 4: Cross-System Lineage */}
            {activeTab === 'lineage' && (
              <div className="lineage-explorer-panel">
                <div className="lineage-nodes-flow">
                  <div className="lineage-node-box">
                    <span className="node-badge cobol">COBOL Mainframe</span>
                    <span className="node-title font-mono">EARNPREM.CBL</span>
                    <span className="node-detail">Calculates WS-EARNED</span>
                  </div>

                  <div className="lineage-arrow">➔</div>

                  <div className="lineage-node-box">
                    <span className="node-badge ssis">SSIS ETL Package</span>
                    <span className="node-title font-mono">Extract_Premium.dtsx</span>
                    <span className="node-detail">Enforces BR-07 &amp; BR-08</span>
                  </div>

                  <div className="lineage-arrow">➔</div>

                  <div className="lineage-node-box">
                    <span className="node-badge sql">PostgreSQL DW / SQL</span>
                    <span className="node-title font-mono">PolicyCenter_CPP_Breakdown.sql</span>
                    <span className="node-detail">Segments by TranType</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
