import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { Sidebar, MobileNav } from './components/layout/Sidebar';
import { HeaderBar } from './components/layout/HeaderBar';
import SearchInterface from './components/SearchInterface';
import DraftAssistant from './components/DraftAssistant';
import SavedDrafts from './components/SavedDrafts';
import CompareModes from './components/CompareModes';
import BatchSearch from './components/BatchSearch';
import LogAnalysis from './components/LogAnalysis';
import About from './components/About';
import Trends from './components/Trends';
import Settings from './components/Settings';
import './App.css';

function App() {
  return (
    <ThemeProvider defaultTheme="light" storageKey="patent-nlp-ui-theme">
      <Router>
        <div className="app-shell">
          <Sidebar />
          <div className="app-main">
            <HeaderBar />
            <main className="flex-1 overflow-auto">
              <Routes>
                <Route path="/" element={<SearchInterface />} />
                <Route path="/draft" element={<DraftAssistant />} />
                <Route path="/analytics" element={<LogAnalysis />} />
                <Route path="/compare" element={<CompareModes />} />
                <Route path="/batch" element={<BatchSearch />} />
                <Route path="/trends" element={<Trends />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="/saved-drafts" element={<SavedDrafts />} />
                <Route path="/about" element={<About />} />
              </Routes>
            </main>
            <MobileNav />
          </div>
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;

