/**
 * Reusable Card component for content containers.
 */

import React from 'react';
import { cn } from '@/lib/utils';
import { BaseComponentProps } from '@/types';

interface CardProps extends BaseComponentProps {
  padding?: 'none' | 'sm' | 'md' | 'lg';
  shadow?: 'none' | 'sm' | 'md' | 'lg';
  border?: boolean;
  hover?: boolean;
}

interface CardHeaderProps extends BaseComponentProps {
  title?: string;
  subtitle?: string;
  action?: React.ReactNode;
}

interface CardContentProps extends BaseComponentProps {}

interface CardFooterProps extends BaseComponentProps {}

const Card: React.FC<CardProps> = ({ 
  className, 
  children, 
  padding = 'md',
  shadow = 'sm',
  border = true,
  hover = false,
}) => {
  const paddings = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  const shadows = {
    none: '',
    sm: 'shadow-sm',
    md: 'shadow-md',
    lg: 'shadow-lg',
  };

  return (
    <div
      className={cn(
        'bg-white rounded-lg',
        paddings[padding],
        shadows[shadow],
        border && 'border border-gray-200',
        hover && 'hover:shadow-md transition-shadow duration-200',
        className
      )}
    >
      {children}
    </div>
  );
};

const CardHeader: React.FC<CardHeaderProps> = ({ 
  className, 
  children, 
  title, 
  subtitle, 
  action 
}) => {
  return (
    <div className={cn('flex items-center justify-between mb-4', className)}>
      <div className="flex-1">
        {title && (
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        )}
        {subtitle && (
          <p className="text-sm text-gray-600 mt-1">{subtitle}</p>
        )}
        {children}
      </div>
      {action && <div className="ml-4">{action}</div>}
    </div>
  );
};

const CardContent: React.FC<CardContentProps> = ({ className, children }) => {
  return (
    <div className={cn('', className)}>
      {children}
    </div>
  );
};

const CardFooter: React.FC<CardFooterProps> = ({ className, children }) => {
  return (
    <div className={cn('mt-4 pt-4 border-t border-gray-200', className)}>
      {children}
    </div>
  );
};

Card.Header = CardHeader;
Card.Content = CardContent;
Card.Footer = CardFooter;

export default Card;