import React, { useState, useEffect } from 'react';
import { BarChart3, Loader2, TrendingUp, Clock, Search, FileText } from 'lucide-react';
import { Button } from './ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/Card';
import { Alert } from './ui/Alert';
import { Badge } from './ui/Badge';
import { LogAnalysisResponse } from '../services/api';
import { searchAPI } from '../services/api';

const LogAnalysis: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<LogAnalysisResponse | null>(null);

  const handleAnalyze = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await searchAPI.analyzeLogs();
      setAnalysis(response);
    } catch (err) {
      setError('Failed to analyze logs. Please check your backend connection.');
      console.error('Log analysis error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // Auto-load analysis on component mount
    handleAnalyze();
  }, []);

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">
            Query Log Analysis
          </h1>
          <p className="mt-2 text-lg text-gray-600">
            Insights into search patterns and system usage
          </p>
        </div>

        {/* Analysis Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Log Analysis Dashboard
            </CardTitle>
            <CardDescription>
              Analyze search query patterns and system performance
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex justify-center">
              <Button onClick={handleAnalyze} disabled={isLoading} size="lg" className="px-8">
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <BarChart3 className="mr-2 h-5 w-5" />
                    Refresh Analysis
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

        {/* Analysis Results */}
        {analysis && (
          <div className="space-y-6">
            {/* Overview Stats */}
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <Search className="h-8 w-8 text-primary-600" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Total Queries</p>
                      <p className="text-2xl font-bold text-gray-900">{analysis.total_queries}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <FileText className="h-8 w-8 text-primary-600" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Unique Queries</p>
                      <p className="text-2xl font-bold text-gray-900">{analysis.unique_queries}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <TrendingUp className="h-8 w-8 text-primary-600" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Avg Score</p>
                      <p className="text-2xl font-bold text-gray-900">
                        {(analysis.average_score * 100).toFixed(1)}%
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <Clock className="h-8 w-8 text-primary-600" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Log File</p>
                      <p className="text-sm font-bold text-gray-900 truncate">
                        {analysis.log_file.split('/').pop()}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Mode Usage */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Search Mode Usage
                </CardTitle>
                <CardDescription>
                  Distribution of search algorithms used
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Object.entries(analysis.mode_usage).map(([mode, count]) => {
                    const percentage = (count / analysis.total_queries) * 100;
                    return (
                      <div key={mode} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <Badge variant="outline" className="capitalize">
                            {mode.replace('-', ' ')}
                          </Badge>
                          <span className="text-sm text-gray-600">
                            {count} queries ({percentage.toFixed(1)}%)
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>

            {/* Most Common Queries */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Most Common Queries
                </CardTitle>
                <CardDescription>
                  Top queries by frequency
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {analysis.most_common_queries.map((query, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <Badge variant="secondary" className="text-xs">
                          #{index + 1}
                        </Badge>
                        <span className="text-sm font-medium text-gray-900">
                          "{query.query}"
                        </span>
                      </div>
                      <Badge variant="outline">
                        {query.count} times
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default LogAnalysis;

