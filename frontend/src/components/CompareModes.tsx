import React, { useState } from 'react';
import { BarChart3, Loader2, Search, Zap, TrendingUp } from 'lucide-react';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/Card';
import { Alert } from './ui/Alert';
import { Badge } from './ui/Badge';
import { SearchResult, CompareModesRequest } from '../services/api';
import { searchAPI } from '../services/api';

const CompareModes: React.FC = () => {
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(5);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<any>(null);

  const handleCompare = async () => {
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const compareRequest: CompareModesRequest = {
        query: query.trim(),
        top_k: topK,
        include_snippets: true,
        include_metadata: true,
      };

      const response = await searchAPI.compareModes(compareRequest);
      setResults(response);
    } catch (err) {
      setError('Failed to compare search modes. Please check your backend connection.');
      console.error('Compare modes error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleCompare();
    }
  };

  const modes = ['tfidf', 'semantic', 'hybrid', 'hybrid-advanced'] as const;

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">
            Search Mode Comparison
          </h1>
          <p className="mt-2 text-lg text-gray-600">
            Compare different search algorithms side by side
          </p>
        </div>

        {/* Search Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Compare Search Modes
            </CardTitle>
            <CardDescription>
              Enter a query to see how different search algorithms perform
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <label htmlFor="query" className="text-sm font-medium text-gray-700">
                  Search Query
                </label>
                <Input
                  id="query"
                  placeholder="e.g., neural network for medical imaging"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="topk" className="text-sm font-medium text-gray-700">
                  Number of Results per Mode
                </label>
                <Input
                  id="topk"
                  type="number"
                  min={1}
                  max={20}
                  value={topK}
                  onChange={(e) => setTopK(Number(e.target.value) || 5)}
                />
              </div>
            </div>

            <div className="flex justify-center">
              <Button onClick={handleCompare} disabled={isLoading} size="lg" className="px-8">
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Comparing...
                  </>
                ) : (
                  <>
                    <BarChart3 className="mr-2 h-5 w-5" />
                    Compare Modes
                  </>
                )}
              </Button>
            </div>

            {error && (
              <Alert variant="destructive">
                {error}
              </Alert>
            )}
          </CardContent>
        </Card>

        {/* Results */}
        {results && (
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-semibold text-gray-900">Comparison Results</h2>
              <p className="mt-1 text-gray-600">Query: "{results.query}"</p>
            </div>

            {/* Performance Stats */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Performance Comparison
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                  {modes.map((mode) => {
                    const modeResult = results.results[mode];
                    return (
                      <div key={mode} className="space-y-2">
                        <Badge variant="outline" className="w-full justify-center">
                          {mode.toUpperCase()}
                        </Badge>
                        <div className="text-center space-y-1">
                          <div className="flex items-center justify-center gap-1 text-sm text-gray-600">
                            <Zap className="h-4 w-4" />
                            <span>{modeResult.search_time.toFixed(3)}s</span>
                          </div>
                          <div className="flex items-center justify-center gap-1 text-sm text-gray-600">
                            <Search className="h-4 w-4" />
                            <span>{modeResult.total_results} results</span>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>

            {/* Mode Results */}
            <div className="grid gap-6 lg:grid-cols-2">
              {modes.map((mode) => {
                const modeResult = results.results[mode];
                return (
                  <Card key={mode}>
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        <span className="flex items-center gap-2">
                          <BarChart3 className="h-5 w-5" />
                          {mode.toUpperCase()} Results
                        </span>
                        <div className="flex items-center gap-2 text-sm text-gray-500">
                          <Badge variant="secondary">
                            {modeResult.results.length} results
                          </Badge>
                          <span>{modeResult.search_time.toFixed(3)}s</span>
                        </div>
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {modeResult.results.map((result: SearchResult, index: number) => (
                        <div key={result.doc_id} className="border-l-4 border-primary-200 pl-4 py-2">
                          <div className="flex items-start justify-between gap-2">
                            <div className="flex-1">
                              <h4 className="text-sm font-semibold text-gray-900">
                                {result.title || 'Untitled Document'}
                              </h4>
                              <p className="text-xs text-gray-500 mt-1">
                                ID: {result.doc_id}
                                {result.metadata?.type && ` • ${result.metadata.type}`}
                                {result.doc_type && ` • ${result.doc_type}`}
                              </p>
                              <p className="text-sm text-gray-600 mt-2 line-clamp-2">
                                {result.snippet}
                              </p>
                            </div>
                            {result.score !== undefined && (
                              <Badge variant="secondary" className="text-xs">
                                {(result.score * 100).toFixed(1)}%
                              </Badge>
                            )}
                          </div>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CompareModes;
