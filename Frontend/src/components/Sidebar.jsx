import React from 'react';
import { 
  Sparkles, 
  FileCode, 
  GitMerge, 
  Network,
  Activity,
  CheckCircle2,
  ArrowRight
} from 'lucide-react';

export default function Sidebar({ 
  activeView, 
  onViewChange,
  activeTask = null, // { type: 'investigation' | 'extraction', status: 'running' | 'complete', title: '' }
}) {
  const navItems = [
    { id: 'investigation', label: 'Investigation Agent' },
    { id: 'sources', label: 'Source Explorer' },
    { id: 'pipeline', label: 'Pipeline' },
    { id: 'graph', label: 'Knowledge Graph' }
  ];

  return (
    <aside className="app-sidebar">
      {/* Brand Header with Official Logo pinned to top-left */}
      <div className="sidebar-brand" onClick={() => onViewChange('investigation')} style={{ cursor: 'pointer' }}>
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

      {/* Main Navigation (4 Options Only) */}
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

      {/* Active Background Task Toast Notification matching Streamlit */}
      {activeTask && (
        <div className={`sidebar-task-banner ${activeTask.status}`}>
          <div className="task-banner-header">
            {activeTask.status === 'running' ? (
              <>
                <span className="pulse-dot-green" />
                <span className="task-status-text">
                  {activeTask.type === 'investigation' ? 'AI Investigation Running...' : 'AST Extraction Running...'}
                </span>
              </>
            ) : (
              <>
                <span>✨</span>
                <span className="task-status-text">
                  {activeTask.type === 'investigation' ? 'Answer Ready!' : 'Extraction Ready!'}
                </span>
              </>
            )}
          </div>
          {activeTask.title && (
            <div className="task-snippet-text font-mono">
              "{activeTask.title.slice(0, 32)}..."
            </div>
          )}
          {activeTask.status === 'complete' && activeView !== 'investigation' && (
            <button 
              className="btn-task-action"
              onClick={() => onViewChange('investigation')}
            >
              View Result →
            </button>
          )}
        </div>
      )}

      {/* Divider */}
      <div className="sidebar-divider" />

      {/* Backend Services Status Card matching Streamlit */}
      <div className="sidebar-footer">
        <div className="services-section-title">BACKEND SERVICES</div>
        <div className="services-card neo-inset">
          <div className="service-row">
            <div className="service-name">
              <span className="status-indicator-dot dot-green" />
              <span>Neo4j Graph</span>
            </div>
            <span className="service-latency font-mono">12.4ms</span>
          </div>

          <div className="service-row">
            <div className="service-name">
              <span className="status-indicator-dot dot-green" />
              <span>Pinecone DB</span>
            </div>
            <span className="service-latency font-mono">18.2ms</span>
          </div>

          <div className="service-row">
            <div className="service-name">
              <span className="status-indicator-dot dot-green" />
              <span>LLM Provider</span>
            </div>
            <span className="service-latency font-mono font-bold text-cyan">NIM</span>
          </div>
        </div>

        <div className="sidebar-version-tag">
          KAIRIX Enterprise Workbench v2.0
        </div>
      </div>
    </aside>
  );
}
