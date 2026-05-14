import { useEffect, useState, useRef, useCallback } from 'react';
import { Network, ZoomIn, Loader2, ChevronDown, Calculator, X, AlertCircle, RefreshCw, Layers } from 'lucide-react';
import ForceGraph2D from 'react-force-graph-2d';
import { GraphVisualizationAPI, handleApiError, type SampleParams, type SamplingStrategy, type SampleMetrics } from './services/api';

const METRICS = [
  "Number of Nodes", "Number of Edges", "Maximum Degree", "Minimum Degree", 
  "Average Degree", "Assortativity", "Number of triangles", "Network Degree", 
  "Network Density", "Network Diameter", "Network Radius", "Network Average Clustering", 
  "Network Average Degree Conectivity", "Network Average Path Length", "Network Degree Distribution", 
  "Network Clustering Coefficient", "Network Communities", "Network Modularity", 
  "Number of Communities", "Network Community Size", "Network Key Nodes", 
  "Community Leader Nodes", "Network Isolates", "Network Degree Centrality", 
  "Network Betweenness Centrality", "Network Closeness Centrality", 
  "Network Eigenvector Centrality", "Network PageRank"
];

export function NetworkVisualization() {
  const fgRef = useRef<any>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [graphData, setGraphData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Sampling State
  const [sampleConfig, setSampleConfig] = useState<SampleParams>({ n_edges: 1000, strategy: 'degree_weighted' });
  const [sampleMetrics, setSampleMetrics] = useState<SampleMetrics | null>(null);
  const [isFullGraph, setIsFullGraph] = useState(false);

  // Metric state
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [calculatingMetric, setCalculatingMetric] = useState(false);
  const [metricResult, setMetricResult] = useState<{ metric: string, result: any } | null>(null);

  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.clientWidth,
          height: containerRef.current.clientHeight
        });
      }
    };
    
    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  const fetchGraph = useCallback(async (full = false) => {
    try {
      setIsLoading(true);
      setError(null);
      setIsDropdownOpen(false);
      
      let data;
      if (full) {
        data = await GraphVisualizationAPI.getLayout();
        setSampleMetrics(null);
        setIsFullGraph(true);
      } else {
        data = await GraphVisualizationAPI.getSample(sampleConfig);
        setSampleMetrics(data.metrics as SampleMetrics);
        setIsFullGraph(false);
      }
      
      setGraphData({ nodes: data.nodes, links: data.edges });
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setIsLoading(false);
    }
  }, [sampleConfig]);

  // Load sample on initial mount
  useEffect(() => {
    fetchGraph(false);
  }, [fetchGraph]);

  const handleZoomToFit = useCallback(() => {
    if (fgRef.current) {
      fgRef.current.zoomToFit(400);
    }
  }, []);

  const handleCalculateMetric = async (metric: string) => {
    try {
      setIsDropdownOpen(false);
      setCalculatingMetric(true);
      const data = await GraphVisualizationAPI.getMetric(metric);
      setMetricResult(data);
    } catch (err) {
      alert(handleApiError(err));
    } finally {
      setCalculatingMetric(false);
    }
  };

  const formatResult = (res: any) => {
    if (typeof res === 'object' && res !== null) {
      return JSON.stringify(res, null, 2).slice(0, 500) + (JSON.stringify(res).length > 500 ? '...' : '');
    }
    return String(res);
  };

  const colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#f97316'];
  const getNodeColor = (node: any) => colors[node.community % colors.length] || colors[0];

  return (
    <div className="flex flex-col h-full animate-fade-in fade-in zoom-in duration-300">
      <header className="glass-panel mb-4 p-5 flex flex-col gap-4 relative z-20">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <Network className="text-brand-400" />
              Network Visualization
            </h1>
            <p className="text-sm text-gray-400 mt-1">Interactive WebGL-powered graph analysis.</p>
          </div>
          
          <div className="flex items-center gap-3">
            {/* Operations Dropdown */}
            <div className="relative">
              <button 
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="px-4 py-2 bg-brand-600 hover:bg-brand-500 text-white border border-brand-500 rounded-lg text-sm transition-colors flex items-center gap-2 shadow-lg shadow-brand-900/50"
                disabled={isLoading || !graphData || calculatingMetric}
              >
                {calculatingMetric ? <Loader2 size={16} className="animate-spin" /> : <Calculator size={16} />}
                {calculatingMetric ? 'Calculating...' : 'Metrics & Ops'}
                <ChevronDown size={14} className={isDropdownOpen ? "rotate-180 transition-transform" : "transition-transform"} />
              </button>
              
              {isDropdownOpen && (
                <>
                  <div className="fixed inset-0 z-30" onClick={() => setIsDropdownOpen(false)} />
                  <div className="absolute right-0 mt-2 w-64 max-h-96 overflow-y-auto bg-dark-panel border border-dark-border rounded-xl shadow-2xl z-40 py-1 animate-in fade-in slide-in-from-top-2 duration-200 custom-scrollbar">
                    {METRICS.map(m => (
                      <button 
                        key={m}
                        onClick={() => handleCalculateMetric(m)}
                        className="w-full text-left px-4 py-2.5 text-sm text-gray-300 hover:text-white hover:bg-dark-hover transition-colors"
                      >
                        {m}
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>

            <button 
              onClick={handleZoomToFit}
              className="px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-sm text-gray-300 hover:text-white transition-colors flex items-center gap-2"
            >
              <ZoomIn size={16} /> Fit to Screen
            </button>
          </div>
        </div>

        {/* Progressive Sampling Toolbar */}
        <div className="flex flex-wrap items-center gap-4 bg-dark-bg/40 p-3 rounded-lg border border-dark-border/50">
          <div className="flex items-center gap-2">
            <Layers size={16} className="text-brand-400" />
            <span className="text-sm font-medium text-gray-300">Sampling Strategy:</span>
            <select 
              value={sampleConfig.strategy}
              onChange={(e) => setSampleConfig(prev => ({ ...prev, strategy: e.target.value as SamplingStrategy }))}
              className="bg-dark-panel border border-dark-border text-sm text-white rounded px-2 py-1 outline-none focus:border-brand-500"
              disabled={isLoading || isFullGraph}
            >
              <option value="degree_weighted">Degree-Weighted (Hubs)</option>
              <option value="snowball">Snowball (Connected)</option>
              <option value="random">Random (Fastest)</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-300">Edges:</span>
            <select 
              value={sampleConfig.n_edges}
              onChange={(e) => setSampleConfig(prev => ({ ...prev, n_edges: Number(e.target.value) }))}
              className="bg-dark-panel border border-dark-border text-sm text-white rounded px-2 py-1 outline-none focus:border-brand-500"
              disabled={isLoading || isFullGraph}
            >
              <option value={100}>100 (Tiny)</option>
              <option value={500}>500 (Small)</option>
              <option value={1000}>1,000 (Medium)</option>
              <option value={5000}>5,000 (Large)</option>
              <option value={10000}>10,000 (Very Large)</option>
            </select>
          </div>

          <div className="flex items-center gap-2 ml-auto">
            {!isFullGraph ? (
              <button 
                onClick={() => fetchGraph(false)}
                className="px-3 py-1.5 bg-dark-panel hover:bg-dark-hover border border-dark-border rounded text-sm text-gray-300 hover:text-white transition-colors flex items-center gap-2"
                disabled={isLoading}
              >
                <RefreshCw size={14} className={isLoading ? "animate-spin" : ""} /> Update Sample
              </button>
            ) : (
              <span className="text-xs font-medium px-2 py-1 bg-brand-500/20 text-brand-400 rounded border border-brand-500/30">
                Viewing Full Dataset
              </span>
            )}
            
            <button 
              onClick={() => {
                if (isFullGraph) fetchGraph(false);
                else fetchGraph(true);
              }}
              className={`px-3 py-1.5 border rounded text-sm transition-colors flex items-center gap-2 ${
                isFullGraph 
                  ? "bg-dark-panel border-dark-border text-gray-300 hover:text-white hover:bg-dark-hover"
                  : "bg-purple-600/20 border-purple-500/50 text-purple-300 hover:bg-purple-600/30"
              }`}
              disabled={isLoading}
            >
              {isFullGraph ? "Back to Sampling" : "Load Full Graph (Warning: Slow)"}
            </button>
          </div>
        </div>
      </header>

      <div className="flex-1 glass-panel relative overflow-hidden flex items-center justify-center bg-dark-bg/30" ref={containerRef}>
        <div className="absolute inset-0 pattern-grid opacity-5 pointer-events-none" style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)', backgroundSize: '32px 32px' }} />
        
        {/* Sample Metrics Overlay */}
        {!isLoading && sampleMetrics && !isFullGraph && (
          <div className="absolute bottom-4 right-4 z-10 bg-dark-panel/80 backdrop-blur border border-dark-border rounded-lg p-3 shadow-lg pointer-events-none">
            <div className="text-xs text-gray-400 mb-1 font-mono uppercase tracking-wider">Sample Metrics</div>
            <div className="flex gap-4">
              <div>
                <div className="text-lg font-semibold text-white">{sampleMetrics.num_nodes}</div>
                <div className="text-xs text-gray-500">Nodes</div>
              </div>
              <div>
                <div className="text-lg font-semibold text-white">{sampleMetrics.num_edges}</div>
                <div className="text-xs text-gray-500">Edges</div>
              </div>
              <div>
                <div className="text-lg font-semibold text-brand-400">{sampleMetrics.sample_coverage_pct}%</div>
                <div className="text-xs text-gray-500">Coverage</div>
              </div>
              <div>
                <div className="text-lg font-semibold text-purple-400">{sampleMetrics.sampling_ms}ms</div>
                <div className="text-xs text-gray-500">Render Time</div>
              </div>
            </div>
          </div>
        )}

        {isLoading && (
          <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-dark-bg/50 backdrop-blur-sm">
            <Loader2 className="animate-spin text-brand-500 mb-4" size={40} />
            <p className="text-gray-300 font-medium">Computing graph layout...</p>
            <p className="text-gray-500 text-sm mt-2 max-w-md text-center">This may take a moment. igraph is calculating forces.</p>
          </div>
        )}

        {error && !isLoading && (
          <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-dark-bg/50">
            <div className="bg-red-500/10 border border-red-500/20 p-6 rounded-xl flex flex-col items-center gap-4 text-red-400 max-w-lg text-center">
              <AlertCircle size={32} className="shrink-0" />
              <p className="font-medium">{error}</p>
              <p className="text-sm text-red-400/70">Did you load a dataset in the Import Data tab first?</p>
            </div>
          </div>
        )}

        {/* Metric Result Panel */}
        {metricResult && (
          <div className="absolute top-4 left-4 z-20 w-80 bg-dark-panel/90 backdrop-blur-md border border-brand-500/30 rounded-xl shadow-2xl overflow-hidden animate-in fade-in slide-in-from-left-4">
            <div className="px-4 py-3 border-b border-dark-border flex items-center justify-between bg-dark-bg/50">
              <h3 className="font-medium text-white flex items-center gap-2">
                <Calculator size={16} className="text-brand-400" />
                {metricResult.metric}
              </h3>
              <button onClick={() => setMetricResult(null)} className="text-gray-500 hover:text-white transition-colors">
                <X size={16} />
              </button>
            </div>
            <div className="p-4 max-h-64 overflow-y-auto custom-scrollbar">
              <pre className="text-xs text-gray-300 font-mono whitespace-pre-wrap break-all">
                {formatResult(metricResult.result)}
              </pre>
            </div>
          </div>
        )}

        {graphData && dimensions.width > 0 && (
          <ForceGraph2D
            ref={fgRef}
            width={dimensions.width}
            height={dimensions.height}
            graphData={graphData}
            nodeId="id"
            nodeRelSize={4}
            nodeVal={(node: any) => Math.log(node.degree + 1) * 2} // Scale size logarithmically
            nodeColor={getNodeColor}
            nodeLabel={(node: any) => `Node ${node.id} (Degree: ${node.degree}, Community: ${node.community})`}
            linkColor={() => 'rgba(255,255,255,0.1)'}
            linkWidth={(link: any) => Math.sqrt(link.weight || 1) * 0.5}
            backgroundColor="transparent"
            d3AlphaDecay={0.05} // Let it settle quickly since layout is precomputed
            cooldownTicks={100}
          />
        )}
      </div>
    </div>
  );
}
