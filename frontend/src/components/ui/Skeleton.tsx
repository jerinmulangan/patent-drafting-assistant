import React from 'react';
import { cn } from '../../utils/cn';

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {}

const Skeleton = React.forwardRef<HTMLDivElement, SkeletonProps>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'animate-pulse rounded-md bg-gray-200 dark:bg-gray-800',
          className
        )}
        {...props}
      />
    );
  }
);
Skeleton.displayName = 'Skeleton';

export { Skeleton };
