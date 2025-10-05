import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Scale, Search, FileText, Info, BarChart3, Upload, TrendingUp } from 'lucide-react';
import { cn } from '../utils/cn';
import ThemeToggle from './ThemeToggle';

const Navbar: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Search', icon: Search },
    { path: '/compare', label: 'Compare', icon: BarChart3 },
    { path: '/batch', label: 'Batch Search', icon: Upload },
    { path: '/logs', label: 'Analytics', icon: TrendingUp },
    { path: '/draft', label: 'Draft Assistant', icon: FileText },
    { path: '/about', label: 'About', icon: Info },
  ];

  return (
    <nav className="border-b border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-8">
            <Link to="/" className="flex items-center gap-2">
              <Scale className="h-6 w-6 text-primary-600" />
              <span className="text-lg font-semibold text-gray-900 dark:text-white">Patent NLP</span>
            </Link>
            <div className="hidden md:flex md:gap-6">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={cn(
                      'flex items-center gap-2 text-sm font-medium transition-colors hover:text-primary-600',
                      isActive ? 'text-primary-600' : 'text-gray-600 dark:text-gray-300'
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    {item.label}
                  </Link>
                );
              })}
            </div>
          </div>
          <div className="flex items-center gap-4">
            <ThemeToggle />
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

