import React from 'react';
import { 
  LayoutDashboard, 
  Network, 
  Sparkles, 
  Code2, 
  GitMerge, 
  Database, 
  Cpu, 
  Radio
} from 'lucide-react';

export default function Header({ activeView, onViewChange }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'graph', label: 'Knowledge Graph', icon: Network },
    { id: 'investigation', label: 'Investigation Agent', icon: Sparkles, highlight: true },
    { id: 'sources', label: 'Source Explorer', icon: Code2 },
    { id: 'pipeline', label: 'Pipeline Engine', icon: GitMerge }
  ];

  return (
    <header className="spatial-header">
      <div className="header-container">
        {/* User Brand Logo & Tag */}
        <div className="brand-zone" onClick={() => onViewChange('dashboard')} title="KAIRIX Enterprise Reverse Engineering Workbench">
          <div className="brand-logo-container">
            <img 
              src="/kairix_emblem_transparent.png" 
              alt="KAIRIX Emblem" 
              className="brand-logo-img"
              onError={(e) => { e.currentTarget.src = '/kairix_logo.svg'; }}
            />
          </div>
          <div>
            <div className="brand-title">
              KAIRIX <span className="brand-version">v2.4 SPATIAL</span>
            </div>
            <div className="brand-subtitle">Legacy Multi-Agent RAG</div>
          </div>
        </div>

        {/* Floating Spatial Navigation Dock */}
        <nav className="spatial-dock">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeView === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onViewChange(item.id)}
                className={`dock-tab ${isActive ? 'dock-tab-active' : ''} ${item.highlight ? 'dock-tab-highlight' : ''}`}
              >
                <Icon size={16} className="dock-icon" />
                <span>{item.label}</span>
                {isActive && <div className="dock-active-glow" />}
              </button>
            );
          })}
        </nav>

        {/* Live Cloud Infrastructure Telemetry */}
        <div className="telemetry-zone">
          <div className="telemetry-pill" title="Neo4j Aura Managed Knowledge Graph">
            <Database size={13} className="pill-icon-cyan" />
            <span>Neo4j Aura</span>
            <span className="pulse-dot pulse-cyan" />
          </div>

          <div className="telemetry-pill" title="Pinecone Serverless Vector Store">
            <Radio size={13} className="pill-icon-purple" />
            <span>Pinecone</span>
            <span className="pulse-dot pulse-emerald" />
          </div>

          <div className="telemetry-pill" title="NVIDIA NIM nematron-3-ultra Engine">
            <Cpu size={13} className="pill-icon-amber" />
            <span>NVIDIA NIM</span>
            <span className="pulse-dot pulse-emerald" />
          </div>
        </div>
      </div>
    </header>
  );
}
