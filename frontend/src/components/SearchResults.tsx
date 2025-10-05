import React, { useState } from 'react';
import { ChevronDown, ChevronUp, FileText, Loader2, Calendar, Tag, Star, Clock } from 'lucide-react';
import { Button } from './ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { Badge } from './ui/Badge';
import { Skeleton } from './ui/Skeleton';
import { SearchResult } from '../services/api';
import { searchAPI } from '../services/api';

interface SearchResultsProps {
  results: SearchResult[];
}

const SearchResults: React.FC<SearchResultsProps> = ({ results }) => {
  const [expandedResults, setExpandedResults] = useState<Set<string>>(new Set());
  const [summaries, setSummaries] = useState<Record<string, string>>({});
  const [loadingSummaries, setLoadingSummaries] = useState<Set<string>>(new Set());

  const toggleExpand = (docId: string) => {
    const newExpanded = new Set(expandedResults);
    if (newExpanded.has(docId)) {
      newExpanded.delete(docId);
    } else {
      newExpanded.add(docId);
    }
    setExpandedResults(newExpanded);
  };

  const handleSummarize = async (docId: string) => {
    if (summaries[docId]) {
      toggleExpand(docId);
      return;
    }

    setLoadingSummaries(new Set(loadingSummaries).add(docId));

    try {
      const response = await searchAPI.summarize({ doc_id: docId });
      setSummaries({ ...summaries, [docId]: response.summary });
      setExpandedResults(new Set(expandedResults).add(docId));
    } catch (err) {
      console.error('Summarization error:', err);
      setSummaries({
        ...summaries,
        [docId]: 'Failed to generate summary. Please try again.',
      });
    } finally {
      const newLoading = new Set(loadingSummaries);
      newLoading.delete(docId);
      setLoadingSummaries(newLoading);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-gray-900">Search Results</h2>
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="flex items-center gap-1">
            <FileText className="h-3 w-3" />
            {results.length} results
          </Badge>
        </div>
      </div>

      <div className="space-y-4">
        {results.map((result, index) => (
          <Card key={result.doc_id} className="hover:shadow-md transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 space-y-2">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-xs">
                      #{index + 1}
                    </Badge>
                    {result.score !== undefined && (
                      <Badge variant="secondary" className="flex items-center gap-1">
                        <Star className="h-3 w-3" />
                        {(result.score * 100).toFixed(1)}%
                      </Badge>
                    )}
                  </div>
                  <CardTitle className="text-lg leading-relaxed text-gray-900">
                    {result.title || 'Untitled Document'}
                  </CardTitle>
                  <div className="flex items-center gap-3 text-sm text-gray-500">
                    <div className="flex items-center gap-1">
                      <FileText className="h-4 w-4" />
                      <span className="font-mono text-xs">{result.doc_id}</span>
                    </div>
                    {result.metadata?.type && (
                      <>
                        <span>•</span>
                        <Badge variant="outline" className="text-xs">
                          <Tag className="mr-1 h-3 w-3" />
                          {result.metadata.type}
                        </Badge>
                      </>
                    )}
                    {result.metadata?.publication_date && (
                      <>
                        <span>•</span>
                        <div className="flex items-center gap-1">
                          <Calendar className="h-4 w-4" />
                          <span>{result.metadata.publication_date}</span>
                        </div>
                      </>
                    )}
                    {result.doc_type && (
                      <>
                        <span>•</span>
                        <Badge variant="outline" className="text-xs">
                          <Tag className="mr-1 h-3 w-3" />
                          {result.doc_type}
                        </Badge>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="rounded-md bg-gray-50 p-4">
                <p className="text-sm leading-relaxed text-gray-700">{result.snippet}</p>
              </div>

              <div className="flex items-center justify-between">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleSummarize(result.doc_id)}
                  disabled={loadingSummaries.has(result.doc_id)}
                  className="flex items-center gap-2"
                >
                  {loadingSummaries.has(result.doc_id) ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Summarizing...
                    </>
                  ) : summaries[result.doc_id] ? (
                    <>
                      {expandedResults.has(result.doc_id) ? (
                        <ChevronUp className="h-4 w-4" />
                      ) : (
                        <ChevronDown className="h-4 w-4" />
                      )}
                      {expandedResults.has(result.doc_id) ? 'Hide' : 'Show'} Summary
                    </>
                  ) : (
                    <>
                      <FileText className="h-4 w-4" />
                      Generate Summary
                    </>
                  )}
                </Button>

                {summaries[result.doc_id] && (
                  <div className="text-xs text-gray-500 flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    <span>Summary available</span>
                  </div>
                )}
              </div>

              {summaries[result.doc_id] && expandedResults.has(result.doc_id) && (
                <div className="rounded-md border border-gray-200 bg-blue-50 p-4">
                  <h4 className="mb-2 text-sm font-semibold text-gray-900 flex items-center gap-2">
                    <FileText className="h-4 w-4" />
                    AI-Generated Summary
                  </h4>
                  <p className="text-sm leading-relaxed text-gray-700">
                    {summaries[result.doc_id]}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default SearchResults;

