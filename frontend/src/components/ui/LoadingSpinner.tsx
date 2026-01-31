/**
 * Loading spinner component with different sizes and variants.
 */

import React from 'react';
import { cn } from '@/lib/utils';
import { Loader2 } from 'lucide-react';
import { LoadingProps } from '@/types';

const LoadingSpinner: React.FC<LoadingProps> = ({ 
  size = 'md', 
  text, 
  className 
}) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  return (
    <div className={cn('flex items-center justify-center', className)}>
      <div className="flex flex-col items-center space-y-2">
        <Loader2 className={cn('animate-spin text-primary-600', sizes[size])} />
        {text && (
          <p className="text-sm text-gray-600">{text}</p>
        )}
      </div>
    </div>
  );
};

export default LoadingSpinner;