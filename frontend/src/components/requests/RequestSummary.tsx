'use client';

import { Package, Clock, CheckCircle, XCircle, DollarSign, TrendingUp } from 'lucide-react';
import { Card, LoadingSpinner } from '@/components/ui';

interface RequestSummaryData {
  total_requests: number;
  pending_requests: number;
  processing_requests: number;
  assigned_requests: number;
  completed_requests: number;
  failed_requests: number;
  avg_processing_time_minutes?: number;
  total_estimated_revenue: number;
}

interface RequestSummaryProps {
  summary?: RequestSummaryData;
  loading: boolean;
}

export function RequestSummary({ summary, loading }: RequestSummaryProps) {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatTime = (minutes?: number) => {
    if (!minutes) return 'N/A';
    if (minutes < 60) return `${Math.round(minutes)}m`;
    return `${Math.round(minutes / 60)}h ${Math.round(minutes % 60)}m`;
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <Card key={i}>
            <div className="flex items-center justify-center h-20">
              <LoadingSpinner size="sm" />
            </div>
          </Card>
        ))}
      </div>
    );
  }

  if (!summary) {
    return null;
  }

  const activeRequests = summary.pending_requests + summary.processing_requests + summary.assigned_requests;
  const completionRate = summary.total_requests > 0 
    ? ((summary.completed_requests / summary.total_requests) * 100).toFixed(1)
    : '0';

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {/* Total Requests */}
      <Card>
        <div className="flex items-center">
          <div className="p-2 bg-blue-100 rounded-lg">
            <Package className="h-6 w-6 text-blue-600" />
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-gray-600">Total Requests</p>
            <p className="text-2xl font-semibold text-gray-900">{summary.total_requests}</p>
            <p className="text-xs text-gray-500">{activeRequests} active</p>
          </div>
        </div>
      </Card>

      {/* Processing Time */}
      <Card>
        <div className="flex items-center">
          <div className="p-2 bg-orange-100 rounded-lg">
            <Clock className="h-6 w-6 text-orange-600" />
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-gray-600">Avg Processing</p>
            <p className="text-2xl font-semibold text-gray-900">
              {formatTime(summary.avg_processing_time_minutes)}
            </p>
            <p className="text-xs text-gray-500">per request</p>
          </div>
        </div>
      </Card>

      {/* Completion Rate */}
      <Card>
        <div className="flex items-center">
          <div className="p-2 bg-green-100 rounded-lg">
            <CheckCircle className="h-6 w-6 text-green-600" />
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-gray-600">Success Rate</p>
            <p className="text-2xl font-semibold text-gray-900">{completionRate}%</p>
            <p className="text-xs text-gray-500">
              {summary.completed_requests} completed, {summary.failed_requests} failed
            </p>
          </div>
        </div>
      </Card>

      {/* Revenue */}
      <Card>
        <div className="flex items-center">
          <div className="p-2 bg-purple-100 rounded-lg">
            <DollarSign className="h-6 w-6 text-purple-600" />
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-gray-600">Est. Revenue</p>
            <p className="text-2xl font-semibold text-gray-900">
              {formatCurrency(summary.total_estimated_revenue)}
            </p>
            <p className="text-xs text-gray-500">from all requests</p>
          </div>
        </div>
      </Card>
    </div>
  );
}