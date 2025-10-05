import React, { useState } from 'react';
import { Search, Loader2, Settings, BarChart3, Zap, FileText } from 'lucide-react';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { Select } from './ui/Select';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/Card';
import { Alert } from './ui/Alert';
import { Badge } from './ui/Badge';
import { SearchResult } from '../services/api';
import SearchResults from './SearchResults';
import { searchAPI, SearchRequest } from '../services/api';

const SearchInterface: React.FC = () => {
  const [query, setQuery] = useState('');
  const [searchMode, setSearchMode] = useState<'tfidf' | 'semantic' | 'hybrid' | 'hybrid-advanced'>('semantic');
  const [topK, setTopK] = useState(5);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [alpha, setAlpha] = useState(0.5);
  const [tfidfWeight, setTfidfWeight] = useState(0.5);
  const [semanticWeight, setSemanticWeight] = useState(0.5);
  const [rerank, setRerank] = useState(true);
  const [includeSnippets, setIncludeSnippets] = useState(true);
  const [includeMetadata, setIncludeMetadata] = useState(true);
  const [logEnabled, setLogEnabled] = useState(false);
  const [searchTime, setSearchTime] = useState<number | null>(null);
  const [totalResults, setTotalResults] = useState<number | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setIsLoading(true);
    setError(null);
    setSearchTime(null);
    setTotalResults(null);

    try {
      const searchRequest: SearchRequest = {
        query: query.trim(),
        mode: searchMode,
        top_k: topK,
        alpha: searchMode === 'hybrid' ? alpha : undefined,
        tfidf_weight: searchMode === 'hybrid-advanced' ? tfidfWeight : undefined,
        semantic_weight: searchMode === 'hybrid-advanced' ? semanticWeight : undefined,
        rerank: rerank,
        include_snippets: includeSnippets,
        include_metadata: includeMetadata,
        log_enabled: logEnabled,
      };

      const response = await searchAPI.search(searchRequest);
      setResults(response.results || []);
      setSearchTime(response.search_time);
      setTotalResults(response.total_results);
    } catch (err) {
      setError('Failed to perform search. Please check your backend connection.');
      console.error('Search error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">
            Patent Search Engine
          </h1>
          <p className="mt-2 text-lg text-gray-600">
            Advanced AI-powered patent search with multiple algorithms
          </p>
        </div>

        {/* Search Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Search className="h-5 w-5" />
              Search Patents
            </CardTitle>
            <CardDescription>
              Enter your search query and select your preferred search mode
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Search Query */}
            <div className="space-y-2">
              <label htmlFor="query" className="text-sm font-medium text-gray-700">
                Search Query
              </label>
              <Input
                id="query"
                placeholder="e.g., neural network for medical imaging, blockchain authentication system..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                className="text-base"
              />
            </div>

            {/* Basic Options */}
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <div className="space-y-2">
                <label htmlFor="mode" className="text-sm font-medium text-gray-700">
                  Search Mode
                </label>
                <Select
                  id="mode"
                  value={searchMode}
                  onChange={(e) => setSearchMode(e.target.value as any)}
                >
                  <option value="tfidf">TF-IDF (Keyword-based)</option>
                  <option value="semantic">Semantic (AI-powered)</option>
                  <option value="hybrid">Hybrid (Balanced)</option>
                  <option value="hybrid-advanced">Hybrid Advanced (Custom)</option>
                </Select>
              </div>

              <div className="space-y-2">
                <label htmlFor="topk" className="text-sm font-medium text-gray-700">
                  Number of Results
                </label>
                <Input
                  id="topk"
                  type="number"
                  min={1}
                  max={100}
                  value={topK}
                  onChange={(e) => setTopK(Number(e.target.value) || 5)}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">
                  Options
                </label>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowAdvanced(!showAdvanced)}
                  >
                    <Settings className="mr-2 h-4 w-4" />
                    {showAdvanced ? 'Hide' : 'Show'} Advanced
                  </Button>
                </div>
              </div>
            </div>

            {/* Advanced Options */}
            {showAdvanced && (
              <div className="space-y-4 rounded-lg border border-gray-200 bg-gray-50 p-4">
                <h3 className="text-sm font-semibold text-gray-900">Advanced Options</h3>
                
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {/* Alpha parameter for hybrid mode */}
                  {searchMode === 'hybrid' && (
                    <div className="space-y-2">
                      <label htmlFor="alpha" className="text-sm font-medium text-gray-700">
                        Alpha (TF-IDF vs Semantic balance)
                      </label>
                      <Input
                        id="alpha"
                        type="number"
                        min={0}
                        max={1}
                        step={0.1}
                        value={alpha}
                        onChange={(e) => setAlpha(Number(e.target.value) || 0.5)}
                      />
                      <p className="text-xs text-gray-500">
                        0 = Pure Semantic, 1 = Pure TF-IDF
                      </p>
                    </div>
                  )}

                  {/* Custom weights for hybrid-advanced mode */}
                  {searchMode === 'hybrid-advanced' && (
                    <>
                      <div className="space-y-2">
                        <label htmlFor="tfidf-weight" className="text-sm font-medium text-gray-700">
                          TF-IDF Weight
                        </label>
                        <Input
                          id="tfidf-weight"
                          type="number"
                          min={0}
                          max={1}
                          step={0.1}
                          value={tfidfWeight}
                          onChange={(e) => setTfidfWeight(Number(e.target.value) || 0.5)}
                        />
                      </div>
                      <div className="space-y-2">
                        <label htmlFor="semantic-weight" className="text-sm font-medium text-gray-700">
                          Semantic Weight
                        </label>
                        <Input
                          id="semantic-weight"
                          type="number"
                          min={0}
                          max={1}
                          step={0.1}
                          value={semanticWeight}
                          onChange={(e) => setSemanticWeight(Number(e.target.value) || 0.5)}
                        />
                      </div>
                    </>
                  )}

                  {/* Boolean options */}
                  <div className="space-y-3">
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="rerank"
                        checked={rerank}
                        onChange={(e) => setRerank(e.target.checked)}
                        className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      />
                      <label htmlFor="rerank" className="text-sm font-medium text-gray-700">
                        Enable Re-ranking
                      </label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="include-snippets"
                        checked={includeSnippets}
                        onChange={(e) => setIncludeSnippets(e.target.checked)}
                        className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      />
                      <label htmlFor="include-snippets" className="text-sm font-medium text-gray-700">
                        Include Snippets
                      </label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="include-metadata"
                        checked={includeMetadata}
                        onChange={(e) => setIncludeMetadata(e.target.checked)}
                        className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      />
                      <label htmlFor="include-metadata" className="text-sm font-medium text-gray-700">
                        Include Metadata
                      </label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="log-enabled"
                        checked={logEnabled}
                        onChange={(e) => setLogEnabled(e.target.checked)}
                        className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      />
                      <label htmlFor="log-enabled" className="text-sm font-medium text-gray-700">
                        Enable Logging
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Search Button */}
            <div className="flex justify-center">
              <Button onClick={handleSearch} disabled={isLoading} size="lg" className="px-8">
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Searching...
                  </>
                ) : (
                  <>
                    <Search className="mr-2 h-5 w-5" />
                    Search Patents
                  </>
                )}
              </Button>
            </div>

            {/* Error Display */}
            {error && (
              <Alert variant="destructive">
                {error}
              </Alert>
            )}

            {/* Search Stats */}
            {(searchTime !== null || totalResults !== null) && (
              <div className="flex items-center justify-center gap-4 text-sm text-gray-600">
                {searchTime !== null && (
                  <div className="flex items-center gap-1">
                    <Zap className="h-4 w-4" />
                    <span>Search time: {searchTime.toFixed(3)}s</span>
                  </div>
                )}
                {totalResults !== null && (
                  <div className="flex items-center gap-1">
                    <BarChart3 className="h-4 w-4" />
                    <span>Total results: {totalResults}</span>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Search Mode Info */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Search Mode Information
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <div className="space-y-2">
                <Badge variant="outline">TF-IDF</Badge>
                <p className="text-sm text-gray-600">
                  Traditional keyword-based search using term frequency analysis
                </p>
              </div>
              <div className="space-y-2">
                <Badge variant="outline">Semantic</Badge>
                <p className="text-sm text-gray-600">
                  AI-powered search that understands meaning and context
                </p>
              </div>
              <div className="space-y-2">
                <Badge variant="outline">Hybrid</Badge>
                <p className="text-sm text-gray-600">
                  Balanced combination of TF-IDF and semantic search
                </p>
              </div>
              <div className="space-y-2">
                <Badge variant="outline">Hybrid Advanced</Badge>
                <p className="text-sm text-gray-600">
                  Custom-weighted combination with fine-tuned control
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Results */}
        {results.length > 0 && <SearchResults results={results} />}
      </div>
    </div>
  );
};

export default SearchInterface;

