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
  Code
} from 'lucide-react';
import { SOURCE_FILES } from '../data/mockData';
import { ApiService } from '../services/api';

export default function SourceExplorerView({ onNavigateToInvestigate }) {
  const [fileOptions, setFileOptions] = useState(SOURCE_FILES);
  const [selectedFileId, setSelectedFileId] = useState(SOURCE_FILES[0].id);
  const [filterType, setFilterType] = useState('ALL');
  const [activeCodeTab, setActiveCodeTab] = useState('code');
  const [liveDetail, setLiveDetail] = useState(null);

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

  return (
    <div className="source-explorer-page">
      {/* Top Title & Action Bar */}
      <div className="source-explorer-top-bar">
        <div>
          <h1 className="source-explorer-title">Source Explorer</h1>
          <p className="source-explorer-subtitle">
            Browse, upload, and inspect enterprise source files, extracted entities, and business rules.
          </p>
        </div>

        <div className="source-explorer-actions">
          <button className="btn-add-source">
            <Plus size={16} /> Add Source
          </button>
          <button className="btn-refresh">
            <RotateCw size={14} /> Refr...
          </button>
        </div>
      </div>

      {/* Filter Segmented Radio Bar */}
      <div className="filter-segmented-bar">
        <label 
          className={`filter-radio-pill ${filterType === 'ALL' ? 'filter-radio-pill-active' : ''}`}
          onClick={() => handleFilterChange('ALL')}
        >
          <span className="radio-circle">
            {filterType === 'ALL' && <span className="radio-dot" />}
          </span>
          <span>All Files ({fileOptions.length})</span>
        </label>

        <label 
          className={`filter-radio-pill ${filterType === 'COBOL' ? 'filter-radio-pill-active' : ''}`}
          onClick={() => handleFilterChange('COBOL')}
        >
          <span className="radio-circle">
            {filterType === 'COBOL' && <span className="radio-dot" />}
          </span>
          <span>COBOL ({fileOptions.filter(f => f.type === 'COBOL').length})</span>
        </label>

        <label 
          className={`filter-radio-pill ${filterType === 'SQL' ? 'filter-radio-pill-active' : ''}`}
          onClick={() => handleFilterChange('SQL')}
        >
          <span className="radio-circle">
            {filterType === 'SQL' && <span className="radio-dot" />}
          </span>
          <span>SQL ({fileOptions.filter(f => f.type === 'SQL').length})</span>
        </label>

        <label 
          className={`filter-radio-pill ${filterType === 'SSIS' ? 'filter-radio-pill-active' : ''}`}
          onClick={() => handleFilterChange('SSIS')}
        >
          <span className="radio-circle">
            {filterType === 'SSIS' && <span className="radio-dot" />}
          </span>
          <span>SSIS Packages ({fileOptions.filter(f => f.type === 'SSIS').length})</span>
        </label>
      </div>

      {/* Select Source File Row */}
      <div className="select-file-row">
        <div className="select-file-group">
          <span className="select-file-label">SELECT SOURCE FILE:</span>
          <div className="custom-select-wrapper">
            <select 
              value={selectedFileId} 
              onChange={(e) => setSelectedFileId(e.target.value)}
              className="source-file-select"
            >
              {fileOptions.map(f => (
                <option key={f.id} value={f.id}>{f.name}</option>
              ))}
            </select>
            <ChevronDown size={16} className="select-chevron" />
          </div>
        </div>

        <div className="select-file-actions">
          <button 
            className="btn-pill-action"
            onClick={() => onNavigateToInvestigate?.(currentFile.name)}
          >
            Investigate
          </button>
          <button className="btn-pill-action btn-delete">
            <span>Delete</span>
            <ChevronDown size={14} />
          </button>
        </div>
      </div>

      {/* Main Content File Card */}
      <div className="source-detail-card">
        <div className="source-type-badge-pill">
          {currentFile.type}
        </div>

        <h2 className="source-detail-filename">{currentFile.name}</h2>

        {/* 4 KPI Metric Cards in Row */}
        <div className="source-metric-row">
          <div className="source-stat-card">
            <div className="stat-label">TOTAL LINES</div>
            <div className="stat-value text-black">{currentFile.lines}</div>
          </div>

          <div className="source-stat-card">
            <div className="stat-label">ENTITIES</div>
            <div className="stat-value text-blue">{currentFile.entities}</div>
          </div>

          <div className="source-stat-card">
            <div className="stat-label">RELATIONSHIPS</div>
            <div className="stat-value text-green">{currentFile.relationships}</div>
          </div>

          <div className="source-stat-card">
            <div className="stat-label">BUSINESS RULES</div>
            <div className="stat-value text-orange">{currentFile.rules}</div>
          </div>
        </div>

        {/* Purpose Callout Box */}
        <div className="purpose-callout-box">
          <strong>Purpose:</strong> {currentFile.purpose}
        </div>

        {/* Inner Tabs for Code & Lineage */}
        <div className="source-inner-tabs">
          <button 
            className={`inner-tab-btn ${activeCodeTab === 'code' ? 'inner-tab-active' : ''}`}
            onClick={() => setActiveCodeTab('code')}
          >
            Source Code
          </button>
          <button 
            className={`inner-tab-btn ${activeCodeTab === 'rules' ? 'inner-tab-active' : ''}`}
            onClick={() => setActiveCodeTab('rules')}
          >
            Business Rules ({currentFile.rules || currentFile.business_rules?.length || 0})
          </button>
          <button 
            className={`inner-tab-btn ${activeCodeTab === 'dependencies' ? 'inner-tab-active' : ''}`}
            onClick={() => setActiveCodeTab('dependencies')}
          >
            Dependencies ({currentFile.relationships || (currentFile.inputs?.length || 0) + (currentFile.outputs?.length || 0)})
          </button>
        </div>

        {/* Code Viewer */}
        {activeCodeTab === 'code' && (
          <div className="code-viewer-container">
            <pre className="code-display-block font-mono">
{currentFile?.raw_code || liveDetail?.raw_code || "No source code available for this artifact."}
            </pre>
          </div>
        )}

        {/* Business Rules Viewer */}
        {activeCodeTab === 'rules' && (
          <div className="rules-viewer-container">
            {((currentFile?.business_rules && currentFile.business_rules.length > 0)
              ? currentFile.business_rules 
              : (liveDetail?.knowledge_package?.business_rules || [])
            ).length > 0 ? (
              (currentFile?.business_rules && currentFile.business_rules.length > 0
                ? currentFile.business_rules 
                : liveDetail.knowledge_package.business_rules
              ).map((r, i) => (
                <div key={i} className="rule-item-box" style={{ marginBottom: '0.75rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <span className="badge badge-amber">{r.rule_id || `Rule ${i + 1}`}</span>
                    <strong>{r.name || r.rule_name || `Business Rule #${i + 1}`}</strong>
                  </div>
                  <p className="rule-desc font-mono" style={{ margin: '4px 0' }}>
                    {r.formula || r.logic || r.description || r.statement || JSON.stringify(r)}
                  </p>
                  {r.line_range && <span className="text-muted text-xs">Lines {r.line_range}</span>}
                </div>
              ))
            ) : (
              <div className="rule-item-box" style={{ padding: '20px', textAlign: 'center', color: '#64748b' }}>
                No explicit business rules cataloged for this component in the AST knowledge base.
              </div>
            )}
          </div>
        )}

        {/* Dependencies Viewer */}
        {activeCodeTab === 'dependencies' && (
          <div className="dependencies-viewer-container" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div className="dep-row" style={{ alignItems: 'flex-start' }}>
              <span className="dep-label" style={{ minWidth: '160px' }}>Inputs (Reads From):</span>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {currentFile?.inputs && currentFile.inputs.length > 0 ? (
                  currentFile.inputs.map((inp, idx) => (
                    <span key={idx} className="dep-pill font-mono">{inp}</span>
                  ))
                ) : (
                  <span className="text-muted text-xs font-mono">No direct input tables/files</span>
                )}
              </div>
            </div>

            <div className="dep-row" style={{ alignItems: 'flex-start' }}>
              <span className="dep-label" style={{ minWidth: '160px' }}>Outputs (Writes To):</span>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {currentFile?.outputs && currentFile.outputs.length > 0 ? (
                  currentFile.outputs.map((out, idx) => (
                    <span key={idx} className="dep-pill font-mono text-blue">{out}</span>
                  ))
                ) : (
                  <span className="text-muted text-xs font-mono">No direct output tables/files</span>
                )}
              </div>
            </div>

            {currentFile?.transformations && currentFile.transformations.length > 0 && (
              <div className="dep-row" style={{ alignItems: 'flex-start' }}>
                <span className="dep-label" style={{ minWidth: '160px' }}>Transformations:</span>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', flex: 1 }}>
                  {currentFile.transformations.map((t, idx) => (
                    <div key={idx} className="rule-item-box font-mono text-xs" style={{ padding: '8px 12px', margin: 0 }}>
                      • {t}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {currentFile?.dependencies && currentFile.dependencies.length > 0 && (
              <div className="dep-row" style={{ alignItems: 'flex-start' }}>
                <span className="dep-label" style={{ minWidth: '160px' }}>Dependencies:</span>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {currentFile.dependencies.map((dep, idx) => (
                    <span key={idx} className="dep-pill font-mono text-secondary">{dep}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
