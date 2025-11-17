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
export interface DraftV2Request {
  description: string;
  model?: 'llama3.2:1b' | 'llama3.2:3b' | 'mistral:7b' | 'codellama:7b';
  template_type?: 'utility' | 'software' | 'medical' | 'design';
  jurisdiction?: 'USPTO' | 'EPO' | 'WIPO-PCT';
  claim_bundle?: 'system' | 'method' | 'crm' | 'system+method' | 'method+crm' | 'all';
  independent_claims_per_type?: number;
  dependent_claims_per_independent?: number;
  spec_depth?: 'concise' | 'standard' | 'deep';
  embodiment_style?: 'narrow' | 'balanced' | 'broad';
  include_definitions?: boolean;
  include_alternatives?: boolean;
  include_figure_callouts?: boolean;
  include_glossary?: boolean;
  include_enablement_language?: boolean;
  include_best_mode?: boolean;
  include_markush_examples?: boolean;
  add_boilerplate_variations?: boolean;
  use_background_search?: boolean;
  search_mode?: 'tfidf' | 'semantic' | 'hybrid' | 'hybrid-advanced';
  search_top_k?: number;
  include_snippets?: boolean;
  include_metadata?: boolean;
  use_cache?: boolean;
  temperature?: number;
}

export interface DraftV2Response {
  success: boolean;
  message: string;
  model: string;
  template_type: string;
  jurisdiction: string;
  generation_time: number;
  cached: boolean;
  abstract: string;
  full_text_markdown: string;
  full_text_html: string;
}

export interface AdvancedDraftRequest {
  description: string;
  precision_model?: string;
  fluency_model?: string;
  use_ensemble?: boolean;
  use_scaffolding?: boolean;
  use_two_pass?: boolean;
  use_critique?: boolean;
  run_evaluation?: boolean;
}

export interface AdvancedDraftResponse {
  success: boolean;
  message: string;
  sections: Record<string, string>;
  glossary: Record<string, any>;
  outline?: string;
  critique_results?: Record<string, any>;
  evaluation_results?: Record<string, any>;
  generation_time: number;
  model_used: Record<string, string>;
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

export interface DraftWithSimilarityRequest {
  description: string;
  search_mode?: 'tfidf' | 'semantic' | 'hybrid' | 'hybrid-advanced';
  model?: string;
  template_type?: string;
  top_k?: number;
  include_snippets?: boolean;
  use_cache?: boolean;
}

export interface SimilarPatent {
  patent_id: string;
  title?: string;
  similarity_score: number;
  doc_type?: string;
  snippet?: string;
  source_file?: string;
}

export interface SectionSimilarity {
  section_name: string;
  section_text: string;
  similar_patents: SimilarPatent[];
  analysis_time: number;
  patent_count: number;
}

export interface DraftWithSimilarityResponse {
  draft: string;
  model: string;
  template_type: string;
  generation_time: number;
  cached: boolean;
  section_similarities: Record<string, SectionSimilarity>;
  total_analysis_time: number;
  success: boolean;
  message: string;
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
  generateDraftV2: async (request: DraftV2Request): Promise<DraftV2Response> => {
    const response = await api.post('/api/v1/generate_draft_v2', request);
    return response.data;
  },
  
  generateDraftAdvanced: async (request: AdvancedDraftRequest): Promise<AdvancedDraftResponse> => {
    const response = await api.post('/api/v1/generate_draft_advanced', request);
    return response.data;
  },

  generateDraftWithSimilarity: async (request: DraftWithSimilarityRequest): Promise<DraftWithSimilarityResponse> => {
    const response = await api.post('/api/v1/generate_draft_with_similarity', request);
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

