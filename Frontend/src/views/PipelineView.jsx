import React, { useState } from 'react';
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
  Zap
} from 'lucide-react';
import SpatialCard from '../components/SpatialCard';

export default function PipelineView() {
  const [isRunning, setIsRunning] = useState(false);
  const [activeStep, setActiveStep] = useState(7);

  const stages = [
    {
      step: "01",
      name: "Source Classification",
      engine: "Regex & File Signature",
      status: "COMPLETED",
      latency: "4ms",
      details: "Detects syntax dialetcs: .cbl (COBOL), .sql (T-SQL/ANSI), .dtsx (SSIS XML)."
    },
    {
      step: "02",
      name: "Deterministic Parsing",
      engine: "Tree-sitter & SQLGlot",
      status: "COMPLETED",
      latency: "82ms",
      details: "Constructs ASTs, extracts tables, copybooks, parameters, and variable assignments without LLM hallucination."
    },
    {
      step: "03",
      name: "Line-Anchored Evidence Building",
      engine: "Source Indexer",
      status: "COMPLETED",
      latency: "16ms",
      details: "Anchors every token, business entity, and statement to exact line and column ranges."
    },
    {
      step: "04",
      name: "Multi-Pass LLM Review",
      engine: "NVIDIA NIM (nematron-3-ultra)",
      status: "COMPLETED",
      latency: "1,240ms",
      details: "Deep cognitive analysis discovering hidden business rules, validation criteria, and implicit dependencies."
    },
    {
      step: "05",
      name: "Pydantic Schema Validation",
      engine: "Pydantic v2 Engine",
      status: "COMPLETED",
      latency: "12ms",
      details: "Strict JSON Schema validation for KnowledgeProfile, BusinessRule, and Transformation models."
    },
    {
      step: "06",
      name: "Reconciliation Engine",
      engine: "Fuzzy Logic & Evidence Scoring",
      status: "COMPLETED",
      latency: "34ms",
      details: "Merges deterministic parser facts (confidence 1.0) with LLM inferences (confidence 0.85), flagging naming drift."
    },
    {
      step: "07",
      name: "Canonical Knowledge Packaging",
      engine: "Package Builder",
      status: "COMPLETED",
      latency: "28ms",
      details: "Generates standardized JSON packages ready for simultaneous loading into Neo4j Aura and Pinecone."
    }
  ];

  const handleTriggerReRun = () => {
    setIsRunning(true);
    setActiveStep(1);
    const interval = setInterval(() => {
      setActiveStep((prev) => {
        if (prev >= 7) {
          clearInterval(interval);
          setIsRunning(false);
          return 7;
        }
        return prev + 1;
      });
    }, 400);
  };

  return (
    <div className="pipeline-container">
      {/* Top Controls Header */}
      <div className="pipeline-header glass-panel">
        <div className="pipeline-title-group">
          <div className="icon-badge-box">
            <GitMerge size={18} className="pill-icon-cyan" />
          </div>
          <div>
            <h2 className="pipeline-main-title">LangGraph Knowledge Engineering Pipeline</h2>
            <p className="pipeline-main-sub">7-Node autonomous state machine running deterministic AST extraction and LLM reconciliation</p>
          </div>
        </div>

        <button 
          className="btn btn-primary"
          onClick={handleTriggerReRun}
          disabled={isRunning}
        >
          {isRunning ? (
            <>
              <RefreshCw size={14} className="spin-icon" /> Executing Pipeline (Step 0{activeStep})...
            </>
          ) : (
            <>
              <Zap size={14} /> Re-Run Full Pipeline
            </>
          )}
        </button>
      </div>

      {/* 7-Stage LangGraph Timeline */}
      <div className="stages-timeline">
        {stages.map((stage, idx) => {
          const stepNum = idx + 1;
          const isDone = stepNum <= activeStep;
          const isCurrent = stepNum === activeStep && isRunning;

          return (
            <SpatialCard 
              key={stage.step} 
              className={`stage-step-card ${isCurrent ? 'stage-card-active' : ''}`}
            >
              <div className="stage-card-top">
                <span className="stage-number">{stage.step}</span>
                <div className="stage-badges">
                  <span className="badge badge-purple">{stage.engine}</span>
                  <span className={`badge ${isDone ? 'badge-emerald' : 'badge-amber'}`}>
                    {isCurrent ? 'RUNNING' : isDone ? 'COMPLETED' : 'PENDING'}
                  </span>
                </div>
              </div>

              <h3 className="stage-name">{stage.name}</h3>
              <p className="stage-desc">{stage.details}</p>

              <div className="stage-footer">
                <span className="stage-latency font-mono">Latency: {stage.latency}</span>
                <span className="stage-status-icon">
                  <CheckCircle2 size={16} className={isDone ? "text-emerald" : "text-muted"} />
                </span>
              </div>
            </SpatialCard>
          );
        })}
      </div>

      {/* Execution Telemetry Stream */}
      <div className="glass-panel pipeline-log-panel">
        <div className="log-panel-header">
          <div className="log-title font-mono">
            <Terminal size={14} className="pill-icon-cyan" />
            <span>State Machine Execution Logs</span>
          </div>
          <span className="badge badge-cyan font-mono">LangGraph State: IDLE</span>
        </div>

        <pre className="code-preview font-mono log-stream-box">
{`[INFO] [2026-09-07T12:30:01] LangGraph node 'source_classifier' started.
[INFO] [2026-09-07T12:30:01] Classified 21 artifacts (8 COBOL, 7 SQL, 6 SSIS).
[INFO] [2026-09-07T12:30:02] Tree-sitter parsed EARNPREM.CBL -> AST node count: 482.
[INFO] [2026-09-07T12:30:03] SQLGlot parsed PolicyCenter_Monoline.sql -> Tables: [pc_policy, STG_EARNED_PREM].
[INFO] [2026-09-07T12:30:04] NVIDIA NIM multi-pass review completed for EARNPREM.CBL.
[INFO] [2026-09-07T12:30:04] Reconciled: 152 business rules locked with line-anchored confidence 1.0.
[SUCCESS] [2026-09-07T12:30:05] Canonical knowledge packages written to /output/knowledge/. Ready for Neo4j Aura & Pinecone.`}
        </pre>
      </div>
    </div>
  );
}
