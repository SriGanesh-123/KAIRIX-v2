import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';
import SourceExplorerView from './views/SourceExplorerView';
import InvestigationView from './views/InvestigationView';
import PipelineView from './views/PipelineView';
import KnowledgeGraphView from './views/KnowledgeGraphView';
import DashboardView from './views/DashboardView';
import './App.css';

export default function App() {
  const [activeView, setActiveView] = useState('sources');
  const [displayedView, setDisplayedView] = useState('sources');
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [activeInvestigationSample, setActiveInvestigationSample] = useState(null);

  const handleViewChange = (newView) => {
    if (newView === activeView || isTransitioning) return;
    setActiveView(newView);
    setIsTransitioning(true);

    setTimeout(() => {
      setDisplayedView(newView);
      window.scrollTo({ top: 0, behavior: 'smooth' });
      setTimeout(() => {
        setIsTransitioning(false);
      }, 40);
    }, 220);
  };

  const handleNavigateToInvestigate = (filename) => {
    handleViewChange('investigation');
  };

  return (
    <div className="app-shell-layout">
      {/* Left Sidebar matching screenshot */}
      <Sidebar activeView={activeView} onViewChange={handleViewChange} />

      {/* Main Content Area */}
      <div className="app-main-area">
        <TopBar />
        <main className="app-content-container">
          <div className={`page-transition-wrapper ${isTransitioning ? 'page-transition-exiting' : 'page-transition-entering'}`}>
            {displayedView === 'sources' && (
              <SourceExplorerView onNavigateToInvestigate={handleNavigateToInvestigate} />
            )}
            {displayedView === 'investigation' && (
              <InvestigationView initialSample={activeInvestigationSample} />
            )}
            {displayedView === 'pipeline' && (
              <PipelineView />
            )}
            {displayedView === 'graph' && (
              <KnowledgeGraphView />
            )}
            {displayedView === 'dashboard' && (
              <DashboardView onNavigate={handleViewChange} onLaunchQuery={handleNavigateToInvestigate} />
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
