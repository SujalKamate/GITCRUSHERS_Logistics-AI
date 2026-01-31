/**
 * Status badge component for displaying truck status, traffic levels, etc.
 */

import React from 'react';
import { cn, getStatusColors, snakeToTitle } from '@/lib/utils';
import { StatusBadgeProps } from '@/types';

const StatusBadge: React.FC<StatusBadgeProps> = ({ 
  status, 
  size = 'md', 
  variant = 'default',
  className,
  children 
}) => {
  const colors = getStatusColors(status);
  
  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-0.5 text-xs',
    lg: 'px-3 py-1 text-sm',
  };

  const variants = {
    default: `${colors.bg} ${colors.text}`,
    outline: `border ${colors.text} bg-transparent`,
    solid: `${colors.bg} ${colors.text}`,
  };

  return (
    <span
      className={cn(
        'inline-flex items-center font-medium rounded-full',
        sizes[size],
        variants[variant],
        className
      )}
    >
      {children || snakeToTitle(status)}
    </span>
  );
};

export default StatusBadge;