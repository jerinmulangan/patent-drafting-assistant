import React, { useState } from 'react';
import { Upload, Loader2, FileText, BarChart3, Download } from 'lucide-react';
import { Button } from './ui/Button';
import { Textarea } from './ui/Textarea';
import { Select } from './ui/Select';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/Card';
import { Alert } from './ui/Alert';
import { Badge } from './ui/Badge';
import { BatchSearchRequest } from '../services/api';
import { searchAPI } from '../services/api';

const BatchSearch: React.FC = () => {
  const [queries, setQueries] = useState('');
  const [searchMode, setSearchMode] = useState<'tfidf' | 'semantic' | 'hybrid' | 'hybrid-advanced'>('semantic');
  const [topK, setTopK] = useState(5);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<any>(null);

  const handleBatchSearch = async () => {
    const queryList = queries
      .split('\n')
      .map(q => q.trim())
      .filter(q => q.length > 0);

    if (queryList.length === 0) {
      setError('Please enter at least one query');
      return;
    }

    if (queryList.length > 50) {
      setError('Maximum 50 queries allowed per batch');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const batchRequest: BatchSearchRequest = {
        queries: queryList,
        mode: searchMode,
        top_k: topK,
        include_snippets: true,
        include_metadata: true,
        log_enabled: false,
      };

      const response = await searchAPI.batchSearch(batchRequest);
      setResults(response);
    } catch (err) {
      setError('Failed to perform batch search. Please check your backend connection.');
      console.error('Batch search error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        setQueries(content);
      };
      reader.readAsText(file);
    }
  };

  const downloadResults = () => {
    if (!results) return;

    const dataStr = JSON.stringify(results, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `batch_search_results_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">
            Batch Search
          </h1>
          <p className="mt-2 text-lg text-gray-600">
            Search multiple queries at once for efficient analysis
          </p>
        </div>

        {/* Search Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5" />
              Batch Search Configuration
            </CardTitle>
            <CardDescription>
              Enter multiple queries (one per line) or upload a text file
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Query Input */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label htmlFor="queries" className="text-sm font-medium text-gray-700">
                  Search Queries (one per line)
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="file"
                    accept=".txt,.csv"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="file-upload"
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => document.getElementById('file-upload')?.click()}
                  >
                    <Upload className="mr-2 h-4 w-4" />
                    Upload File
                  </Button>
                </div>
              </div>
              <Textarea
                id="queries"
                placeholder="neural network for medical imaging&#10;blockchain authentication system&#10;machine learning optimization algorithm&#10;..."
                value={queries}
                onChange={(e) => setQueries(e.target.value)}
                rows={8}
                className="resize-none"
              />
              <p className="text-xs text-gray-500">
                Enter one query per line. Maximum 50 queries per batch.
              </p>
            </div>

            {/* Search Options */}
            <div className="grid gap-4 sm:grid-cols-2">
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
                  Results per Query
                </label>
                <input
                  id="topk"
                  type="number"
                  min={1}
                  max={20}
                  value={topK}
                  onChange={(e) => setTopK(Number(e.target.value) || 5)}
                  className="flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm ring-offset-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2"
                />
              </div>
            </div>

            {/* Search Button */}
            <div className="flex justify-center">
              <Button onClick={handleBatchSearch} disabled={isLoading} size="lg" className="px-8">
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Processing Batch...
                  </>
                ) : (
                  <>
                    <BarChart3 className="mr-2 h-5 w-5" />
                    Start Batch Search
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
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-semibold text-gray-900">Batch Search Results</h2>
                <p className="text-gray-600">
                  Processed {results.total_queries} queries using {results.mode} mode
                </p>
              </div>
              <Button onClick={downloadResults} variant="outline">
                <Download className="mr-2 h-4 w-4" />
                Download Results
              </Button>
            </div>

            {/* Summary Stats */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Batch Summary
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 sm:grid-cols-3">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary-600">{results.total_queries}</div>
                    <div className="text-sm text-gray-600">Total Queries</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary-600">
                      {results.results.reduce((sum: number, r: any) => sum + r.total_results, 0)}
                    </div>
                    <div className="text-sm text-gray-600">Total Results</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary-600">
                      {(results.results.reduce((sum: number, r: any) => sum + r.search_time, 0) / results.total_queries).toFixed(3)}s
                    </div>
                    <div className="text-sm text-gray-600">Avg Search Time</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Individual Results */}
            <div className="space-y-4">
              {results.results.map((queryResult: any, index: number) => (
                <Card key={index}>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span className="text-lg">Query {index + 1}</span>
                      <div className="flex items-center gap-2">
                        <Badge variant="secondary">
                          {queryResult.total_results} results
                        </Badge>
                        <Badge variant="outline">
                          {queryResult.search_time.toFixed(3)}s
                        </Badge>
                      </div>
                    </CardTitle>
                    <p className="text-sm text-gray-600 font-mono bg-gray-50 p-2 rounded">
                      "{queryResult.query}"
                    </p>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {queryResult.results.map((result: any, resultIndex: number) => (
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
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BatchSearch;
