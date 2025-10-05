import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types for API requests and responses
export interface SearchRequest {
  query: string;
  mode: 'tfidf' | 'semantic' | 'hybrid' | 'hybrid-advanced';
  top_k: number;
  alpha?: number;
  tfidf_weight?: number;
  semantic_weight?: number;
  rerank?: boolean;
  include_snippets?: boolean;
  include_metadata?: boolean;
  log_enabled?: boolean;
}

export interface SearchResult {
  doc_id: string;
  title?: string;
  snippet: string;
  metadata?: {
    type?: string;
    publication_date?: string;
    [key: string]: any;
  };
  doc_type?: string;
  source_file?: string;
  base_doc_id?: string;
  score?: number;
}

export interface SearchResponse {
  query: string;
  mode: string;
  search_time: number;
  total_results: number;
  results: SearchResult[];
}

export interface SummarizeRequest {
  doc_id: string;
  max_length?: number;
}

export interface SummarizeResponse {
  doc_id: string;
  summary: string;
  title?: string;
  doc_type?: string;
}

export interface BatchSearchRequest {
  queries: string[];
  mode: 'tfidf' | 'semantic' | 'hybrid' | 'hybrid-advanced';
  top_k: number;
  alpha?: number;
  tfidf_weight?: number;
  semantic_weight?: number;
  rerank?: boolean;
  include_snippets?: boolean;
  include_metadata?: boolean;
  log_enabled?: boolean;
}

export interface BatchSearchResponse {
  total_queries: number;
  mode: string;
  results: SearchResponse[];
}

export interface CompareModesRequest {
  query: string;
  top_k: number;
  alpha?: number;
  tfidf_weight?: number;
  semantic_weight?: number;
  rerank?: boolean;
  include_snippets?: boolean;
  include_metadata?: boolean;
}

export interface CompareModesResponse {
  query: string;
  top_k: number;
  results: {
    tfidf: SearchResponse;
    semantic: SearchResponse;
    hybrid: SearchResponse;
    'hybrid-advanced': SearchResponse;
  };
}

export interface LogAnalysisResponse {
  log_file: string;
  total_queries: number;
  unique_queries: number;
  mode_usage: Record<string, number>;
  average_score: number;
  most_common_queries: Array<{
    query: string;
    count: number;
  }>;
}

export interface HealthResponse {
  status: string;
  message: string;
  version: string;
}

export interface DraftRequest {
  description: string;
  model?: string;
  template_type?: string;
  max_length?: number;
}

export interface DraftResponse {
  draft: string;
  model: string;
  template_type: string;
  generation_time: number;
  cached: boolean;
  success: boolean;
  message: string;
}

export interface OllamaHealthResponse {
  status: string;
  message: string;
  available_models: Record<string, string>;
  default_model: string;
  error?: string;
}

export interface OllamaModelsResponse {
  available_models: Record<string, string>;
  model_info: Record<string, any>;
  total_models: number;
}

// API functions
export const searchAPI = {
  // Basic search
  search: async (request: SearchRequest): Promise<SearchResponse> => {
    const response = await api.post('/api/v1/search', request);
    return response.data;
  },

  // Summarize a document
  summarize: async (request: SummarizeRequest): Promise<SummarizeResponse> => {
    const response = await api.post('/api/v1/summarize', request);
    return response.data;
  },

  // Batch search
  batchSearch: async (request: BatchSearchRequest): Promise<BatchSearchResponse> => {
    const response = await api.post('/api/v1/batch_search', request);
    return response.data;
  },

  // Compare modes
  compareModes: async (request: CompareModesRequest): Promise<CompareModesResponse> => {
    const response = await api.post('/api/v1/compare_modes', request);
    return response.data;
  },

  // Analyze logs
  analyzeLogs: async (logFile?: string): Promise<LogAnalysisResponse> => {
    const params = logFile ? { log_file: logFile } : {};
    const response = await api.get('/api/v1/logs/analyze', { params });
    return response.data;
  },

  // Health check
  health: async (): Promise<HealthResponse> => {
    const response = await api.get('/api/v1/health');
    return response.data;
  },
};

// Draft generation API
export const draftAPI = {
  // Generate patent draft
  generateDraft: async (request: DraftRequest): Promise<DraftResponse> => {
    const response = await api.post('/api/v1/generate_draft', request);
    return response.data;
  },

  // Check Ollama health
  ollamaHealth: async (): Promise<OllamaHealthResponse> => {
    const response = await api.get('/api/v1/ollama/health');
    return response.data;
  },

  // Get available models
  getModels: async (): Promise<OllamaModelsResponse> => {
    const response = await api.get('/api/v1/ollama/models');
    return response.data;
  },

  // Pull/download model
  pullModel: async (modelName: string): Promise<{success: boolean; message: string; model_name: string}> => {
    const response = await api.post(`/api/v1/ollama/pull_model?model_name=${modelName}`);
    return response.data;
  },
};

export default api;

