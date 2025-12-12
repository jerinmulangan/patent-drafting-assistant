import React from 'react';
import { useLocation } from 'react-router-dom';
import {
  Bell,
  Download,
  Filter,
  RefreshCw,
  Search as SearchIcon,
  Repeat,
} from 'lucide-react';

const pageMeta: Record<
  string,
  { eyebrow: string; title: string; subtitle: string }
> = {
  '/': {
    eyebrow: 'Discovery Console',
    title: 'Patent Search',
    subtitle: 'Blend semantic and hybrid modes to surface the strongest prior art.',
  },
  '/draft': {
    eyebrow: 'Author Studio',
    title: 'Draft Editor',
    subtitle: 'Guide AI-assisted drafting with structured prompts and claim control.',
  },
  '/analytics': {
    eyebrow: 'Signals Hub',
    title: 'Analytics Dashboard',
    subtitle: 'Monitor novelty, similarity, and citation health across inventions.',
  },
  '/compare': {
    eyebrow: 'Diagnostics',
    title: 'Mode Comparison',
    subtitle: 'Inspect how each retrieval strategy ranks the landscape.',
  },
  '/batch': {
    eyebrow: 'Automation',
    title: 'Batch Search',
    subtitle: 'Process large query lists with consistent scoring pipelines.',
  },
  '/trends': {
    eyebrow: 'Landscape',
    title: 'Technology Trends',
    subtitle: 'Track emerging art units and signal velocity over time.',
  },
  '/settings': {
    eyebrow: 'Control Center',
    title: 'Workspace Settings',
    subtitle: 'Configure collaboration, notifications, and integration keys.',
  },
  '/saved-drafts': {
    eyebrow: 'Library',
    title: 'Saved Drafts',
    subtitle: 'Return to previously generated applications and refine them.',
  },
  '/about': {
    eyebrow: 'Briefing',
    title: 'About PatentAI',
    subtitle: 'Understand the stack powering real-time patent intelligence.',
  },
};

const HeaderActionButton: React.FC<
  React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'ghost' | 'solid' }
> = ({ children, className = '', variant = 'ghost', ...props }) => {
  const base =
    'inline-flex items-center gap-2 rounded-xl border px-4 py-2 text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-400/60';
  const styles =
    variant === 'solid'
      ? 'border-transparent bg-slate-900 text-white hover:bg-slate-800'
      : 'border-slate-200 bg-white/70 text-slate-600 hover:bg-white';
  return (
    <button className={`${base} ${styles} ${className}`} {...props}>
      {children}
    </button>
  );
};

export const HeaderBar: React.FC = () => {
  const location = useLocation();
  const meta = pageMeta[location.pathname] || {
    eyebrow: 'Workspace',
    title: 'PatentAI Studio',
    subtitle: 'Seamless prior-art research and assisted drafting.',
  };

  return (
    <header className="sticky top-0 z-20 border-b border-white/50 bg-white/70 backdrop-blur-lg">
      <div className="flex flex-wrap items-center justify-between gap-4 px-6 py-5">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.4em] text-slate-400">
            {meta.eyebrow}
          </p>
          <div className="mt-1 flex flex-wrap items-end gap-3">
            <h1 className="text-2xl font-semibold text-slate-900">{meta.title}</h1>
            <span className="rounded-full bg-slate-900/5 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-slate-500">
              Live
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-500">{meta.subtitle}</p>
        </div>

        <div className="flex flex-1 items-center justify-end gap-3">
          <div className="hidden max-w-sm flex-1 items-center rounded-xl border border-white/60 bg-white/70 px-3 py-2 text-sm text-slate-500 shadow-inner lg:flex">
            <SearchIcon className="mr-2 h-4 w-4 text-slate-400" />
            <input
              placeholder="Quick search across queries, drafts, and citations"
              className="w-full border-0 bg-transparent text-sm focus:outline-none"
            />
          </div>
          <div className="flex items-center gap-2">
            <HeaderActionButton>
              <Filter className="h-4 w-4" />
              Filter
            </HeaderActionButton>
            <HeaderActionButton>
              <RefreshCw className="h-4 w-4" />
              Refresh
            </HeaderActionButton>
            <HeaderActionButton variant="solid">
              <Download className="h-4 w-4" />
              Export
            </HeaderActionButton>
            <button className="rounded-full border border-white/60 bg-white/80 p-2 text-slate-500 shadow-sm hover:text-slate-900">
              <Bell className="h-4 w-4" />
            </button>
            <button className="rounded-full border border-white/60 bg-white/80 p-2 text-slate-500 shadow-sm hover:text-slate-900">
              <Repeat className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default HeaderBar;
