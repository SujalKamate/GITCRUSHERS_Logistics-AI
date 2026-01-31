/**
 * System health monitoring component showing AI performance metrics.
 */

'use client';

import React, { useState, useEffect } from 'react';
import { cn, formatDuration, formatPercentage } from '@/lib/utils';
import { Card } from '@/components/ui';
import { 
  Activity, 
  Zap, 
  Clock, 
  TrendingUp, 
  AlertTriangle,
  CheckCircle,
  Server,
  Cpu
} from 'lucide-react';

interface SystemHealthProps {
  className?: string;
}

interface HealthMetrics {
  uptime: number; // seconds
  cyclesPerMinute: number;
  averageCycleTime: number; // milliseconds
  successRate: number; // percentage
  activeIssues: number;
  resolvedIssues: number;
  systemLoad: number; // percentage
  memoryUsage: number; // percentage
  lastUpdate: string;
}

const SystemHealth: React.FC<SystemHealthProps> = ({ className }) => {
  const [metrics, setMetrics] = useState<HealthMetrics>({
    uptime: 3600 * 24 * 2, // 2 days
    cyclesPerMinute: 12,
    averageCycleTime: 2500, // 2.5 seconds
    successRate: 96.5,
    activeIssues: 2,
    resolvedIssues: 47,
    systemLoad: 34,
    memoryUsage: 67,
    lastUpdate: new Date().toISOString(),
  });

  // Simulate real-time metrics updates
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => ({
        ...prev,
        uptime: prev.uptime + 5,
        cyclesPerMinute: 10 + Math.random() * 6, // 10-16 cycles/min
        averageCycleTime: 2000 + Math.random() * 1000, // 2-3 seconds
        successRate: 94 + Math.random() * 4, // 94-98%
        systemLoad: 20 + Math.random() * 40, // 20-60%
        memoryUsage: 50 + Math.random() * 30, // 50-80%
        lastUpdate: new Date().toISOString(),
      }));
    }, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, []);

  const getHealthStatus = () => {
    if (metrics.successRate > 95 && metrics.systemLoad < 70) {
      return { status: 'healthy', color: 'text-success-600', bgColor: 'bg-success-100' };
    } else if (metrics.successRate > 90 && metrics.systemLoad < 85) {
      return { status: 'warning', color: 'text-warning-600', bgColor: 'bg-warning-100' };
    } else {
      return { status: 'critical', color: 'text-danger-600', bgColor: 'bg-danger-100' };
    }
  };

  const healthStatus = getHealthStatus();

  const MetricCard: React.FC<{
    icon: React.ComponentType<any>;
    title: string;
    value: string | number;
    subtitle?: string;
    trend?: 'up' | 'down' | 'stable';
    color?: string;
  }> = ({ icon: Icon, title, value, subtitle, trend, color = 'text-gray-600' }) => (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-2">
        <Icon className={cn('w-5 h-5', color)} />
        {trend && (
          <div className={cn(
            'flex items-center text-xs',
            trend === 'up' ? 'text-success-600' : 
            trend === 'down' ? 'text-danger-600' : 'text-gray-500'
          )}>
            <TrendingUp className={cn(
              'w-3 h-3 mr-1',
              trend === 'down' && 'rotate-180'
            )} />
            {trend}
          </div>
        )}
      </div>
      <div className="text-2xl font-bold text-gray-900 mb-1">
        {value}
      </div>
      <div className="text-sm text-gray-600">{title}</div>
      {subtitle && (
        <div className="text-xs text-gray-500 mt-1">{subtitle}</div>
      )}
    </div>
  );

  return (
    <div className={className}>
      <Card>
        <Card.Header
          title="System Health"
          subtitle="AI performance and system metrics"
          action={
            <div className="flex items-center space-x-2">
              <div className={cn('p-2 rounded-lg', healthStatus.bgColor)}>
                {healthStatus.status === 'healthy' ? (
                  <CheckCircle className={cn('w-4 h-4', healthStatus.color)} />
                ) : (
                  <AlertTriangle className={cn('w-4 h-4', healthStatus.color)} />
                )}
              </div>
              <div>
                <div className={cn('text-sm font-medium', healthStatus.color)}>
                  {healthStatus.status.charAt(0).toUpperCase() + healthStatus.status.slice(1)}
                </div>
                <div className="text-xs text-gray-500">
                  System Status
                </div>
              </div>
            </div>
          }
        />

        <Card.Content>
          <div className="space-y-6">
            {/* Key Metrics Grid */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <MetricCard
                icon={Clock}
                title="Uptime"
                value={formatDuration(metrics.uptime / 60)} // Convert to minutes
                color="text-primary-600"
                trend="stable"
              />
              
              <MetricCard
                icon={Zap}
                title="Cycles/Min"
                value={metrics.cyclesPerMinute.toFixed(1)}
                subtitle="Decision cycles"
                color="text-success-600"
                trend="up"
              />
              
              <MetricCard
                icon={Activity}
                title="Avg Cycle Time"
                value={`${(metrics.averageCycleTime / 1000).toFixed(1)}s`}
                subtitle="Per decision cycle"
                color="text-blue-600"
                trend="stable"
              />
              
              <MetricCard
                icon={CheckCircle}
                title="Success Rate"
                value={`${metrics.successRate.toFixed(1)}%`}
                subtitle="Decision accuracy"
                color="text-success-600"
                trend="up"
              />
            </div>

            {/* System Resources */}
            <div className="space-y-4">
              <h4 className="text-sm font-medium text-gray-700">System Resources</h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* CPU Usage */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Cpu className="w-4 h-4 text-gray-600" />
                      <span className="text-sm text-gray-700">CPU Load</span>
                    </div>
                    <span className="text-sm font-medium">
                      {formatPercentage(metrics.systemLoad)}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={cn(
                        'h-2 rounded-full transition-all duration-500',
                        metrics.systemLoad > 80 ? 'bg-danger-500' :
                        metrics.systemLoad > 60 ? 'bg-warning-500' : 'bg-success-500'
                      )}
                      style={{ width: `${metrics.systemLoad}%` }}
                    />
                  </div>
                </div>

                {/* Memory Usage */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Server className="w-4 h-4 text-gray-600" />
                      <span className="text-sm text-gray-700">Memory</span>
                    </div>
                    <span className="text-sm font-medium">
                      {formatPercentage(metrics.memoryUsage)}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={cn(
                        'h-2 rounded-full transition-all duration-500',
                        metrics.memoryUsage > 85 ? 'bg-danger-500' :
                        metrics.memoryUsage > 70 ? 'bg-warning-500' : 'bg-primary-500'
                      )}
                      style={{ width: `${metrics.memoryUsage}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Issues Summary */}
            <div className="space-y-4">
              <h4 className="text-sm font-medium text-gray-700">Issue Management</h4>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center justify-between p-3 bg-warning-50 rounded-lg border border-warning-200">
                  <div className="flex items-center space-x-2">
                    <AlertTriangle className="w-4 h-4 text-warning-600" />
                    <span className="text-sm text-warning-700">Active Issues</span>
                  </div>
                  <span className="text-lg font-bold text-warning-700">
                    {metrics.activeIssues}
                  </span>
                </div>

                <div className="flex items-center justify-between p-3 bg-success-50 rounded-lg border border-success-200">
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="w-4 h-4 text-success-600" />
                    <span className="text-sm text-success-700">Resolved Today</span>
                  </div>
                  <span className="text-lg font-bold text-success-700">
                    {metrics.resolvedIssues}
                  </span>
                </div>
              </div>
            </div>

            {/* Last Update */}
            <div className="pt-4 border-t border-gray-200">
              <div className="flex items-center justify-between text-sm text-gray-500">
                <span>Last updated: {new Date(metrics.lastUpdate).toLocaleTimeString()}</span>
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse" />
                  <span>Live monitoring</span>
                </div>
              </div>
            </div>
          </div>
        </Card.Content>
      </Card>
    </div>
  );
};

export default SystemHealth;