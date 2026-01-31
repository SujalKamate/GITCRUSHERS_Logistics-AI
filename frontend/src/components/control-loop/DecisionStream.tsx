/**
 * Live decision stream showing AI decisions as they happen.
 */

'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { cn, formatRelativeTime } from '@/lib/utils';
import { Decision, ActionType } from '@/types';
import { Card, Button } from '@/components/ui';
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

const DecisionStream: React.FC<DecisionStreamProps> = ({
  decisions = [],
  maxItems = 10,
  autoScroll = true,
  className,
}) => {
  const [isLive, setIsLive] = useState(true);

  // Convert API decisions to stream items
  const streamItems: DecisionStreamItem[] = useMemo(() => {
    return decisions.slice(0, maxItems).map(decision => ({
      id: decision.id,
      type: 'decision' as const,
      timestamp: decision.decided_at?.toString() ?? new Date().toISOString(),
      title: getDecisionTitle(decision.action_type),
      description: decision.rationale ?? 'AI decision pending',
      status: decision.human_approved ? 'approved' : 'pending',
      confidence: decision.confidence,
      actionType: decision.action_type,
      truckId: decision.parameters?.truck_id,
      loadId: decision.parameters?.load_id,
      metadata: {
        reason: decision.parameters?.reason,
        score: decision.score ? `${Math.round(decision.score * 100)}%` : undefined
      }
    }));
  }, [decisions, maxItems]);

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
            {streamItems.length > 0 ? (
              streamItems.map((item, index) => {
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
                      {item.metadata && Object.keys(item.metadata).filter(k => item.metadata![k]).length > 0 && (
                        <div className="mt-2 pt-2 border-t border-gray-100">
                          <div className="flex flex-wrap gap-2">
                            {Object.entries(item.metadata)
                              .filter(([_, value]) => value)
                              .map(([key, value]) => (
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
              })
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Brain className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>No decisions yet. AI is monitoring...</p>
                <p className="text-sm mt-1">Start the control loop to see decisions</p>
              </div>
            )}
          </div>
        </Card.Content>
      </Card>
    </div>
  );
};

// Helper function to get decision title from action type
function getDecisionTitle(actionType?: ActionType): string {
  switch (actionType) {
    case ActionType.REROUTE:
      return 'Route Optimization';
    case ActionType.REASSIGN:
      return 'Load Reassignment';
    case ActionType.DISPATCH:
      return 'Dispatch Order';
    case ActionType.WAIT:
      return 'Hold Position';
    case ActionType.NOTIFY:
      return 'Notification Alert';
    case ActionType.ESCALATE:
      return 'Issue Escalation';
    default:
      return 'AI Decision';
  }
}

export default DecisionStream;
