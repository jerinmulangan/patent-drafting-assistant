import React, { useState, useEffect } from 'react';
import { FileText, Loader2, Sparkles, Settings, Download, RefreshCw, ChevronDown } from 'lucide-react';
import { Button } from './ui/Button';
import { Textarea } from './ui/Textarea';
import { Select } from './ui/Select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/Card';
import { Alert } from './ui/Alert';
import { Badge } from './ui/Badge';
import { draftAPI, searchAPI, DraftRequest, DraftResponse, OllamaHealthResponse, StreamProgressEvent, SaveDraftRequest, SavedDraft } from '../services/api';
import { DraftV2Request, DraftV2Response, AdvancedDraftRequest, AdvancedDraftResponse, AdvancedDraftWithSimilarityRequest, AdvancedDraftWithSimilarityResponse, DraftWithSimilarityRequest, DraftWithSimilarityResponse } from '../services/api';
import { downloadDraft } from '../utils/downloadDraft';

type GenerationMode = 'similarity' | 'advanced_similarity';

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
  const [generationMode, setGenerationMode] = useState<GenerationMode>('similarity');
  const [similarityResults, setSimilarityResults] = useState<DraftWithSimilarityResponse | null>(null);
  const [sectionProgress, setSectionProgress] = useState<Array<{ name: string; text: string }>>([])
  const [saveLoading, setSaveLoading] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);
  const [showDownloadMenu, setShowDownloadMenu] = useState(false);
  const [downloadLoading, setDownloadLoading] = useState(false);
  const hasSimilarity = !!(similarityResults && Object.keys(similarityResults.section_similarities || {}).length > 0);
  const hasSectionProgress = sectionProgress.length > 0;

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
    if (!description.trim()) { setError('Please enter an invention description'); return; }
    if (description.trim().length < 50) { setError('Description must be at least 50 characters long'); return; }

    setIsLoading(true);
    setError(null);
    setGenerationTime(null);
    setSimilarityResults(null);

    try {
      if (generationMode === 'similarity') {
        // --- Generate with Similarity (basic draft + prior art) ---
        const req: DraftWithSimilarityRequest = {
          description: description.trim(),
          model: selectedModel,
          template_type: templateType,
          search_mode: 'hybrid-advanced',  // Use hybrid-advanced for stricter matching
          top_k: 5,
          include_snippets: true,
          use_cache: true
        };
        const res: DraftWithSimilarityResponse = await draftAPI.generateDraftWithSimilarity(req);
        console.log('Similarity response:', res);
        console.log('Section similarities:', res.section_similarities);
        setDraft(res.draft);
        setGenerationTime(res.generation_time);
        setSimilarityResults(res);
      } else if (generationMode === 'advanced_similarity') {
        // --- Advanced 17-step system with similarity and streaming ---
        setSectionProgress([]);
        
        const req: AdvancedDraftWithSimilarityRequest = {
          description: description.trim(),
          precision_model: selectedModel,
          fluency_model: selectedModel === 'llama3.2:3b' ? 'mistral:7b' : 'llama3.2:3b',
          use_ensemble: true,
          use_scaffolding: true,
          use_two_pass: true,
          use_critique: true,
          run_evaluation: false,
          search_mode: 'hybrid-advanced',
          top_k: 5,
          include_snippets: true
        };

        try {
          await draftAPI.generateDraftAdvancedWithSimilarityStream(req, (event: StreamProgressEvent) => {
            if (event.type === 'section_complete') {
              setSectionProgress(prev => [...prev, { name: event.section_name, text: event.section_text }]);
            } else if (event.type === 'complete') {
              setGenerationTime(event.generation_time);
            } else if (event.type === 'error') {
              setError(event.message);
            }
          });

          // After streaming completes, fetch the full result
          const res: AdvancedDraftWithSimilarityResponse = await draftAPI.generateDraftAdvancedWithSimilarity(req);
          
          // Convert sections to markdown format for display
          const sections = res.sections || {};
          const markdownParts: string[] = [];
          
          // Order sections properly
          const sectionOrder = [
            'TITLE OF THE INVENTION',
            'CROSS-REFERENCE TO RELATED APPLICATIONS',
            'FIELD OF THE INVENTION',
            'BACKGROUND OF THE INVENTION',
            'BRIEF SUMMARY OF THE INVENTION',
            'BRIEF DESCRIPTION OF THE DRAWINGS',
            'DETAILED DESCRIPTION OF THE INVENTION',
            'CLAIMS',
            'ABSTRACT OF THE DISCLOSURE'
          ];
          
          for (const sectionName of sectionOrder) {
            if (sections[sectionName]) {
              markdownParts.push(`## ${sectionName}\n\n${sections[sectionName]}`);
            }
          }
          
          // Add any other sections
          for (const [sectionName, content] of Object.entries(sections)) {
            if (!sectionOrder.includes(sectionName)) {
              markdownParts.push(`## ${sectionName}\n\n${content}`);
            }
          }
          
          setDraft(markdownParts.join('\n\n'));
          setGenerationTime(res.generation_time);
          
          // Set similarity results from the response
          if (res.section_similarities && Object.keys(res.section_similarities).length > 0) {
            const result: DraftWithSimilarityResponse = {
              draft: markdownParts.join('\n\n'),
              model: selectedModel,
              template_type: 'utility',
              generation_time: res.generation_time,
              cached: false,
              section_similarities: res.section_similarities,
              total_analysis_time: res.total_analysis_time,
              success: res.success,
              message: res.message
            };
            setSimilarityResults(result);
          }
        } catch (streamErr: any) {
          console.error('Stream error:', streamErr);
          // Fallback to non-streaming version
          const res: AdvancedDraftWithSimilarityResponse = await draftAPI.generateDraftAdvancedWithSimilarity(req);
          
          const sections = res.sections || {};
          const markdownParts: string[] = [];
          
          const sectionOrder = [
            'TITLE OF THE INVENTION',
            'CROSS-REFERENCE TO RELATED APPLICATIONS',
            'FIELD OF THE INVENTION',
            'BACKGROUND OF THE INVENTION',
            'BRIEF SUMMARY OF THE INVENTION',
            'BRIEF DESCRIPTION OF THE DRAWINGS',
            'DETAILED DESCRIPTION OF THE INVENTION',
            'CLAIMS',
            'ABSTRACT OF THE DISCLOSURE'
          ];
          
          for (const sectionName of sectionOrder) {
            if (sections[sectionName]) {
              markdownParts.push(`## ${sectionName}\n\n${sections[sectionName]}`);
            }
          }
          
          for (const [sectionName, content] of Object.entries(sections)) {
            if (!sectionOrder.includes(sectionName)) {
              markdownParts.push(`## ${sectionName}\n\n${content}`);
            }
          }
          
          setDraft(markdownParts.join('\n\n'));
          setGenerationTime(res.generation_time);
          
          if (res.section_similarities && Object.keys(res.section_similarities).length > 0) {
            const result: DraftWithSimilarityResponse = {
              draft: markdownParts.join('\n\n'),
              model: selectedModel,
              template_type: 'utility',
              generation_time: res.generation_time,
              cached: false,
              section_similarities: res.section_similarities,
              total_analysis_time: res.total_analysis_time,
              success: res.success,
              message: res.message
            };
            setSimilarityResults(result);
          }
        }
      }
    } catch (err: any) {
      console.error('Draft generation error:', err);
      if (err.response?.status === 503) setError('Ollama service is not available. Please install and start Ollama.');
      else if (err.response?.status === 400) setError(err.response.data.detail || 'Invalid request parameters');
      else setError('Failed to generate draft. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };


  const handleDownload = async (format: 'txt' | 'pdf' | 'docx') => {
    if (!draft) return;
    setDownloadLoading(true);
    try {
      await downloadDraft(draft, format);
    } catch (err) {
      console.error('Download failed:', err);
      alert('Failed to download draft');
    } finally {
      setDownloadLoading(false);
      setShowDownloadMenu(false);
    }
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
          <p className="mt-2 text-sm text-gray-600">
            Not intended for legal advice or official use, For professional assistance, consult a patent attorney
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

            {/* Generation Mode Selection */}
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">
                  Generation Mode
                </label>
                <div className="grid gap-3 sm:grid-cols-4">
                  <button
                    type="button"
                    onClick={() => setGenerationMode('advanced_similarity')}
                    className={`sm:col-span-3 p-3 rounded-lg border-2 transition-all ${
                      generationMode === 'advanced_similarity'
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="text-sm font-medium text-gray-900">Full Draft Generation with Similarity</div>
                    <div className="text-xs text-gray-500 mt-1">Advanced drafting system + prior art search</div>
                  </button>
                  <button
                    type="button"
                    onClick={() => setGenerationMode('similarity')}
                    className={`sm:col-span-1 p-3 rounded-lg border-2 transition-all ${
                      generationMode === 'similarity'
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="text-sm font-medium text-gray-900">Preview Draft</div>
                    <div className="text-xs text-gray-500 mt-1">Basic draft generation + prior art search</div>
                  </button>
                </div>
              </div>

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

        {/* Responsive layout: left column (draft + progress) and right column (similarity) */}
        <div className="grid gap-4 md:grid-cols-4">
          <div className={`space-y-6 ${hasSimilarity ? 'md:col-span-3' : 'md:col-span-4'}`}>
            {/* Section Progress */}
            {hasSectionProgress && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Loader2 className="h-5 w-5 animate-spin" />
                    Section Generation Progress
                  </CardTitle>
                  <CardDescription>
                    Sections completed: {sectionProgress.length}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {sectionProgress.map((section, idx) => (
                      <div key={idx} className="rounded-lg border border-green-200 bg-green-50 p-4">
                        <h4 className="font-semibold text-green-900 mb-2">{section.name}</h4>
                        <p className="text-sm text-green-700 line-clamp-3">{section.text}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

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
                    <div className="flex items-center gap-2 relative">
                      <div className="relative">
                        <Button
                          onClick={() => setShowDownloadMenu(!showDownloadMenu)}
                          variant="outline"
                          size="sm"
                          disabled={downloadLoading}
                        >
                          <Download className="mr-2 h-4 w-4" />
                          Download
                          <ChevronDown className="ml-1 h-4 w-4" />
                        </Button>
                        {showDownloadMenu && (
                          <div className="absolute right-0 mt-1 w-32 bg-white border border-gray-200 rounded shadow-lg z-50">
                            <button
                              onClick={() => handleDownload('txt')}
                              disabled={downloadLoading}
                              className="block w-full text-left px-4 py-2 text-sm hover:bg-gray-100 disabled:opacity-50"
                            >
                              Text (.txt)
                            </button>
                            <button
                              onClick={() => handleDownload('docx')}
                              disabled={downloadLoading}
                              className="block w-full text-left px-4 py-2 text-sm hover:bg-gray-100 disabled:opacity-50"
                            >
                              Word (.docx)
                            </button>
                            <button
                              onClick={() => handleDownload('pdf')}
                              disabled={downloadLoading}
                              className="block w-full text-left px-4 py-2 text-sm hover:bg-gray-100 disabled:opacity-50"
                            >
                              PDF (.pdf)
                            </button>
                          </div>
                        )}
                      </div>
                        <Button
                          onClick={async () => {
                            if (!draft) return;
                            setSaveLoading(true);
                            setSaveMessage(null);
                            try {
                              const payload: SaveDraftRequest = {
                                title: draft.split('\n')[0].slice(0, 120),
                                content: draft,
                                model: selectedModel,
                                template_type: templateType
                              };
                              const saved: SavedDraft = await searchAPI.saveDraft(payload);
                              setSaveMessage('Saved draft');
                            } catch (e) {
                              console.error('Save draft failed', e);
                              setSaveMessage('Failed to save draft');
                            } finally {
                              setSaveLoading(false);
                              setTimeout(() => setSaveMessage(null), 3000);
                            }
                          }}
                          variant="secondary"
                          size="sm"
                          disabled={saveLoading}
                        >
                          {saveLoading ? 'Saving...' : 'Save Draft'}
                        </Button>
                      </div>
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

          {/* Right column: Similarity / Prior Art */}
          <div className="md:col-span-1 space-y-6">
            {hasSimilarity && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5" />
                    Prior Art Matches
                  </CardTitle>
                  <CardDescription>
                    Similar patents found for each section. Analysis time: {similarityResults!.total_analysis_time.toFixed(2)}s
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {Object.entries(similarityResults!.section_similarities).map(([sectionName, similarity]) => (
                      <div key={sectionName} className="rounded-lg border border-gray-200 p-4">
                        <h4 className="font-semibold text-gray-900 mb-2">{similarity.section_name || sectionName}</h4>
                        <p className="text-sm text-gray-600 mb-3">
                          Found {similarity.patent_count || (similarity.similar_patents?.length || 0)} similar patent{(similarity.patent_count || (similarity.similar_patents?.length || 0)) !== 1 ? 's' : ''} 
                          {' '}({similarity.analysis_time?.toFixed(2) || '0.00'}s)
                        </p>
                        {similarity.similar_patents && similarity.similar_patents.length > 0 ? (
                          <div className="space-y-2">
                            {similarity.similar_patents.map((patent, idx) => (
                              <PatentResultItem key={idx} patent={patent} />
                            ))}
                          </div>
                        ) : (
                          <div className="text-sm text-gray-500 italic">No similar patents found for this section.</div>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {similarityResults && (!similarityResults.section_similarities || Object.keys(similarityResults.section_similarities).length === 0) && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5" />
                    Prior Art Matches
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-sm text-gray-500">
                    No section similarities available. The draft may not have been parsed into sections, or similarity analysis may have failed.
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Component for displaying document-level patent results with expandable chunks
const PatentResultItem: React.FC<{ patent: any }> = ({ patent }) => {
  const [isExpanded, setIsExpanded] = React.useState(false);
  
  return (
    <div className="text-sm bg-gray-50 p-4 rounded border border-gray-100">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="font-medium text-gray-900">{patent.title || `Patent ${patent.patent_id}`}</div>
          <div className="text-xs text-gray-500 mt-1">ID: {patent.patent_id}</div>
          
          {/* Document-level scores */}
          <div className="mt-2 grid grid-cols-3 gap-2 text-xs">
            {patent.max_score !== undefined && (
              <div className="bg-white p-2 rounded border border-gray-200">
                <div className="text-gray-500">Max Score</div>
                <div className="font-semibold text-gray-900">{patent.max_score.toFixed(3)}</div>
              </div>
            )}
            {patent.avg_score !== undefined && (
              <div className="bg-white p-2 rounded border border-gray-200">
                <div className="text-gray-500">Avg Score</div>
                <div className="font-semibold text-gray-900">{patent.avg_score.toFixed(3)}</div>
              </div>
            )}
            {patent.similarity_score !== undefined && (
              <div className="bg-white p-2 rounded border border-gray-200">
                <div className="text-gray-500">Hybrid Score</div>
                <div className="font-semibold text-gray-900">{patent.similarity_score.toFixed(3)}</div>
              </div>
            )}
          </div>
          
          {/* Top snippet */}
          {patent.snippet && (
            <div className="text-xs text-gray-600 mt-2 line-clamp-2 bg-white p-2 rounded border border-gray-200">
              {patent.snippet}
            </div>
          )}
        </div>
      </div>
      
      {/* Chunk expansion button */}
      {patent.chunk_details && patent.chunk_details.length > 0 && (
        <div className="mt-3 border-t border-gray-200 pt-3">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-xs text-blue-600 hover:text-blue-700 font-medium"
          >
            {isExpanded ? '▼' : '▶'} Chunks ({patent.chunk_count || patent.chunk_details.length} matches)
          </button>
          
          {/* Expanded chunk list */}
          {isExpanded && (
            <div className="mt-2 space-y-2">
              {patent.chunk_details.map((chunk: any, idx: number) => (
                <div key={idx} className="bg-white border border-gray-200 rounded p-2 ml-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="text-xs font-mono text-gray-500">{chunk.chunk_id}</div>
                      <div className="inline-block mt-1 px-2 py-1 bg-blue-50 border border-blue-200 rounded text-xs text-blue-700">
                        Score: {chunk.chunk_score.toFixed(3)}
                      </div>
                    </div>
                  </div>
                  {chunk.chunk_snippet && (
                    <div className="text-xs text-gray-600 mt-2 line-clamp-2 bg-gray-50 p-2 rounded border border-gray-100">
                      {chunk.chunk_snippet}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
      
      {/* Fallback info */}
      {patent.doc_type && !patent.chunk_details && (
        <div className="text-xs text-gray-500 mt-2">Type: {patent.doc_type}</div>
      )}
    </div>
  );
};

export default DraftAssistant;
