import React, { useState } from 'react';
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

export default function SourceExplorerView({ onNavigateToInvestigate }) {
  const [selectedFileId, setSelectedFileId] = useState('cbl-1');
  const [filterType, setFilterType] = useState('ALL');
  const [activeCodeTab, setActiveCodeTab] = useState('code');

  // Multi-file datasets matching the counts from screenshot
  const fileOptions = [
    { id: 'cbl-1', name: 'EARNPREM.CBL', type: 'COBOL', lines: 320, entities: 69, relationships: 35, rules: 11,
      purpose: "Calculate earned and unearned premium amounts for each premium record by matching it to a policy, validating dates, applying the earned-premium formula, and writing the results or error records."
    },
    { id: 'cbl-2', name: 'PREMCALC.CBL', type: 'COBOL', lines: 480, entities: 94, relationships: 42, rules: 16,
      purpose: "Core rating algorithm computing base rate factors, driver surcharges, and discount credits for multi-line auto policies."
    },
    { id: 'cbl-3', name: 'POLSTATUS.CBL', type: 'COBOL', lines: 210, entities: 38, relationships: 19, rules: 7,
      purpose: "Batch status transition processor validating effective date intervals and updating status flags from InForce to Expired."
    },
    { id: 'sql-1', name: 'PolicyCenter_Monoline.sql', type: 'SQL', lines: 184, entities: 52, relationships: 28, rules: 8,
      purpose: "Analytical query aggregating earned premium across active commercial monoline policies, joining pc_policy and coverage records."
    },
    { id: 'ssis-1', name: 'Extract_Policy.dtsx', type: 'SSIS', lines: 412, entities: 76, relationships: 31, rules: 11,
      purpose: "Guidewire operational store ETL pipeline extracting policy revisions and staging into reporting warehouse dimension tables."
    }
  ];

  const currentFile = fileOptions.find(f => f.id === selectedFileId) || fileOptions[0];

  const handleFilterChange = (type) => {
    setFilterType(type);
    if (type === 'COBOL') setSelectedFileId('cbl-1');
    else if (type === 'SQL') setSelectedFileId('sql-1');
    else if (type === 'SSIS') setSelectedFileId('ssis-1');
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
          <span>All Files (21)</span>
        </label>

        <label 
          className={`filter-radio-pill ${filterType === 'COBOL' ? 'filter-radio-pill-active' : ''}`}
          onClick={() => handleFilterChange('COBOL')}
        >
          <span className="radio-circle">
            {filterType === 'COBOL' && <span className="radio-dot" />}
          </span>
          <span>COBOL (6)</span>
        </label>

        <label 
          className={`filter-radio-pill ${filterType === 'SQL' ? 'filter-radio-pill-active' : ''}`}
          onClick={() => handleFilterChange('SQL')}
        >
          <span className="radio-circle">
            {filterType === 'SQL' && <span className="radio-dot" />}
          </span>
          <span>SQL (4)</span>
        </label>

        <label 
          className={`filter-radio-pill ${filterType === 'SSIS' ? 'filter-radio-pill-active' : ''}`}
          onClick={() => handleFilterChange('SSIS')}
        >
          <span className="radio-circle">
            {filterType === 'SSIS' && <span className="radio-dot" />}
          </span>
          <span>SSIS Packages (11)</span>
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
            Business Rules ({currentFile.rules})
          </button>
          <button 
            className={`inner-tab-btn ${activeCodeTab === 'dependencies' ? 'inner-tab-active' : ''}`}
            onClick={() => setActiveCodeTab('dependencies')}
          >
            Dependencies ({currentFile.relationships})
          </button>
        </div>

        {/* Code Viewer */}
        {activeCodeTab === 'code' && (
          <div className="code-viewer-container">
            <pre className="code-display-block font-mono">
{`000100 IDENTIFICATION DIVISION.
000200 PROGRAM-ID. ${currentFile.name.replace('.CBL', '')}.
000300 ENVIRONMENT DIVISION.
000400 DATA DIVISION.
000500 WORKING-STORAGE SECTION.
000600 01  WS-POLICY-RECORD.
000700     05 WS-POL-NUM         PIC X(10).
000800     05 WS-POL-EFF-DATE    PIC 9(8).
000900     05 WS-POL-EXP-DATE    PIC 9(8).
001000     05 WS-WRITTEN-PREM    PIC 9(9)V99.
001100     05 WS-EARNED-PREM     PIC 9(9)V99.
001200     05 WS-DAYS-IN-FORCE   PIC 9(4).
001300     05 WS-TERM-DAYS       PIC 9(4).
001400 PROCEDURE DIVISION.
001500 0000-MAIN-LOGIC.
001600     PERFORM 1000-CALC-EARNED-PREM.
001700     GOBACK.
001800 1000-CALC-EARNED-PREM.
001900     COMPUTE WS-DAYS-IN-FORCE = FUNCTION CURRENT-DATE(1:8) - WS-POL-EFF-DATE
002000     COMPUTE WS-TERM-DAYS = WS-POL-EXP-DATE - WS-POL-EFF-DATE
002100     IF WS-DAYS-IN-FORCE > WS-TERM-DAYS
002200         MOVE WS-TERM-DAYS TO WS-DAYS-IN-FORCE
002300     END-IF.
002400     COMPUTE WS-EARNED-PREM ROUNDED = 
002500         (WS-DAYS-IN-FORCE / WS-TERM-DAYS) * WS-WRITTEN-PREM.`}
            </pre>
          </div>
        )}

        {/* Business Rules Viewer */}
        {activeCodeTab === 'rules' && (
          <div className="rules-viewer-container">
            <div className="rule-item-box">
              <span className="badge badge-amber">Rule 300</span>
              <strong>Earned Premium Calculation Formula</strong>
              <p className="rule-desc font-mono">
                WS-EARNED-PREM = (WS-DAYS-IN-FORCE / WS-TERM-DAYS) * WS-WRITTEN-PREM
              </p>
              <span className="text-muted text-xs">Anchored at EARNPREM.CBL: Lines 19–25</span>
            </div>
          </div>
        )}

        {/* Dependencies Viewer */}
        {activeCodeTab === 'dependencies' && (
          <div className="dependencies-viewer-container">
            <div className="dep-row">
              <span className="dep-label">Inputs (Reads From):</span>
              <span className="dep-pill font-mono">POLICY_MASTER</span>
              <span className="dep-pill font-mono">CPY_PREMCALC</span>
            </div>
            <div className="dep-row">
              <span className="dep-label">Outputs (Writes To):</span>
              <span className="dep-pill font-mono text-blue">STG_EARNED_PREM</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
