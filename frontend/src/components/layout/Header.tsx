/**
 * Main application header with navigation and status indicators.
 */

import React from 'react';
import { Truck, Bell, Settings, User } from 'lucide-react';
import { cn } from '@/lib/utils';
import Button from '@/components/ui/Button';

interface HeaderProps {
  className?: string;
}

const Header: React.FC<HeaderProps> = ({ className }) => {
  return (
    <header className={cn('bg-white shadow-sm border-b border-gray-200', className)}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Title */}
          <div className="flex items-center">
            <Truck className="h-8 w-8 text-primary-600" />
            <h1 className="ml-3 text-xl font-semibold text-gray-900">
              Logistics AI Dashboard
            </h1>
          </div>

          {/* Status Indicator */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-500">System Status:</span>
              <div className="flex items-center space-x-1">
                <div className="h-2 w-2 bg-success-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-success-600 font-medium">Active</span>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center space-x-2">
              <Button variant="ghost" size="sm">
                <Bell className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm">
                <Settings className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm">
                <User className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;