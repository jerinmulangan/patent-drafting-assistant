import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import Navbar from './components/Navbar';
import SearchInterface from './components/SearchInterface';
import DraftAssistant from './components/DraftAssistant';
import CompareModes from './components/CompareModes';
import BatchSearch from './components/BatchSearch';
import LogAnalysis from './components/LogAnalysis';
import About from './components/About';
import './App.css';

function App() {
  return (
    <ThemeProvider defaultTheme="light" storageKey="patent-nlp-ui-theme">
      <Router>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
          <Navbar />
          <main className="min-h-[calc(100vh-4rem)]">
            <Routes>
              <Route path="/" element={<SearchInterface />} />
              <Route path="/compare" element={<CompareModes />} />
              <Route path="/batch" element={<BatchSearch />} />
              <Route path="/logs" element={<LogAnalysis />} />
              <Route path="/draft" element={<DraftAssistant />} />
              <Route path="/about" element={<About />} />
            </Routes>
          </main>
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;

