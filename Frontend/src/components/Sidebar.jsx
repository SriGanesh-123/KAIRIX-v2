import React from 'react';
import { 
  FileCode, 
  Search, 
  GitMerge, 
  Network,
  Database,
  Radio,
  Cpu,
  Sparkles
} from 'lucide-react';

export default function Sidebar({ activeView, onViewChange }) {
  const navItems = [
    { id: 'investigation', label: 'Investigation Agent' },
    { id: 'sources', label: 'Source Explorer' },
    { id: 'pipeline', label: 'Pipeline' },
    { id: 'graph', label: 'Knowledge Graph' }
  ];

  return (
    <aside className="app-sidebar">
      {/* Brand Header */}
      <div className="sidebar-brand" onClick={() => onViewChange('sources')}>
        <div className="sidebar-logo-box">
          <img 
            src="/kairix_emblem_transparent.png" 
            alt="KAIRIX" 
            className="sidebar-logo-img"
            onError={(e) => { e.currentTarget.src = '/kairix_logo.svg'; }}
          />
        </div>
        <div className="sidebar-brand-text">
          <div className="sidebar-brand-title">KAIRIX</div>
          <div className="sidebar-brand-subtitle">INVESTIGATION AGENT</div>
        </div>
      </div>

      {/* Navigation Buttons List */}
      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const isActive = activeView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onViewChange(item.id)}
              className={`sidebar-nav-btn ${isActive ? 'sidebar-nav-btn-active' : ''}`}
            >
              {item.label}
            </button>
          );
        })}
      </nav>

      {/* Divider */}
      <div className="sidebar-divider" />

      {/* Backend Services Status Card */}
      <div className="sidebar-footer">
        <div className="services-section-title">BACKEND SERVICES</div>
        <div className="services-card">
          <div className="service-row">
            <div className="service-name">
              <span className="status-indicator-dot dot-green" />
              <span>Neo4j Graph</span>
            </div>
            <span className="service-latency font-mono">528.9ms</span>
          </div>

          <div className="service-row">
            <div className="service-name">
              <span className="status-indicator-dot dot-green" />
              <span>Pinecone DB</span>
            </div>
            <span className="service-latency font-mono">693.5ms</span>
          </div>

          <div className="service-row">
            <div className="service-name">
              <span className="status-indicator-dot dot-green" />
              <span>LLM Provider</span>
            </div>
            <span className="service-latency font-mono font-bold">NIM</span>
          </div>
        </div>

        <div className="sidebar-version-tag">
          KAIRIX Enterprise Workbench v2.0
        </div>
      </div>
    </aside>
  );
}
