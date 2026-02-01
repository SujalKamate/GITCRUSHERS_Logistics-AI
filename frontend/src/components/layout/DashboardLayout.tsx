/**
 * Main dashboard layout component with header, sidebar, and content area.
 */

'use client';

import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import { DashboardLayoutProps } from '@/types';
import Header from './Header';
import Sidebar from './Sidebar';
import ConnectionTest from '../ui/ConnectionTest';

const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  children,
  sidebar,
  header,
  footer,
  sidebarCollapsed: controlledCollapsed,
  onSidebarToggle,
  className,
}) => {
  const [internalCollapsed, setInternalCollapsed] = useState(false);
  
  const collapsed = controlledCollapsed !== undefined ? controlledCollapsed : internalCollapsed;
  const handleToggle = onSidebarToggle || (() => setInternalCollapsed(!collapsed));

  return (
    <div className={cn('min-h-screen bg-gray-50 flex flex-col', className)}>
      {/* Header */}
      {header || <Header />}

      <div className="flex flex-1">
        {/* Sidebar */}
        {sidebar || (
          <Sidebar 
            collapsed={collapsed} 
            onToggle={handleToggle}
          />
        )}

        {/* Main Content */}
        <main className="flex-1 overflow-auto">
          <div className="p-6">
            {children}
          </div>
        </main>
      </div>

      {/* Footer */}
      {footer}
      
      {/* Connection Test (Development) */}
      {process.env.NODE_ENV === 'development' && <ConnectionTest />}
    </div>
  );
};

export default DashboardLayout;