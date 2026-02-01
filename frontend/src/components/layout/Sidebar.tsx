/**
 * Sidebar navigation component.
 */

'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { 
  LayoutDashboard, 
  Truck, 
  MapPin, 
  Package, 
  Brain, 
  BarChart3, 
  Settings,
  ChevronLeft,
  ChevronRight,
  FileText,
  type LucideIcon
} from 'lucide-react';
import { SidebarProps, SidebarItem } from '@/types';

const navigationItems: SidebarItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    href: '/',
    icon: LayoutDashboard,
  },
  {
    id: 'requests',
    label: 'Delivery Requests',
    href: '/requests',
    icon: FileText,
  },
  {
    id: 'fleet',
    label: 'Fleet Management',
    href: '/fleet',
    icon: Truck,
  },
  {
    id: 'routes',
    label: 'Routes & Maps',
    href: '/routes',
    icon: MapPin,
  },
  {
    id: 'loads',
    label: 'Load Management',
    href: '/loads',
    icon: Package,
  },
  {
    id: 'ai-control',
    label: 'AI Control Loop',
    href: '/ai-control',
    icon: Brain,
  },
  {
    id: 'analytics',
    label: 'Analytics',
    href: '/analytics',
    icon: BarChart3,
  },
  {
    id: 'settings',
    label: 'Settings',
    href: '/settings',
    icon: Settings,
  },
];

const Sidebar: React.FC<SidebarProps> = ({ 
  collapsed = false, 
  onToggle, 
  items: propItems,
  className 
}) => {
  const pathname = usePathname();

  // Use provided items or default navigation items
  const items = propItems || navigationItems;

  return (
    <div className={cn(
      'bg-white border-r border-gray-200 flex flex-col transition-all duration-300',
      collapsed ? 'w-16' : 'w-64',
      className
    )}>
      {/* Toggle Button */}
      <div className="flex items-center justify-end p-4 border-b border-gray-200">
        {onToggle && (
          <button
            onClick={onToggle}
            className="p-1 rounded-lg hover:bg-gray-100 transition-colors"
          >
            {collapsed ? (
              <ChevronRight className="h-4 w-4 text-gray-600" />
            ) : (
              <ChevronLeft className="h-4 w-4 text-gray-600" />
            )}
          </button>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {items.length === 0 && (
          <div className="text-sm text-gray-500 text-center py-4">
            No navigation items
          </div>
        )}
        {items.map((item: SidebarItem) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.id}
              href={item.href || '#'}
              className={cn(
                'flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary-100 text-primary-700'
                  : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
              )}
            >
              {Icon ? <Icon className="h-5 w-5 flex-shrink-0" /> : (
                <div className="h-5 w-5 flex-shrink-0 bg-gray-300 rounded"></div>
              )}
              {!collapsed && (
                <span className="ml-3 truncate">{item.label}</span>
              )}
              {!collapsed && item.badge && (
                <span className="ml-auto bg-primary-100 text-primary-600 text-xs px-2 py-0.5 rounded-full">
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      {!collapsed && (
        <div className="p-4 border-t border-gray-200">
          <div className="text-xs text-gray-500 text-center">
            Agentic AI Control System
            <br />
            v1.0.0
          </div>
        </div>
      )}
    </div>
  );
};

export default Sidebar;