import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  Send, 
  Database, 
  Radio, 
  GitCommit, 
  CheckCircle2, 
  FileText, 
  Code, 
  ArrowRight, 
  ShieldCheck, 
  Cpu,
  Layers,
  Terminal,
  Activity
} from 'lucide-react';
import SpatialCard from '../components/SpatialCard';
import { INVESTIGATION_SAMPLES } from '../data/mockData';

export default function InvestigationView({ initialSample }) {
  const [selectedSample, setSelectedSample] = useState(initialSample || INVESTIGATION_SAMPLES[0]);
  const [inputValue, setInputValue] = useState('');
  const [isInvestigating, setIsInvestigating] = useState(false);
  const [activeStep, setActiveStep] = useState(3); // 1: Intent, 2: Retrieval, 3: Synthesis

  useEffect(() => {
    if (initialSample) {
      setSelectedSample(initialSample);
    }
  }, [initialSample]);

  const handleSelectSample = (sample) => {
    setSelectedSample(sample);
    setIsInvestigating(true);
    setActiveStep(1);

    setTimeout(() => {
      setActiveStep(2);
      setTimeout(() => {
        setActiveStep(3);
        setIsInvestigating(false);
      }, 350);
    }, 300);
  };

  const handleCustomSubmit = (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    setIsInvestigating(true);
    setActiveStep(1);

    // Dynamic generation simulation for user query
    setTimeout(() => {
      setActiveStep(2);
      setTimeout(() => {
        setSelectedSample({
          id: 'custom-' + Date.now(),
          question: inputValue,
          intent: 'COMBINED',
          confidence: '97.2%',
          cypherQuery: `MATCH (p:Program)-[:WRITES_TO|READS_FROM]->(t:Table)\nWHERE p.name CONTAINS 'PREM' OR t.name CONTAINS 'PREM'\nRETURN p, t LIMIT 10;`,
          pineconeMatch: {
            score: 0.928,
            source: 'EARNPREM.CBL (Lines 15-28)',
            vectorCluster: 'kairix_chunks'
          },
          answer: `Analysis completed across Neo4j Aura knowledge graph and Pinecone vector store: The inquiry regarding "${inputValue}" traces back to core policy accounting routines. Lineage confirms cross-system dependency with downstream SQL reporting scripts.`,
          formula: "WS-CALC-FACTOR = (CURRENT_DATE - EFF_DATE) / TERM_DAYS",
          lineageTrail: [
            "Source Batch Routine",
            "Staging Data Layer",
            "SQL Reporting View"
          ],
          anchors: ["EARNPREM.CBL:L18-L25", "PolicyCenter_Monoline.sql:L12-L14"]
        });
        setActiveStep(3);
        setIsInvestigating(false);
        setInputValue('');
      }, 400);
    }, 350);
  };

  return (
    <div className="investigation-container">
      {/* Top Banner with Spatial Search Input */}
      <div className="glass-panel investigation-hero">
        <div className="investigation-header-top">
          <div className="badge badge-purple">
            <Sparkles size={13} />
            <span>Multi-Agent Hybrid Copilot</span>
          </div>
          <span className="live-indicator">
            NVIDIA NIM nematron-3-ultra • Neo4j Aura • Pinecone
          </span>
        </div>

        <h2 className="investigation-title">
          Ask Any <span className="gradient-text-cyan">Legacy Architecture Question</span>
        </h2>
        <p className="investigation-subtitle">
          Concurrent dual-path investigation: Graph traversal for structural lineage + Vector search for functional implementation.
        </p>

        {/* Input Bar */}
        <form onSubmit={handleCustomSubmit} className="investigation-form">
          <input
            type="text"
            className="investigation-input"
            placeholder="E.g., How is earned premium calculated in EARNPREM.CBL and where does it feed?"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
          />
          <button type="submit" className="btn btn-primary" disabled={isInvestigating}>
            {isInvestigating ? (
              <>
                <Activity size={15} className="spin-icon" /> Investigating...
              </>
            ) : (
              <>
                <Send size={15} /> Investigate
              </>
            )}
          </button>
        </form>

        {/* Quick Question Chips */}
        <div className="sample-chips-row">
          <span className="sample-chips-label">Quick Prompts:</span>
          {INVESTIGATION_SAMPLES.map((sample) => (
            <button
              key={sample.id}
              className={`sample-chip ${selectedSample?.id === sample.id ? 'sample-chip-active' : ''}`}
              onClick={() => handleSelectSample(sample)}
            >
              {sample.question}
            </button>
          ))}
        </div>
      </div>

      {/* Execution Multi-Lane Visualization */}
      {selectedSample && (
        <div className="investigation-result-layout">
          {/* Lane 1: Intent & Execution Trace */}
          <div className="trace-column">
            {/* Step 1: Intent Detection */}
            <SpatialCard className="trace-card">
              <div className="trace-card-header">
                <span className="step-number">01</span>
                <span className="trace-step-title">Intent Detection</span>
                <span className={`badge ${selectedSample.intent === 'COMBINED' ? 'badge-cyan' : selectedSample.intent === 'LINEAGE' ? 'badge-purple' : 'badge-emerald'}`}>
                  {selectedSample.intent}
                </span>
              </div>
              <p className="trace-desc">
                Question analyzed. Routed to concurrent <strong>Graph Traversal</strong> and <strong>Semantic Vector Matching</strong>.
              </p>
              <div className="trace-meta-pill">
                <span>Routing Confidence</span>
                <strong className="text-cyan">{selectedSample.confidence}</strong>
              </div>
            </SpatialCard>

            {/* Step 2A: Neo4j Aura Graph Lane */}
            <SpatialCard className="trace-card">
              <div className="trace-card-header">
                <span className="step-number">02A</span>
                <span className="trace-step-title">Neo4j Aura Traversal</span>
                <Database size={15} className="pill-icon-cyan" />
              </div>
              <p className="trace-desc">Dynamically generated & executed Cypher query:</p>
              <pre className="code-preview font-mono trace-code">
                {selectedSample.cypherQuery}
              </pre>
              <div className="trace-meta-pill">
                <span>Traversal Status</span>
                <strong className="text-emerald">Lines Linked • 0 Duplicates</strong>
              </div>
            </SpatialCard>

            {/* Step 2B: Pinecone Vector Search Lane */}
            <SpatialCard className="trace-card">
              <div className="trace-card-header">
                <span className="step-number">02B</span>
                <span className="trace-step-title">Pinecone Vector Search</span>
                <Radio size={15} className="pill-icon-purple" />
              </div>
              <p className="trace-desc">Dense semantic vector search across 384-dim code chunks:</p>
              <div className="vector-match-box">
                <div className="vector-match-row">
                  <span>Match Similarity:</span>
                  <strong className="text-purple">{(selectedSample.pineconeMatch.score * 100).toFixed(1)}% Cosine Match</strong>
                </div>
                <div className="vector-match-row">
                  <span>Target Cluster:</span>
                  <span className="font-mono text-secondary">{selectedSample.pineconeMatch.vectorCluster}</span>
                </div>
                <div className="vector-match-row">
                  <span>Evidence Snippet:</span>
                  <span className="font-mono text-cyan">{selectedSample.pineconeMatch.source}</span>
                </div>
              </div>
            </SpatialCard>
          </div>

          {/* Lane 2: Final Synthesized Answer & Evidence Anchoring */}
          <div className="evidence-column">
            <SpatialCard className="synthesis-card">
              <div className="synthesis-header">
                <div className="synthesis-badge">
                  <ShieldCheck size={16} className="text-emerald" />
                  <span>Synthesized Reverse Engineering Answer</span>
                </div>
                <span className="badge badge-emerald">Evidence-Backed</span>
              </div>

              {/* Natural Language Answer */}
              <div className="synthesis-body">
                <h3 className="synthesis-question">{selectedSample.question}</h3>
                <p className="synthesis-answer-text">{selectedSample.answer}</p>

                {/* Mathematical / Calculation Formula Card */}
                {selectedSample.formula && (
                  <div className="formula-box">
                    <div className="formula-label">
                      <Code size={14} /> Extracted Business / Calculation Formula:
                    </div>
                    <div className="formula-code font-mono">
                      {selectedSample.formula}
                    </div>
                  </div>
                )}

                {/* End-to-End Data Lineage Chain */}
                <div className="lineage-chain-section">
                  <h4 className="lineage-title">
                    <GitCommit size={15} /> Verified Cross-System Data Lineage:
                  </h4>
                  <div className="lineage-steps">
                    {selectedSample.lineageTrail.map((step, idx) => (
                      <div key={idx} className="lineage-step-item">
                        <span className="lineage-dot" />
                        <span className="lineage-step-text">{step}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Line-Anchored Code Proof Badges */}
                <div className="anchors-section">
                  <span className="anchors-label">Verifiable Source Code Citations:</span>
                  <div className="anchors-list">
                    {selectedSample.anchors.map((anchor, idx) => (
                      <span key={idx} className="anchor-pill font-mono">
                        <FileText size={12} /> {anchor}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </SpatialCard>
          </div>
        </div>
      )}
    </div>
  );
}
