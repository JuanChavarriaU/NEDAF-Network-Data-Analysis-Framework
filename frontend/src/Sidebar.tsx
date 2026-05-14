import { Database, LineChart, Network, ChevronLeft, Menu, BrainCircuit } from 'lucide-react';

interface SidebarProps {
  isCollapsed: boolean;
  setIsCollapsed: (value: boolean) => void;
  activeView: string;
  setActiveView: (view: string) => void;
}

const navItems = [
  { id: 'import', label: 'Import Data', icon: Database },
  { id: 'explore', label: 'Explore Data', icon: LineChart },
  { id: 'network', label: 'Network Visualization', icon: Network },
  { id: 'ai', label: 'LLM Insights', icon: BrainCircuit },
];

export function Sidebar({ isCollapsed, setIsCollapsed, activeView, setActiveView }: SidebarProps) {
  return (
    <aside
      className={`relative flex flex-col h-full bg-dark-panel border-r border-dark-border transition-all duration-300 ease-in-out ${
        isCollapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between h-16 px-4 border-b border-dark-border">
        {!isCollapsed && (
          <span className="text-xl font-bold tracking-wider text-white truncate">NEDAF</span>
        )}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className={`p-2 rounded-lg hover:bg-dark-hover transition-colors text-gray-400 hover:text-white ${isCollapsed ? 'mx-auto' : ''}`}
        >
          {isCollapsed ? <Menu size={20} /> : <ChevronLeft size={20} />}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-3 space-y-2 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveView(item.id)}
              className={`w-full flex items-center p-3 rounded-xl transition-all duration-200 group relative ${
                isActive
                  ? 'bg-brand-600/20 text-brand-400'
                  : 'text-gray-400 hover:bg-dark-hover hover:text-gray-200'
              } ${isCollapsed ? 'justify-center' : 'justify-start'}`}
            >
              <Icon size={22} className={`shrink-0 ${isActive ? 'text-brand-400' : 'group-hover:text-gray-200'}`} />
              {!isCollapsed && (
                <span className="ml-3 font-medium whitespace-nowrap">{item.label}</span>
              )}
              
              {/* Tooltip for collapsed state */}
              {isCollapsed && (
                <div className="absolute left-full ml-4 px-3 py-2 bg-gray-800 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 pointer-events-none z-50 whitespace-nowrap shadow-xl transition-opacity">
                  {item.label}
                  <div className="absolute -left-1 top-1/2 -translate-y-1/2 w-2 h-2 bg-gray-800 rotate-45"></div>
                </div>
              )}
            </button>
          );
        })}
      </nav>
      
      {/* Footer / User Profile */}
      <div className="p-4 border-t border-dark-border">
        <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'justify-start'} gap-3`}>
          <div className="w-8 h-8 rounded-full bg-brand-600 flex items-center justify-center shrink-0 text-sm font-bold text-white shadow-lg">
            JD
          </div>
          {!isCollapsed && (
            <div className="flex flex-col truncate">
              <span className="text-sm font-medium text-gray-200">Juan Doe</span>
              <span className="text-xs text-gray-500">Data Scientist</span>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
