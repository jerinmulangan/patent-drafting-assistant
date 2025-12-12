import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  Search,
  FileText,
  BarChart3,
  TrendingUp,
  Settings,
  Layers,
  GitBranch,
  Bookmark,
  Info,
  Sparkles,
} from 'lucide-react';
import ThemeToggle from '../ThemeToggle';

type NavItem = {
  label: string;
  path: string;
  icon: React.ComponentType<{ className?: string }>;
  description?: string;
};

const primaryNav: NavItem[] = [
  { label: 'Search', path: '/', icon: Search, description: 'Discovery' },
  { label: 'Draft', path: '/draft', icon: FileText, description: 'Editor' },
  { label: 'Analytics', path: '/analytics', icon: BarChart3, description: 'Insights' },
  { label: 'Trends', path: '/trends', icon: TrendingUp, description: 'Signals' },
  { label: 'Settings', path: '/settings', icon: Settings, description: 'Control' },
];

const secondaryNav: NavItem[] = [
  { label: 'Compare Modes', path: '/compare', icon: Layers },
  { label: 'Batch Search', path: '/batch', icon: GitBranch },
  { label: 'Saved Drafts', path: '/saved-drafts', icon: Bookmark },
  { label: 'About', path: '/about', icon: Info },
];

const navLinkClass =
  'group flex items-center justify-between rounded-xl px-3 py-3 transition-all hover:bg-white/10';

const activeClass =
  'bg-white/10 text-white shadow-[0_10px_30px_rgba(6,27,61,0.35)] ring-1 ring-white/30';

const SidebarLink: React.FC<{ item: NavItem }> = ({ item }) => {
  const Icon = item.icon;
  return (
    <NavLink
      to={item.path}
      className={({ isActive }) =>
        [
          navLinkClass,
          isActive ? activeClass : 'text-slate-200 hover:text-white',
        ]
          .filter(Boolean)
          .join(' ')
      }
    >
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white/10 text-white">
          <Icon className="h-5 w-5" />
        </div>
        <div>
          <p className="text-sm font-semibold">{item.label}</p>
          {item.description && (
            <p className="text-xs text-white/70">{item.description}</p>
          )}
        </div>
      </div>
      <div className="text-xs uppercase tracking-wide text-white/60 opacity-0 transition-opacity group-hover:opacity-100">
        →
      </div>
    </NavLink>
  );
};

export const Sidebar: React.FC = () => {
  const location = useLocation();

  return (
    <aside className="app-sidebar relative hidden min-h-screen w-72 border-r border-white/5 bg-[#050c1f] text-white lg:flex">
      <div className="flex w-full flex-col px-6 py-6">
        <div className="mb-8 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/10">
            <Sparkles className="h-5 w-5 text-sky-300" />
          </div>
          <div>
            <p className="text-sm uppercase tracking-[0.3em] text-white/60">PatentAI</p>
            <p className="text-lg font-semibold text-white">Workbench</p>
          </div>
        </div>

        <div className="flex-1 space-y-8">
          <div className="space-y-2">
            <p className="text-xs uppercase tracking-[0.3em] text-white/50">
              Workspace
            </p>
            <div className="space-y-1">
              {primaryNav.map((item) => (
                <SidebarLink key={item.path} item={item} />
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <p className="text-xs uppercase tracking-[0.3em] text-white/40">
              Tools
            </p>
            <div className="space-y-1">
              {secondaryNav.map((item) => (
                <SidebarLink key={item.path} item={item} />
              ))}
            </div>
          </div>
        </div>

        <div className="mt-8 space-y-4">
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p className="text-xs uppercase tracking-[0.3em] text-white/40">Focus</p>
            <p className="mt-2 text-sm text-white/80">
              {location.pathname === '/draft'
                ? 'Drafting Session • Quantum Encryption'
                : 'Analytics Monitor • Active'}
            </p>
            <div className="mt-4 flex items-center justify-between text-xs text-white/60">
              <span>Status</span>
              <span className="flex items-center gap-1 text-sky-300">
                <span className="h-2 w-2 rounded-full bg-emerald-400" />
                Live
              </span>
            </div>
          </div>

          <div className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-white/40">Theme</p>
              <p className="text-sm text-white/80">Adaptive</p>
            </div>
            <ThemeToggle />
          </div>
        </div>
      </div>
    </aside>
  );
};

export const MobileNav: React.FC = () => {
  return (
    <nav className="fixed bottom-4 left-1/2 z-30 w-[92%] max-w-md -translate-x-1/2 rounded-3xl border border-white/50 bg-[#050c1f]/95 p-2 backdrop-blur-xl lg:hidden">
      <div className="grid grid-cols-4 gap-1">
        {primaryNav.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                [
                  'flex flex-col items-center rounded-2xl px-2 py-2 text-[11px] font-semibold uppercase tracking-wide transition-all',
                  isActive ? 'bg-white/10 text-white' : 'text-white/60',
                ].join(' ')
              }
            >
              <Icon className="mb-1 h-4 w-4" />
              {item.label}
            </NavLink>
          );
        })}
      </div>
    </nav>
  );
};

export default Sidebar;
