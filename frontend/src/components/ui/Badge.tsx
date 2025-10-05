import React from 'react';
import { cn } from '../../utils/cn';

interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'secondary' | 'destructive' | 'outline';
}

const Badge = React.forwardRef<HTMLDivElement, BadgeProps>(
  ({ className, variant = 'default', ...props }, ref) => {
    const variants = {
      default: 'bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200',
      secondary: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200',
      destructive: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      outline: 'border border-gray-300 text-gray-800 dark:border-gray-700 dark:text-gray-200',
    };

    return (
      <div
        ref={ref}
        className={cn(
          'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors',
          variants[variant],
          className
        )}
        {...props}
      />
    );
  }
);

Badge.displayName = 'Badge';

export { Badge };

