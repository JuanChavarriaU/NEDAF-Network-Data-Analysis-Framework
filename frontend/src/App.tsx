import { useState } from 'react';
import { Sidebar } from './Sidebar';
import { ExploreData } from './ExploreData';
import { ImportData } from './ImportData';
import { NetworkVisualization } from './NetworkVisualization';
import { LLMInsights } from './LLMInsights';

function App() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [activeView, setActiveView] = useState('explore');

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-dark-bg">
      <Sidebar 
        isCollapsed={isCollapsed} 
        setIsCollapsed={setIsCollapsed} 
        activeView={activeView}
        setActiveView={setActiveView}
      />
      
      <main className="flex-1 relative flex flex-col h-full overflow-hidden p-6">
        {/* Background ambient light effects */}
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-brand-600/10 rounded-full blur-[120px] pointer-events-none" />
        <div className="absolute bottom-0 left-1/4 w-[400px] h-[400px] bg-indigo-900/10 rounded-full blur-[100px] pointer-events-none" />
        
        <div className="relative z-10 w-full max-w-7xl mx-auto h-full">
          {activeView === 'explore' && <ExploreData />}
          {activeView === 'import' && <ImportData />}
          {activeView === 'network' && <NetworkVisualization />}
          {activeView === 'ai' && <LLMInsights />}
        </div>
      </main>
    </div>
  );
}

export default App;
