import React from 'react';
import { cn } from '../../utils/cn';
import { AlertCircle, CheckCircle, Info, AlertTriangle } from 'lucide-react';

interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'destructive' | 'success' | 'warning';
}

const Alert = React.forwardRef<HTMLDivElement, AlertProps>(
  ({ className, variant = 'default', ...props }, ref) => {
    const variants = {
      default: 'bg-blue-50 text-blue-800 border-blue-200 dark:bg-blue-950 dark:text-blue-200 dark:border-blue-800',
      destructive: 'bg-red-50 text-red-800 border-red-200 dark:bg-red-950 dark:text-red-200 dark:border-red-800',
      success: 'bg-green-50 text-green-800 border-green-200 dark:bg-green-950 dark:text-green-200 dark:border-green-800',
      warning: 'bg-yellow-50 text-yellow-800 border-yellow-200 dark:bg-yellow-950 dark:text-yellow-200 dark:border-yellow-800',
    };

    const icons = {
      default: Info,
      destructive: AlertCircle,
      success: CheckCircle,
      warning: AlertTriangle,
    };

    const Icon = icons[variant];

    return (
      <div
        ref={ref}
        className={cn(
          'relative flex items-start gap-3 rounded-lg border p-4',
          variants[variant],
          className
        )}
        {...props}
      >
        <Icon className="h-5 w-5 shrink-0" />
        <div className="flex-1">{props.children}</div>
      </div>
    );
  }
);
Alert.displayName = 'Alert';

export { Alert };
