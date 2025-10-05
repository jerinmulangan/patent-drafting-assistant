import React from 'react';
import { Scale, Search, FileText, BarChart3, Zap } from 'lucide-react';

const About: React.FC = () => {
  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold tracking-tight text-gray-900">
          About Patent NLP
        </h1>
        <p className="mt-2 text-lg text-gray-600">
          Advanced AI-powered patent search and analysis platform
        </p>
      </div>

      <div className="prose prose-lg max-w-none">
        <h2>Overview</h2>
        <p>
          Patent NLP is a comprehensive patent search and analysis platform that leverages 
          state-of-the-art natural language processing and machine learning techniques to help 
          researchers, inventors, and legal professionals discover and analyze patent documents 
          with unprecedented accuracy and efficiency.
        </p>

        <h2>Key Features</h2>
        <div className="grid gap-6 sm:grid-cols-2">
          <div className="flex items-start gap-3">
            <Search className="h-6 w-6 text-primary-600 mt-1" />
            <div>
              <h3 className="font-semibold">Multiple Search Modes</h3>
              <p className="text-sm text-gray-600">
                TF-IDF, Semantic, Hybrid, and Advanced Hybrid search algorithms
              </p>
            </div>
          </div>
          
          <div className="flex items-start gap-3">
            <Zap className="h-6 w-6 text-primary-600 mt-1" />
            <div>
              <h3 className="font-semibold">Intelligent Re-ranking</h3>
              <p className="text-sm text-gray-600">
                Keyword-based re-ranking for improved relevance
              </p>
            </div>
          </div>
          
          <div className="flex items-start gap-3">
            <FileText className="h-6 w-6 text-primary-600 mt-1" />
            <div>
              <h3 className="font-semibold">Smart Summarization</h3>
              <p className="text-sm text-gray-600">
                AI-powered patent document summarization
              </p>
            </div>
          </div>
          
          <div className="flex items-start gap-3">
            <BarChart3 className="h-6 w-6 text-primary-600 mt-1" />
            <div>
              <h3 className="font-semibold">Advanced Analytics</h3>
              <p className="text-sm text-gray-600">
                Query logging and usage analysis
              </p>
            </div>
          </div>
        </div>

        <h2>Search Modes</h2>
        <div className="space-y-4">
          <div>
            <h3>TF-IDF Search</h3>
            <p>
              Traditional keyword-based search using Term Frequency-Inverse Document Frequency 
              weighting to find documents with the most relevant keyword matches.
            </p>
          </div>
          
          <div>
            <h3>Semantic Search</h3>
            <p>
              AI-powered search that understands the meaning and context of your query, 
              finding patents that are conceptually related even if they don't contain 
              exact keyword matches.
            </p>
          </div>
          
          <div>
            <h3>Hybrid Search</h3>
            <p>
              Combines the precision of TF-IDF with the intelligence of semantic search 
              to provide the best of both worlds.
            </p>
          </div>
          
          <div>
            <h3>Advanced Hybrid Search</h3>
            <p>
              Sophisticated hybrid approach with customizable weighting parameters for 
              fine-tuned control over search behavior.
            </p>
          </div>
        </div>

        <h2>Technology Stack</h2>
        <ul>
          <li><strong>Backend:</strong> FastAPI, Python, scikit-learn, sentence-transformers</li>
          <li><strong>Frontend:</strong> React, TypeScript, Tailwind CSS</li>
          <li><strong>Search:</strong> FAISS, TF-IDF, BERT-based embeddings</li>
          <li><strong>UI Components:</strong> Lucide React icons</li>
        </ul>

        <h2>Getting Started</h2>
        <p>
          Simply enter your search query in the search interface, select your preferred 
          search mode, and adjust the parameters as needed. The system will return 
          relevant patent documents ranked by relevance, with options to view summaries 
          and detailed information.
        </p>

        <h2>API Documentation</h2>
        <p>
          For developers, comprehensive API documentation is available at 
          <code className="bg-gray-100 px-2 py-1 rounded text-sm">/docs</code> when running the backend server.
        </p>
      </div>
    </div>
  );
};

export default About;


