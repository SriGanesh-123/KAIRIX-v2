import React from 'react';
import { 
  FileCode, 
  Binary, 
  GitFork, 
  CheckCircle, 
  ArrowRight, 
  Sparkles, 
  Database, 
  Layers, 
  Search,
  ExternalLink,
  ShieldCheck,
  Zap
} from 'lucide-react';
import SpatialCard from '../components/SpatialCard';
import { SYSTEM_METRICS, PIPELINE_LAYERS, SOURCE_FILES, INVESTIGATION_SAMPLES } from '../data/mockData';

export default function DashboardView({ onNavigate, onLaunchQuery }) {
  const kpis = [
    {
      title: "Analyzed Artifacts",
      value: SYSTEM_METRICS.totalFiles,
      breakdown: `${SYSTEM_METRICS.cobolPrograms} COBOL • ${SYSTEM_METRICS.sqlScripts} SQL • ${SYSTEM_METRICS.ssisPackages} SSIS`,
      icon: FileCode,
      color: "var(--cyan-neon)",
      glow: "var(--cyan-glow)"
    },
    {
      title: "Knowledge Graph Entities",
      value: SYSTEM_METRICS.graphEntities.toLocaleString(),
      breakdown: `${SYSTEM_METRICS.graphRelationships.toLocaleString()} Lineage Connections in Neo4j Aura`,
      icon: Database,
      color: "#a78bfa",
      glow: "var(--purple-glow)"
    },
    {
      title: "Extracted Business Rules",
      value: SYSTEM_METRICS.businessRules,
      breakdown: `${SYSTEM_METRICS.transformations} AST Data Mappings Reconciled`,
      icon: ShieldCheck,
      color: "var(--emerald-neon)",
      glow: "var(--emerald-glow)"
    },
    {
      title: "Vector Embeddings",
      value: SYSTEM_METRICS.pineconeChunks.toLocaleString(),
      breakdown: `Pinecone Serverless (${SYSTEM_METRICS.embeddingDimension}-dim MiniLM)`,
      icon: Zap,
      color: "var(--amber-neon)",
      glow: "var(--amber-glow)"
    }
  ];

  return (
    <div className="dashboard-container">
      {/* Hero Holographic Banner */}
      <div className="glass-panel hero-panel">
        <div className="hero-content">
          <div className="hero-badge">
            <span className="pulse-dot pulse-cyan" />
            <span>ENTERPRISE REVERSE ENGINEERING HUD</span>
          </div>
          <h1 className="hero-title">
            Spatial Intelligence for <span className="gradient-text-cyan">Legacy Codebases</span>
          </h1>
          <p className="hero-description">
            Reverse-engineer Mainframe COBOL, SQL stored procedures, and Guidewire SSIS ETL pipelines. 
            Powered by deterministic AST parsing, <strong>Neo4j Aura</strong> knowledge graphs, 
            <strong>Pinecone</strong> vector search, and multi-agent hybrid reasoning.
          </p>
          <div className="hero-actions">
            <button 
              className="btn btn-primary"
              onClick={() => onNavigate('investigation')}
            >
              <Sparkles size={16} />
              Launch Investigation Copilot
            </button>
            <button 
              className="btn btn-glass"
              onClick={() => onNavigate('graph')}
            >
              <Database size={16} />
              Explore Neo4j Knowledge Graph
            </button>
          </div>
        </div>
        <div className="hero-glow-sphere" />
      </div>

      {/* KPI Metrics Grid */}
      <div className="metrics-grid">
        {kpis.map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <SpatialCard key={idx} className="metric-card">
              <div className="metric-header">
                <span className="metric-title">{kpi.title}</span>
                <div className="metric-icon-box" style={{ background: kpi.glow, color: kpi.color }}>
                  <Icon size={18} />
                </div>
              </div>
              <div className="metric-value">{kpi.value}</div>
              <div className="metric-breakdown">{kpi.breakdown}</div>
            </SpatialCard>
          );
        })}
      </div>

      {/* 4-Layer Architecture Map */}
      <div className="section-block">
        <div className="section-header">
          <div>
            <h2 className="section-title">End-to-End System Pipeline</h2>
            <p className="section-subtitle">Real-time status of the 4 autonomous platform layers</p>
          </div>
          <button className="btn btn-glass btn-sm" onClick={() => onNavigate('pipeline')}>
            View LangGraph Details <ArrowRight size={14} />
          </button>
        </div>

        <div className="layers-grid">
          {PIPELINE_LAYERS.map((layer, index) => (
            <SpatialCard key={layer.id} className="layer-card">
              <div className="layer-card-top">
                <span className="layer-step-badge">0{index + 1}</span>
                <span className="badge badge-cyan">{layer.badge}</span>
              </div>
              <h3 className="layer-title">{layer.name}</h3>
              <div className="layer-tech">{layer.tech}</div>
              <p className="layer-desc">{layer.description}</p>
              <div className="layer-status-row">
                <span className="pulse-dot pulse-emerald" />
                <span className="layer-status-text">{layer.status}</span>
              </div>
            </SpatialCard>
          ))}
        </div>
      </div>

      {/* Quick Interactive Investigation Launchpad */}
      <div className="section-block">
        <div className="section-header">
          <div>
            <h2 className="section-title">Pre-Engineered Investigation Prompts</h2>
            <p className="section-subtitle">Test multi-agent hybrid reasoning on real legacy calculations</p>
          </div>
        </div>

        <div className="prompts-grid">
          {INVESTIGATION_SAMPLES.map((sample) => (
            <SpatialCard 
              key={sample.id} 
              className="prompt-card glass-interactive"
              onClick={() => onLaunchQuery(sample)}
            >
              <div className="prompt-card-header">
                <span className={`badge ${sample.intent === 'COMBINED' ? 'badge-cyan' : sample.intent === 'LINEAGE' ? 'badge-purple' : 'badge-emerald'}`}>
                  {sample.intent} RETRIEVAL
                </span>
                <span className="confidence-pill">Confidence: {sample.confidence}</span>
              </div>
              <div className="prompt-question">{sample.question}</div>
              <div className="prompt-bottom">
                <span className="prompt-run-text">Run Query on Neo4j Aura + Pinecone</span>
                <ArrowRight size={14} className="prompt-arrow" />
              </div>
            </SpatialCard>
          ))}
        </div>
      </div>
    </div>
  );
}
