import axios, { AxiosError } from 'axios';

const API_URL = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ==========================================
// TYPES & INTERFACES
// ==========================================

// 1. Data Management Types
export interface LoadDataPayload {
  file_path: string; // Deprecated, replaced by File payload
}

export interface LoadDataResponse {
  message: string;
  columns: string[];
  rows: number;
}

export interface ColumnsResponse {
  columns: string[];
}

// 2. Exploration Types
export interface ColumnPayload {
  column: string;
  sample_size?: number | null;
}

export interface MetricsResponse {
  unique_values: number;
  missing_values: number;
  mean: number;
  median: number;
  variance: number;
  std_dev: number;
  min_max: [number, number];
}

// 3. Graph Visualization Types
export interface GraphNode {
  id: string;
  x: number;
  y: number;
  community: number;
  degree: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  weight: number;
}

export interface GraphLayoutResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
  metrics: Record<string, any>;
}

// ==========================================
// API SERVICES
// ==========================================

export const DataManagementAPI = {
  /**
   * Loads a dataset from a local file path.
   */
  loadData: async (file: File): Promise<LoadDataResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post<LoadDataResponse>('/api/data/load', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Retrieves the list of columns for the currently loaded dataset.
   */
  getColumns: async (): Promise<ColumnsResponse> => {
    const response = await apiClient.get<ColumnsResponse>('/api/data/columns');
    return response.data;
  },

  /**
   * Drops rows with null values from the currently loaded dataset.
   */
  dropNulls: async (): Promise<{ message?: string; rows?: number }> => {
    const response = await apiClient.post('/api/data/transform/drop-nulls');
    return response.data;
  },

  /**
   * Normalizes the numeric columns in the currently loaded dataset.
   */
  normalize: async (): Promise<{ message?: string }> => {
    const response = await apiClient.post('/api/data/transform/normalize');
    return response.data;
  }
};

export interface ColumnInfo {
  name: string;
  type: 'numeric' | 'categorical';
}

export interface ColumnsInfoResponse {
  columns: ColumnInfo[];
}

export const ExplorationAPI = {
  /**
   * Retrieves the list of numeric columns.
   */
  getNumericColumns: async (): Promise<string[] | ColumnsResponse> => {
    const response = await apiClient.get<string[] | ColumnsResponse>('/api/explore/numeric-columns');
    return response.data;
  },

  /**
   * Retrieves the list of all columns and their types.
   */
  getColumnsInfo: async (): Promise<ColumnInfo[]> => {
    const response = await apiClient.get<ColumnsInfoResponse>('/api/explore/columns-info');
    return response.data.columns;
  },

  /**
   * Calculates metrics for a specific column.
   */
  getMetrics: async (payload: ColumnPayload): Promise<MetricsResponse> => {
    const response = await apiClient.post<MetricsResponse>('/api/explore/metrics', payload);
    return response.data;
  },

  /**
   * Gets a summary for a column (e.g. for tabular display).
   */
  getSummary: async (payload: ColumnPayload): Promise<any[]> => {
    const response = await apiClient.post<any[]>('/api/explore/summary', payload);
    return response.data;
  },

  /**
   * Gets distribution data for a column.
   */
  getDistribution: async (payload: ColumnPayload): Promise<any[]> => {
    const response = await apiClient.post<any[]>('/api/explore/distribution', payload);
    return response.data;
  },

  /**
   * Gets correlation data related to a column.
   */
  getCorrelation: async (payload: ColumnPayload): Promise<any[]> => {
    const response = await apiClient.post<any[]>('/api/explore/correlation', payload);
    return response.data;
  }
};

// 4. Graph Sampling Types
export type SamplingStrategy = 'random' | 'degree_weighted' | 'snowball';

export interface SampleParams {
  n_edges?: number;          // default 500, range 10–20000
  strategy?: SamplingStrategy;
  seed?: number;
}

export interface SampleMetrics {
  num_nodes: number;
  num_edges: number;
  num_communities: number;
  total_nodes_in_dataset: number;
  total_edges_in_dataset: number;
  sample_coverage_pct: number;
  sampling_ms: number;
  strategy: SamplingStrategy;
  seed: number;
}

export interface GraphSampleResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
  metrics: SampleMetrics;
}

export const GraphVisualizationAPI = {
  /**
   * Retrieves the pre-calculated graph layout structure (full dataset).
   */
  getLayout: async (): Promise<GraphLayoutResponse> => {
    const response = await apiClient.get<GraphLayoutResponse>('/api/graph/layout');
    return response.data;
  },

  /**
   * Returns a fast sampled subgraph for progressive visualization.
   *
   * @param n_edges   Number of edges to include (10–20000, default 500)
   * @param strategy  'random' | 'degree_weighted' | 'snowball'
   * @param seed      Random seed for reproducibility (default 42)
   */
  getSample: async ({ n_edges = 500, strategy = 'degree_weighted', seed = 42 }: SampleParams = {}): Promise<GraphSampleResponse> => {
    const response = await apiClient.get<GraphSampleResponse>('/api/graph/sample', {
      params: { n_edges, strategy, seed },
    });
    return response.data;
  },

  /**
   * Calculates a specific metric for the network graph.
   */
  getMetric: async (metric_name: string): Promise<{ metric: string; result: any }> => {
    const response = await apiClient.post<{ metric: string; result: any }>('/api/graph/metric', { metric_name });
    return response.data;
  }
};

// 5. AI Insights API
export interface InsightPayload {
  question: string;
  include_graph_metrics?: boolean;
}

export interface InsightResponse {
  response: string;
  context_used: boolean;
}

export const AI_API = {
  getInsights: async (payload: InsightPayload): Promise<InsightResponse> => {
    const response = await apiClient.post<InsightResponse>('/api/ai/insights', payload);
    return response.data;
  }
};


// ==========================================
// UTILITIES
// ==========================================

/**
 * Utility function to handle Axios errors safely in the frontend components.
 */
export const handleApiError = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ message?: string; detail?: string }>;

    // Server responded with a status code outside of 2xx
    if (axiosError.response) {
      return axiosError.response.data?.detail ||
        axiosError.response.data?.message ||
        `Server Error: ${axiosError.response.status}`;
    }
    // Request was made but no response was received
    else if (axiosError.request) {
      return 'No response received from the backend server. Is it running?';
    }

    // Something happened in setting up the request that triggered an Error
    return axiosError.message;
  }

  return error instanceof Error ? error.message : 'An unexpected error occurred';
};
