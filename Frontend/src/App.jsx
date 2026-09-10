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
  // Default landing view is Investigation Agent, matching Streamlit
  const [activeView, setActiveView] = useState('investigation');
  const [displayedView, setDisplayedView] = useState('investigation');
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [activeInvestigationSample, setActiveInvestigationSample] = useState(null);
  const [pendingInvestigationQuery, setPendingInvestigationQuery] = useState(null);
  const [activeTask, setActiveTask] = useState(null);

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
    }, 200);
  };

  const handleNavigateToInvestigate = (queryOrFilename) => {
    if (typeof queryOrFilename === 'string') {
      setPendingInvestigationQuery(queryOrFilename);
    }
    handleViewChange('investigation');
  };

  return (
    <div className="app-shell-layout">
      {/* Left Navigation Sidebar matching Streamlit */}
      <Sidebar 
        activeView={activeView} 
        onViewChange={handleViewChange} 
        activeTask={activeTask}
      />

      {/* Main Workbench Area */}
      <div className="app-main-area">
        <TopBar />
        <main className="app-content-container">
          <div className={`page-transition-wrapper ${isTransitioning ? 'page-transition-exiting' : 'page-transition-entering'}`}>
            {displayedView === 'investigation' && (
              <InvestigationView 
                initialSample={activeInvestigationSample}
                initialQuery={pendingInvestigationQuery}
                onNavigateToGraph={() => handleViewChange('graph')}
                onNavigateToSource={() => handleViewChange('sources')}
              />
            )}
            {displayedView === 'sources' && (
              <SourceExplorerView 
                onNavigateToInvestigate={handleNavigateToInvestigate} 
              />
            )}
            {displayedView === 'pipeline' && (
              <PipelineView />
            )}
            {displayedView === 'graph' && (
              <KnowledgeGraphView />
            )}
            {displayedView === 'dashboard' && (
              <DashboardView 
                onNavigate={handleViewChange} 
                onLaunchQuery={handleNavigateToInvestigate} 
              />
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
