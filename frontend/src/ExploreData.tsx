import { useState, useEffect, useMemo } from 'react';
import { TrendingUp, Loader2, AlertCircle, BarChart3, Calculator, AlignLeft } from 'lucide-react';
import { ExplorationAPI, handleApiError, type ColumnInfo } from './services/api';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';

type OperationType =
  | 'Resumen estadístico'
  | 'Promedio'
  | 'Mediana'
  | 'Varianza'
  | 'Desviación estándar'
  | 'Min y Max'
  | 'Cantidad de valores únicos'
  | 'Cantidad de valores faltantes'
  | 'Distribución'
  | 'Correlación';

const NUMERIC_OPERATIONS: OperationType[] = [
  'Resumen estadístico', 'Promedio', 'Mediana', 'Varianza', 'Desviación estándar',
  'Min y Max', 'Cantidad de valores únicos', 'Cantidad de valores faltantes',
  'Distribución', 'Correlación'
];

const CATEGORICAL_OPERATIONS: OperationType[] = [
  'Cantidad de valores únicos', 'Cantidad de valores faltantes', 'Distribución'
];

export function ExploreData() {
  const [columnsInfo, setColumnsInfo] = useState<ColumnInfo[]>([]);
  const [selectedColumn, setSelectedColumn] = useState<string>('');
  const [selectedOperation, setSelectedOperation] = useState<OperationType>('Resumen estadístico');
  const [sampleSize, setSampleSize] = useState<number | null>(10000);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Data states
  const [metrics, setMetrics] = useState<any>(null);
  const [distributionData, setDistributionData] = useState<any[]>([]);
  const [tableData, setTableData] = useState<any[]>([]);

  useEffect(() => {
    const fetchColumns = async () => {
      try {
        setIsLoading(true);
        const cols = await ExplorationAPI.getColumnsInfo();
        setColumnsInfo(cols);
        if (cols.length > 0) {
          setSelectedColumn(cols[0].name);
        }
      } catch (err) {
        setError(handleApiError(err));
      } finally {
        setIsLoading(false);
      }
    };
    fetchColumns();
  }, []);

  const activeColumnInfo = useMemo(() => {
    return columnsInfo.find(c => c.name === selectedColumn);
  }, [columnsInfo, selectedColumn]);

  const availableOperations = useMemo(() => {
    if (!activeColumnInfo) return [];
    return activeColumnInfo.type === 'numeric' ? NUMERIC_OPERATIONS : CATEGORICAL_OPERATIONS;
  }, [activeColumnInfo]);

  // Ensure selected operation is valid for the column type
  useEffect(() => {
    if (availableOperations.length > 0 && !availableOperations.includes(selectedOperation)) {
      setSelectedOperation(availableOperations[0]);
    }
  }, [availableOperations, selectedOperation]);

  useEffect(() => {
    if (!selectedColumn || !selectedOperation) return;

    const fetchData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        setMetrics(null);
        setDistributionData([]);
        setTableData([]);

        // Metrics includes scalar values
        if (['Promedio', 'Mediana', 'Varianza', 'Desviación estándar', 'Min y Max', 'Cantidad de valores únicos', 'Cantidad de valores faltantes'].includes(selectedOperation)) {
          const m = await ExplorationAPI.getMetrics({ column: selectedColumn });
          setMetrics(m);
        } else if (selectedOperation === 'Distribución') {
          const dist = await ExplorationAPI.getDistribution({ column: selectedColumn, sample_size: sampleSize });
          setDistributionData(dist);
        } else if (selectedOperation === 'Resumen estadístico') {
          const summary = await ExplorationAPI.getSummary({ column: selectedColumn });
          setTableData(summary);
        } else if (selectedOperation === 'Correlación') {
          const corr = await ExplorationAPI.getCorrelation({ column: selectedColumn });
          // correlation endpoint returns { columns: [], data: [] } 
          setTableData((corr as any).data || []);
        }

      } catch (err) {
        setError(handleApiError(err));
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [selectedColumn, selectedOperation, sampleSize]);

  // Transform distribution data for Recharts
  const chartData = useMemo(() => {
    if (!distributionData || distributionData.length === 0) return [];
    return distributionData.map(d => {
      const vals = Object.values(d);
      return {
        name: String(vals[0] ?? 'Null'),
        count: typeof vals[1] === 'number' ? vals[1] : 0
      };
    });
  }, [distributionData]);

  const renderResult = () => {
    if (isLoading) {
      return (
        <div className="flex flex-col items-center justify-center h-full text-brand-400">
          <Loader2 className="animate-spin mb-4" size={40} />
          <p>Processing operation...</p>
        </div>
      );
    }

    if (error) {
      return (
        <div className="flex flex-col items-center justify-center h-full">
          <div className="bg-red-500/10 border border-red-500/20 p-6 rounded-xl flex items-center gap-4 text-red-400 max-w-lg">
            <AlertCircle size={32} className="shrink-0" />
            <p>{error}</p>
          </div>
        </div>
      );
    }

    switch (selectedOperation) {
      case 'Promedio':
        return <ScalarResult title="Promedio (Mean)" value={metrics?.mean?.toFixed(4)} icon={<Calculator />} />;
      case 'Mediana':
        return <ScalarResult title="Mediana (Median)" value={metrics?.median?.toFixed(4)} icon={<Calculator />} />;
      case 'Varianza':
        return <ScalarResult title="Varianza (Variance)" value={metrics?.variance?.toFixed(4)} icon={<Calculator />} />;
      case 'Desviación estándar':
        return <ScalarResult title="Desviación Estándar (Std Dev)" value={metrics?.std_dev?.toFixed(4)} icon={<Calculator />} />;
      case 'Min y Max':
        return (
          <ScalarResult
            title="Mínimo y Máximo"
            value={metrics?.min_max ? `Min: ${metrics.min_max[0]} / Max: ${metrics.min_max[1]}` : 'N/A'}
            icon={<AlignLeft />}
          />
        );
      case 'Cantidad de valores únicos':
        return <ScalarResult title="Valores Únicos" value={metrics?.unique_values} icon={<AlignLeft />} />;
      case 'Cantidad de valores faltantes':
        return <ScalarResult title="Valores Faltantes (Nulls)" value={metrics?.missing_values} icon={<AlertCircle />} />;

      case 'Distribución':
        if (chartData.length === 0) return <div className="text-gray-400 text-center mt-20">No distribution data</div>;
        return (
          <div className="w-full h-full p-4 flex flex-col">
            <h3 className="text-lg font-medium text-white mb-6 flex items-center gap-2">
              <BarChart3 className="text-brand-400" /> Distribución de {selectedColumn}
            </h3>
            <div className="flex-1 min-h-[400px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
                  <XAxis
                    dataKey="name"
                    stroke="#888"
                    tick={{ fill: '#888' }}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis stroke="#888" tick={{ fill: '#888' }} />
                  <Tooltip
                    cursor={{ fill: 'rgba(255, 255, 255, 0.05)' }}
                    contentStyle={{ backgroundColor: '#1e1e2d', border: '1px solid #333', borderRadius: '8px' }}
                  />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {chartData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={index % 2 === 0 ? '#3b82f6' : '#60a5fa'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        );

      case 'Resumen estadístico':
      case 'Correlación':
        if (tableData.length === 0) return <div className="text-gray-400 text-center mt-20">No table data</div>;
        const keys = Object.keys(tableData[0]);
        return (
          <div className="w-full h-full p-4 overflow-auto custom-scrollbar">
            <h3 className="text-lg font-medium text-white mb-6 capitalize">{selectedOperation}</h3>
            <table className="w-full text-left border-collapse">
              <thead className="bg-dark-panel sticky top-0 shadow-sm border-b border-dark-border">
                <tr>
                  {keys.map(k => (
                    <th key={k} className="py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">{k}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-dark-border">
                {tableData.map((row, i) => (
                  <tr key={i} className="hover:bg-dark-hover/50 transition-colors">
                    {keys.map(k => (
                      <td key={k} className="py-3 px-4 text-sm text-gray-300">
                        {typeof row[k] === 'number' ? row[k].toFixed(4) : String(row[k])}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );

      default:
        return <div className="text-gray-400">Selecciona una operación.</div>;
    }
  };

  return (
    <div className="flex flex-col h-full animate-fade-in fade-in zoom-in duration-300">
      <header className="glass-panel mb-4 p-5 flex flex-col gap-4 relative z-20">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <TrendingUp className="text-brand-400" />
            Exploración de Datos (Estadística Descriptiva)
          </h1>
          <p className="text-sm text-gray-400 mt-1">Selecciona una columna y una operación para analizar la estructura de los datos.</p>
        </div>

        <div className="flex flex-wrap gap-4 bg-dark-bg/40 p-4 rounded-lg border border-dark-border/50">
          <div className="flex flex-col gap-1.5 flex-1 min-w-[200px]">
            <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Columna</label>
            <select
              value={selectedColumn}
              onChange={(e) => setSelectedColumn(e.target.value)}
              className="bg-dark-panel border border-dark-border text-sm text-white rounded-lg px-3 py-2 outline-none focus:border-brand-500 w-full"
            >
              {columnsInfo.map(c => (
                <option key={c.name} value={c.name}>
                  {c.name} ({c.type === 'numeric' ? '# Numérica' : 'A Categórica'})
                </option>
              ))}
            </select>
          </div>

          <div className="flex flex-col gap-1.5 flex-1 min-w-[200px]">
            <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Operación</label>
            <select
              value={selectedOperation}
              onChange={(e) => setSelectedOperation(e.target.value as OperationType)}
              className="bg-dark-panel border border-dark-border text-sm text-white rounded-lg px-3 py-2 outline-none focus:border-brand-500 w-full"
            >
              {availableOperations.map(op => (
                <option key={op} value={op}>{op}</option>
              ))}
            </select>
          </div>

          {selectedOperation === 'Distribución' && (
            <div className="flex flex-col gap-1.5 flex-1 min-w-[150px]">
              <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Muestra (Sample)</label>
              <select 
                value={sampleSize === null ? 'All' : sampleSize.toString()}
                onChange={(e) => setSampleSize(e.target.value === 'All' ? null : Number(e.target.value))}
                className="bg-dark-panel border border-dark-border text-sm text-white rounded-lg px-3 py-2 outline-none focus:border-brand-500 w-full"
              >
                <option value="1000">1,000</option>
                <option value="10000">10,000</option>
                <option value="50000">50,000</option>
                <option value="100000">100,000</option>
                <option value="All">Ver Toda la Data</option>
              </select>
            </div>
          )}
        </div>
      </header>

      <div className="flex-1 glass-panel overflow-hidden flex relative bg-dark-bg/30">
        <div className="absolute inset-0 pattern-grid opacity-5 pointer-events-none" style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)', backgroundSize: '32px 32px' }} />
        {renderResult()}
      </div>
    </div>
  );
}

// Helper component for rendering single scalar metrics beautifully
const ScalarResult = ({ title, value, icon }: { title: string, value: any, icon: React.ReactNode }) => (
  <div className="flex flex-col items-center justify-center w-full h-full">
    <div className="bg-dark-panel border border-brand-500/30 p-10 rounded-2xl shadow-2xl flex flex-col items-center gap-6 animate-in fade-in slide-in-from-bottom-4">
      <div className="p-4 bg-brand-500/20 text-brand-400 rounded-full">
        {icon}
      </div>
      <div className="text-center">
        <h3 className="text-gray-400 text-sm uppercase tracking-widest font-semibold mb-2">{title}</h3>
        <p className="text-5xl font-bold text-white tracking-tight">
          {value !== undefined && value !== null ? value : 'N/A'}
        </p>
      </div>
    </div>
  </div>
);
