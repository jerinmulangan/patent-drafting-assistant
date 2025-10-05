import React, { useState, useEffect } from 'react';
import { FileText, Loader2, Sparkles, Settings, Download, RefreshCw } from 'lucide-react';
import { Button } from './ui/Button';
import { Textarea } from './ui/Textarea';
import { Select } from './ui/Select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/Card';
import { Alert } from './ui/Alert';
import { Badge } from './ui/Badge';
import { draftAPI, DraftRequest, DraftResponse, OllamaHealthResponse } from '../services/api';

const DraftAssistant: React.FC = () => {
  const [description, setDescription] = useState('');
  const [draft, setDraft] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState('llama3.2:3b');
  const [templateType, setTemplateType] = useState('utility');
  const [ollamaStatus, setOllamaStatus] = useState<OllamaHealthResponse | null>(null);
  const [generationTime, setGenerationTime] = useState<number | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Check Ollama status on component mount
  useEffect(() => {
    checkOllamaStatus();
  }, []);

  const checkOllamaStatus = async () => {
    try {
      const status = await draftAPI.ollamaHealth();
      setOllamaStatus(status);
    } catch (err) {
      console.error('Failed to check Ollama status:', err);
      setOllamaStatus({
        status: 'unhealthy',
        message: 'Failed to connect to Ollama',
        available_models: {},
        default_model: 'llama3.2:3b',
        error: 'Connection failed'
      });
    }
  };

  const handleGenerate = async () => {
    if (!description.trim()) {
      setError('Please enter an invention description');
      return;
    }

    if (description.trim().length < 50) {
      setError('Description must be at least 50 characters long');
      return;
    }

    setIsLoading(true);
    setError(null);
    setGenerationTime(null);

    try {
      const request: DraftRequest = {
        description: description.trim(),
        model: selectedModel,
        template_type: templateType,
        max_length: 2000
      };

      const response: DraftResponse = await draftAPI.generateDraft(request);
      setDraft(response.draft);
      setGenerationTime(response.generation_time);
    } catch (err: any) {
      console.error('Draft generation error:', err);
      if (err.response?.status === 503) {
        setError('Ollama service is not available. Please install and start Ollama.');
      } else if (err.response?.status === 400) {
        setError(err.response.data.detail || 'Invalid request parameters');
      } else {
        setError('Failed to generate draft. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const downloadDraft = () => {
    if (!draft) return;
    
    const blob = new Blob([draft], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `patent_draft_${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const generatePlaceholderDraft = (description: string): string => {
    return `PATENT APPLICATION DRAFT SKELETON
[MVP Placeholder - To be integrated with Ollama backend]

TITLE OF INVENTION
[System/Method for ${description.slice(0, 50)}...]

FIELD OF THE INVENTION
The present invention relates to [technical field based on description].

BACKGROUND OF THE INVENTION
[Problem statement and prior art discussion]

SUMMARY OF THE INVENTION
The present invention provides a solution to the aforementioned problems by...

Key aspects include:
- [Feature 1 extracted from description]
- [Feature 2 extracted from description]
- [Feature 3 extracted from description]

BRIEF DESCRIPTION OF THE DRAWINGS
Figure 1 illustrates [system overview]
Figure 2 shows [detailed component view]
Figure 3 depicts [process flow]

DETAILED DESCRIPTION
[Detailed technical description based on invention disclosure]

CLAIMS
1. A system/method comprising:
   [Claims to be generated based on description]

---
Note: This is a placeholder draft skeleton. 
The full implementation will use Ollama to generate detailed, 
context-aware patent application drafts.`;
  };

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">
            Patent Draft Assistant
          </h1>
          <p className="mt-2 text-lg text-gray-600">
            Generate professional patent applications using AI
          </p>
        </div>

        {/* Ollama Status */}
        {ollamaStatus && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <RefreshCw className="h-5 w-5" />
                Ollama Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Badge variant={ollamaStatus.status === 'healthy' ? 'default' : 'destructive'}>
                    {ollamaStatus.status === 'healthy' ? 'Online' : 'Offline'}
                  </Badge>
                  <span className="text-sm text-gray-600">{ollamaStatus.message}</span>
                </div>
                <Button variant="outline" size="sm" onClick={checkOllamaStatus}>
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Refresh
                </Button>
              </div>
              {ollamaStatus.status === 'unhealthy' && (
                <Alert variant="destructive" className="mt-4">
                  <div>
                    <h4 className="font-semibold">Ollama Not Available</h4>
                    <p className="text-sm mt-1">
                      Please install and start Ollama to use the draft generation feature.
                      <br />
                      <a href="https://ollama.ai" target="_blank" rel="noopener noreferrer" 
                         className="underline hover:no-underline">
                        Download Ollama
                      </a>
                    </p>
                  </div>
                </Alert>
              )}
            </CardContent>
          </Card>
        )}

        {/* Draft Generation Form */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Invention Description
            </CardTitle>
            <CardDescription>
              Describe your invention in detail. Include the technical problem, solution, and key features.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <label htmlFor="description" className="text-sm font-medium text-gray-700">
                Description
              </label>
              <Textarea
                id="description"
                placeholder="Example: A neural network system for analyzing medical images that uses convolutional layers to detect anomalies in X-ray scans. The system preprocesses images, applies feature extraction, and classifies findings with 95% accuracy..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={8}
                className="resize-none"
              />
              <p className="text-xs text-gray-500">
                Minimum 50 characters ({description.length}/50)
              </p>
            </div>

            {/* Advanced Options */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-medium text-gray-700">Advanced Options</h3>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowAdvanced(!showAdvanced)}
                >
                  <Settings className="mr-2 h-4 w-4" />
                  {showAdvanced ? 'Hide' : 'Show'} Options
                </Button>
              </div>

              {showAdvanced && (
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <label htmlFor="model" className="text-sm font-medium text-gray-700">
                      AI Model
                    </label>
                    <Select
                      id="model"
                      value={selectedModel}
                      onChange={(e) => setSelectedModel(e.target.value)}
                    >
                      <option value="llama3.2:1b">Llama 3.2 1B (Ultra-fast)</option>
                      <option value="llama3.2:3b">Llama 3.2 3B (Balanced)</option>
                      <option value="mistral:7b">Mistral 7B (High Quality)</option>
                      <option value="codellama:7b">CodeLlama 7B (Technical)</option>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="template" className="text-sm font-medium text-gray-700">
                      Patent Type
                    </label>
                    <Select
                      id="template"
                      value={templateType}
                      onChange={(e) => setTemplateType(e.target.value)}
                    >
                      <option value="utility">Utility Patent</option>
                      <option value="software">Software Patent</option>
                      <option value="medical">Medical Device Patent</option>
                      <option value="design">Design Patent</option>
                    </Select>
                  </div>
                </div>
              )}
            </div>

            <div className="flex gap-2">
              <Button 
                onClick={handleGenerate} 
                disabled={isLoading || ollamaStatus?.status !== 'healthy'} 
                className="flex-1"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating Draft...
                  </>
                ) : (
                  <>
                    <Sparkles className="mr-2 h-4 w-4" />
                    Generate Patent Draft
                  </>
                )}
              </Button>
            </div>

            {error && (
              <Alert variant="destructive">
                {error}
              </Alert>
            )}

            {generationTime && (
              <div className="text-sm text-gray-600 flex items-center gap-2">
                <span>Generation time: {generationTime.toFixed(2)}s</span>
                <span>•</span>
                <span>Model: {selectedModel}</span>
                <span>•</span>
                <span>Type: {templateType}</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Generated Draft */}
        {draft && (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Sparkles className="h-5 w-5" />
                    Generated Patent Draft
                  </CardTitle>
                  <CardDescription>
                    AI-generated patent application draft. Review and refine as needed.
                  </CardDescription>
                </div>
                <Button onClick={downloadDraft} variant="outline" size="sm">
                  <Download className="mr-2 h-4 w-4" />
                  Download
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="rounded-md border border-gray-200 bg-gray-50 p-6">
                <div className="prose prose-sm max-w-none">
                  <div className="whitespace-pre-wrap font-mono text-sm leading-relaxed text-gray-800">
                    {draft}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default DraftAssistant;


