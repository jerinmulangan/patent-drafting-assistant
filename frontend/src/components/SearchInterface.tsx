import React, { useState } from 'react';
import {
  Search,
  Loader2,
  Settings,
  BarChart3,
  Zap,
  FileText,
  Filter,
  RefreshCw,
  Download,
  Activity,
  Target,
  Layers,
  ShieldCheck,
} from 'lucide-react';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { Select } from './ui/Select';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/Card';
import { Alert } from './ui/Alert';
import { Badge } from './ui/Badge';
import { SearchResult } from '../services/api';
import SearchResults from './SearchResults';
import { searchAPI, SearchRequest } from '../services/api';

const SIGNAL_PILLS = ['Novelty Analysis', 'Technology Landscape', 'Filing Trends', 'Competitor Analysis'] as const;
type SignalPill = (typeof SIGNAL_PILLS)[number];

const KEYWORD_SIGNALS = [
  { label: 'quantum', score: 95, tag: 'Quantum Computing' },
  { label: 'encryption', score: 88, tag: 'Cryptography' },
  { label: 'entanglement', score: 82, tag: 'Quantum Physics' },
  { label: 'photon', score: 79, tag: 'Optics' },
  { label: 'key distribution', score: 76, tag: 'Security' },
  { label: 'protocol', score: 73, tag: 'Networking' },
  { label: 'secure', score: 71, tag: 'Security' },
  { label: 'transmission', score: 68, tag: 'Communications' },
  { label: 'device', score: 65, tag: 'Hardware' },
  { label: 'verification', score: 62, tag: 'Validation' },
] as const;

const DIFFERENTIATOR_COLUMNS = [
  {
    title: 'Key Differentiators',
    bullets: [
      'Novel error correction methodology',
      'Multi-wavelength implementation',
      'Enhanced quantum state verification',
    ],
  },
  {
    title: 'Potential Obstacles',
    bullets: [
      'High similarity to US20230123456',
      'Crowded quantum encryption space',
      'Recent competitor filings (Q1 2024)',
    ],
  },
  {
    title: 'Recommended Actions',
    bullets: [
      'Strengthen claims around error correction',
      'Add hardware implementation details',
      'Consider provisional filing soon',
    ],
  },
] as const;

const HIGHLIGHT_CARDS = [
  {
    title: 'Signal Velocity',
    value: '+64%',
    delta: 'vs last quarter',
    icon: Activity,
  },
  {
    title: 'Primary Focus',
    value: 'Quantum Security',
    delta: 'Dominant Cluster',
    icon: Target,
  },
  {
    title: 'Prior Art Density',
    value: '142 matches',
    delta: 'Moderate saturation',
    icon: Layers,
  },
  {
    title: 'Claim Coverage',
    value: 'Strong',
    delta: '+18 dependent claims',
    icon: ShieldCheck,
  },
] as const;

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
  const [activePill, setActivePill] = useState<SignalPill>(SIGNAL_PILLS[0]);

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
    <div className="page-padding space-y-8">
      {/* Hero */}
      <div className="rounded-3xl bg-gradient-to-br from-slate-900 via-slate-900/95 to-slate-800 p-8 text-white shadow-[0_25px_60px_rgba(2,6,23,0.35)]">
        <div className="flex flex-wrap items-center justify-between gap-6">
          <div className="space-y-3">
            <p className="text-xs uppercase tracking-[0.45em] text-white/60">Analytics Dashboard</p>
            <h1 className="text-4xl font-semibold">Analytics Overview</h1>
            <p className="text-sm text-white/70 max-w-2xl">
              Visualize your invention&apos;s position in the patent landscape with blended semantic, hybrid, and novelty
              analysis pipelines.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <Button variant="outline" className="bg-white/10 text-white hover:bg-white/20">
              <Filter className="mr-2 h-4 w-4" />
              Filter
            </Button>
            <Button variant="outline" className="bg-white/10 text-white hover:bg-white/20">
              <RefreshCw className="mr-2 h-4 w-4" />
              Refresh
            </Button>
            <Button variant="outline" className="bg-white text-slate-900 hover:bg-slate-50">
              <Download className="mr-2 h-4 w-4" />
              Export
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="space-y-8">
      {/* Quick stats */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {HIGHLIGHT_CARDS.map((card) => {
          const Icon = card.icon;
          return (
            <Card key={card.title}>
              <CardContent className="space-y-3 p-5">
                <div className="flex items-center justify-between text-xs uppercase tracking-[0.3em] text-slate-400">
                  <span>{card.title}</span>
                  <Icon className="h-4 w-4 text-slate-400" />
                </div>
                <p className="text-3xl font-semibold text-slate-900">{card.value}</p>
                <p className="text-sm text-emerald-500">{card.delta}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Metrics */}
      <div className="dashboard-grid">
        {[
          { label: 'Novelty Score', value: '87%', delta: '+5%' },
          { label: 'Similar Patents', value: '142', delta: '+12' },
          { label: 'Tech Fields', value: '8', delta: '+2' },
          { label: 'Citations', value: '23', delta: '+3' },
        ].map((metric) => (
          <Card key={metric.label} className="radial-card">
            <CardContent className="space-y-4 p-6">
              <p className="text-xs uppercase tracking-[0.35em] text-slate-400">{metric.label}</p>
              <p className="text-4xl font-semibold text-slate-900">{metric.value}</p>
              <p className="text-sm text-emerald-500">{metric.delta}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Pills */}
      <div className="flex flex-wrap gap-3">
        {SIGNAL_PILLS.map((pill) => (
          <button
            key={pill}
            onClick={() => setActivePill(pill)}
            className={`rounded-full px-5 py-2 text-sm font-medium transition-all ${
              activePill === pill ? 'bg-slate-900 text-white shadow-lg' : 'bg-white/80 text-slate-500'
            }`}
          >
            {pill}
          </button>
        ))}
      </div>

      {/* Top analysis cards */}
      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-xl">Semantic Uniqueness</CardTitle>
              <CardDescription>How your invention compares across key dimensions</CardDescription>
            </div>
            <Badge variant="secondary" className="uppercase tracking-wide">
              Live
            </Badge>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-8 pt-6">
            <div className="relative h-64 w-64">
              <svg viewBox="0 0 200 200" className="h-full w-full text-slate-200">
                <polygon points="100,20 180,70 150,180 50,180 20,70" fill="currentColor" opacity="0.2" />
                <polygon
                  points="100,40 165,80 140,165 60,165 35,80"
                  className="text-sky-400"
                  fill="currentColor"
                  opacity="0.4"
                />
                <polygon
                  points="100,60 145,90 130,150 70,150 50,90"
                  className="text-blue-500"
                  fill="currentColor"
                  opacity="0.7"
                />
              </svg>
            </div>
            <div className="flex-1 space-y-4">
              {[
                { label: 'Technical Novelty', value: 'High' },
                { label: 'Market Fit', value: 'Strong' },
                { label: 'Cost Efficiency', value: 'Moderate' },
                { label: 'Scalability', value: 'High' },
                { label: 'Implementation', value: 'In Progress' },
              ].map((item) => (
                <div key={item.label} className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3">
                  <p className="text-sm font-medium text-slate-500">{item.label}</p>
                  <p className="text-sm font-semibold text-slate-900">{item.value}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="space-y-4">
          <CardHeader className="pb-0">
            <CardTitle className="text-xl">Keyword Density Analysis</CardTitle>
            <CardDescription>Most significant terms vs. technology field</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 pt-4">
            {KEYWORD_SIGNALS.map((signal) => (
              <div key={signal.label} className="space-y-1">
                <div className="flex items-center justify-between text-xs text-slate-500">
                  <span className="uppercase tracking-wide">{signal.label}</span>
                  <span className="text-slate-400">{signal.tag}</span>
                </div>
                <div className="h-3 rounded-full bg-slate-100">
                  <div
                    className="h-3 rounded-full bg-gradient-to-r from-sky-400 to-emerald-400"
                    style={{ width: `${signal.score}%` }}
                  />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Differentiator columns */}
      <div className="grid gap-6 lg:grid-cols-3">
        {DIFFERENTIATOR_COLUMNS.map((column) => (
          <Card key={column.title}>
            <CardHeader className="pb-0">
              <CardTitle className="text-lg">{column.title}</CardTitle>
            </CardHeader>
            <CardContent className="pt-4">
              <ul className="space-y-3 text-sm text-slate-600">
                {column.bullets.map((bullet) => (
                  <li key={bullet} className="flex items-start gap-2">
                    <span className="mt-1 h-2 w-2 rounded-full bg-emerald-400" />
                    <span>{bullet}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        ))}
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

