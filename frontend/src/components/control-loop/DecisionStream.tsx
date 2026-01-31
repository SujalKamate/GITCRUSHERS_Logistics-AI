/**
 * Live decision stream showing AI decisions as they happen.
 */

'use client';

import React, { useState, useEffect } from 'react';
import { cn, formatRelativeTime } from '@/lib/utils';
import { Decision, ActionType, Issue } from '@/types';
import { Card, StatusBadge, Button } from '@/components/ui';
import { 
  Brain, 
  CheckCircle, 
  XCircle, 
  Clock, 
  AlertTriangle,
  Route,
  Truck,
  Package,
  MoreHorizontal
} from 'lucide-react';

interface DecisionStreamProps {
  decisions?: Decision[];
  maxItems?: number;
  autoScroll?: boolean;
  className?: string;
}

interface DecisionStreamItem {
  id: string;
  type: 'decision' | 'issue' | 'action';
  timestamp: string;
  title: string;
  description: string;
  status: 'pending' | 'approved' | 'rejected' | 'executed' | 'failed';
  confidence?: number;
  actionType?: ActionType;
  truckId?: string;
  loadId?: string;
  metadata?: Record<string, any>;
}

// Mock decision stream data
const generateMockDecisions = (): DecisionStreamItem[] => [
  {
    id: 'DEC-001',
    type: 'decision',
    timestamp: new Date(Date.now() - 30000).toISOString(),
    title: 'Route Optimization',
    description: 'Reroute TRK-001 via Highway 95 to avoid traffic congestion',
    status: 'executed',
    confidence: 0.94,
    actionType: ActionType.REROUTE,
    truckId: 'TRK-001',
    metadata: { savings: '12 minutes', fuel: '1.5L' }
  },
  {
    id: 'ISS-001',
    type: 'issue',
    timestamp: new Date(Date.now() - 120000).toISOString(),
    title: 'Traffic Detected',
    description: 'Heavy traffic on Route 1 causing 15-minute delays',
    status: 'pending',
    truckId: 'TRK-001',
    metadata: { severity: 'medium', affectedTrucks: 3 }
  },
  {
    id: 'DEC-002',
    type: 'decision',
    timestamp: new Date(Date.now() - 180000).toISOString(),
    title: 'Load Reassignment',
    description: 'Reassign LOAD-456 from TRK-002 to TRK-005 for better efficiency',
    status: 'approved',
    confidence: 0.87,
    actionType: ActionType.REASSIGN,
    truckId: 'TRK-002',
    loadId: 'LOAD-456',
    metadata: { costSaving: '$45.00' }
  },
  {
    id: 'ACT-001',
    type: 'action',
    timestamp: new Date(Date.now() - 240000).toISOString(),
    title: 'Dispatch Completed',
    description: 'TRK-004 successfully dispatched to pickup location',
    status: 'executed',
    actionType: ActionType.DISPATCH,
    truckId: 'TRK-004',
    metadata: { eta: '14:30' }
  },
  {
    id: 'DEC-003',
    type: 'decision',
    timestamp: new Date(Date.now() - 300000).toISOString(),
    title: 'Maintenance Alert',
    description: 'Schedule maintenance for TRK-003 based on mileage threshold',
    status: 'pending',
    confidence: 0.76,
    actionType: ActionType.NOTIFY,
    truckId: 'TRK-003',
    metadata: { priority: 'low', dueDate: '2024-02-15' }
  }
];

const DecisionStream: React.FC<DecisionStreamProps> = ({
  decisions,
  maxItems = 10,
  autoScroll = true,
  className,
}) => {
  const [streamItems, setStreamItems] = useState<DecisionStreamItem[]>(generateMockDecisions());
  const [isLive, setIsLive] = useState(true);

  // Simulate new decisions coming in
  useEffect(() => {
    if (!isLive) return;

    const interval = setInterval(() => {
      const newDecision: DecisionStreamItem = {
        id: `DEC-${Date.now()}`,
        type: Math.random() > 0.7 ? 'issue' : 'decision',
        timestamp: new Date().toISOString(),
        title: [
          'Route Optimization',
          'Load Assignment',
          'Traffic Alert',
          'Fuel Warning',
          'Maintenance Due'
        ][Math.floor(Math.random() * 5)],
        description: [
          'AI detected optimal route change for improved efficiency',
          'Load reassignment recommended for better capacity utilization',
          'Traffic congestion detected on primary route',
          'Low fuel level detected, refueling station recommended',
          'Preventive maintenance scheduled based on usage patterns'
        ][Math.floor(Math.random() * 5)],
        status: ['pending', 'approved', 'executed'][Math.floor(Math.random() * 3)] as any,
        confidence: 0.7 + Math.random() * 0.3,
        actionType: Object.values(ActionType)[Math.floor(Math.random() * Object.values(ActionType).length)],
        truckId: `TRK-00${Math.floor(Math.random() * 5) + 1}`,
        metadata: { impact: 'medium' }
      };

      setStreamItems(prev => [newDecision, ...prev.slice(0, maxItems - 1)]);
    }, 8000); // New decision every 8 seconds

    return () => clearInterval(interval);
  }, [isLive, maxItems]);

  const getItemIcon = (item: DecisionStreamItem) => {
    switch (item.type) {
      case 'decision':
        return Brain;
      case 'issue':
        return AlertTriangle;
      case 'action':
        return CheckCircle;
      default:
        return MoreHorizontal;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-warning-100 text-warning-800';
      case 'approved':
        return 'bg-primary-100 text-primary-800';
      case 'executed':
        return 'bg-success-100 text-success-800';
      case 'rejected':
      case 'failed':
        return 'bg-danger-100 text-danger-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getActionIcon = (actionType?: ActionType) => {
    switch (actionType) {
      case ActionType.REROUTE:
        return Route;
      case ActionType.REASSIGN:
        return Package;
      case ActionType.DISPATCH:
        return Truck;
      default:
        return null;
    }
  };

  return (
    <div className={className}>
      <Card>
        <Card.Header
          title="Decision Stream"
          subtitle="Live AI decisions and actions"
          action={
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1">
                <div className={cn(
                  'w-2 h-2 rounded-full',
                  isLive ? 'bg-success-500 animate-pulse' : 'bg-gray-400'
                )} />
                <span className="text-sm text-gray-600">
                  {isLive ? 'Live' : 'Paused'}
                </span>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsLive(!isLive)}
              >
                {isLive ? 'Pause' : 'Resume'}
              </Button>
            </div>
          }
        />

        <Card.Content>
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {streamItems.map((item, index) => {
              const Icon = getItemIcon(item);
              const ActionIcon = getActionIcon(item.actionType);

              return (
                <div
                  key={item.id}
                  className={cn(
                    'flex items-start space-x-3 p-3 rounded-lg border transition-all',
                    index === 0 && isLive ? 'border-primary-200 bg-primary-50' : 'border-gray-200 bg-white'
                  )}
                >
                  {/* Icon */}
                  <div className={cn(
                    'p-2 rounded-lg flex-shrink-0',
                    item.type === 'decision' ? 'bg-purple-100 text-purple-600' :
                    item.type === 'issue' ? 'bg-warning-100 text-warning-600' :
                    'bg-success-100 text-success-600'
                  )}>
                    <Icon className="w-4 h-4" />
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="text-sm font-medium text-gray-900 truncate">
                        {item.title}
                      </h4>
                      <div className="flex items-center space-x-2 ml-2">
                        {item.confidence && (
                          <span className="text-xs text-gray-500">
                            {Math.round(item.confidence * 100)}%
                          </span>
                        )}
                        <span className={cn(
                          'px-2 py-0.5 text-xs font-medium rounded-full',
                          getStatusColor(item.status)
                        )}>
                          {item.status}
                        </span>
                      </div>
                    </div>

                    <p className="text-sm text-gray-600 mb-2">
                      {item.description}
                    </p>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3 text-xs text-gray-500">
                        <div className="flex items-center space-x-1">
                          <Clock className="w-3 h-3" />
                          <span>{formatRelativeTime(item.timestamp)}</span>
                        </div>
                        
                        {item.truckId && (
                          <div className="flex items-center space-x-1">
                            <Truck className="w-3 h-3" />
                            <span>{item.truckId}</span>
                          </div>
                        )}

                        {item.loadId && (
                          <div className="flex items-center space-x-1">
                            <Package className="w-3 h-3" />
                            <span>{item.loadId}</span>
                          </div>
                        )}
                      </div>

                      {ActionIcon && (
                        <div className="flex items-center space-x-1">
                          <ActionIcon className="w-3 h-3 text-gray-400" />
                          <span className="text-xs text-gray-500 capitalize">
                            {item.actionType?.replace('_', ' ')}
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Metadata */}
                    {item.metadata && Object.keys(item.metadata).length > 0 && (
                      <div className="mt-2 pt-2 border-t border-gray-100">
                        <div className="flex flex-wrap gap-2">
                          {Object.entries(item.metadata).map(([key, value]) => (
                            <span
                              key={key}
                              className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded"
                            >
                              {key}: {String(value)}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {streamItems.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <Brain className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>No decisions yet. AI is monitoring...</p>
            </div>
          )}
        </Card.Content>
      </Card>
    </div>
  );
};

export default DecisionStream;