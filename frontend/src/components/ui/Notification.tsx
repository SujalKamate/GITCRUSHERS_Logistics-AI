/**
 * Notification/Toast component for displaying alerts and messages.
 */

'use client';

import React, { useEffect } from 'react';
import { cn } from '@/lib/utils';
import { X, CheckCircle, AlertTriangle, AlertCircle, Info } from 'lucide-react';
import { NotificationProps } from '@/types';

const Notification: React.FC<NotificationProps> = ({
  id,
  type,
  title,
  message,
  duration = 5000,
  closable = true,
  onClose,
}) => {
  const icons = {
    success: CheckCircle,
    error: AlertCircle,
    warning: AlertTriangle,
    info: Info,
  };

  const colors = {
    success: 'bg-success-50 border-success-200 text-success-800',
    error: 'bg-danger-50 border-danger-200 text-danger-800',
    warning: 'bg-warning-50 border-warning-200 text-warning-800',
    info: 'bg-primary-50 border-primary-200 text-primary-800',
  };

  const iconColors = {
    success: 'text-success-500',
    error: 'text-danger-500',
    warning: 'text-warning-500',
    info: 'text-primary-500',
  };

  const Icon = icons[type];

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose?.();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  return (
    <div
      className={cn(
        'flex items-start p-4 border rounded-lg shadow-sm',
        colors[type]
      )}
    >
      <Icon className={cn('w-5 h-5 mt-0.5 mr-3 flex-shrink-0', iconColors[type])} />
      
      <div className="flex-1 min-w-0">
        <h4 className="text-sm font-medium">{title}</h4>
        {message && (
          <p className="mt-1 text-sm opacity-90">{message}</p>
        )}
      </div>

      {closable && (
        <button
          onClick={onClose}
          className="ml-3 flex-shrink-0 text-current opacity-60 hover:opacity-100 transition-opacity"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
};

export default Notification;