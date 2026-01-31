/**
 * Error message component with retry functionality.
 */

import React from 'react';
import { cn } from '@/lib/utils';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { ErrorProps } from '@/types';
import Button from './Button';

const ErrorMessage: React.FC<ErrorProps> = ({ 
  error, 
  retry, 
  showDetails = false, 
  className 
}) => {
  const errorMessage = error instanceof Error ? error.message : error;
  const errorDetails = error instanceof Error ? error.stack : undefined;

  return (
    <div className={cn('flex flex-col items-center justify-center p-6', className)}>
      <div className="flex items-center space-x-3 mb-4">
        <AlertTriangle className="w-6 h-6 text-danger-500" />
        <h3 className="text-lg font-medium text-gray-900">Something went wrong</h3>
      </div>
      
      <p className="text-gray-600 text-center mb-4 max-w-md">
        {errorMessage}
      </p>

      {showDetails && errorDetails && (
        <details className="mb-4 w-full max-w-2xl">
          <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700">
            Show error details
          </summary>
          <pre className="mt-2 p-3 bg-gray-100 rounded text-xs overflow-auto max-h-40">
            {errorDetails}
          </pre>
        </details>
      )}

      {retry && (
        <Button
          variant="outline"
          onClick={retry}
          icon={<RefreshCw className="w-4 h-4" />}
        >
          Try Again
        </Button>
      )}
    </div>
  );
};

export default ErrorMessage;