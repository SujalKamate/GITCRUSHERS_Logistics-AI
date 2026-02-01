'use client';

import { useState } from 'react';
import { Clock, Package, MapPin, User, AlertCircle, CheckCircle, XCircle } from 'lucide-react';
import { DashboardLayout } from '@/components/layout';
import { Card, Button, LoadingSpinner, StatusBadge } from '@/components/ui';
import { PendingRequestsList } from '@/components/requests/PendingRequestsList';
import { RequestProcessingPanel } from '@/components/requests/RequestProcessingPanel';
import { useRequests, useRequestSummary } from '@/lib/hooks/useRequests';

export default function RequestsPage() {
  const [selectedRequest, setSelectedRequest] = useState<string | null>(null);
  const { data: pendingRequests, loading: requestsLoading, error: requestsError, refetch } = useRequests('pending');
  const { data: summary, loading: summaryLoading } = useRequestSummary();

  const handleProcessRequest = (requestId: string) => {
    setSelectedRequest(requestId);
  };

  const handleRequestProcessed = () => {
    setSelectedRequest(null);
    refetch();
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Pending Delivery Requests</h1>
            <p className="text-gray-600 mt-2">
              Customer requests waiting for AI processing and truck allocation
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500">Customer App</div>
            <a 
              href="/customer-app" 
              target="_blank"
              className="text-primary-600 hover:underline font-medium"
            >
              Open Customer Interface →
            </a>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <Clock className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Pending</p>
                {summaryLoading ? (
                  <div className="h-8 flex items-center">
                    <LoadingSpinner size="sm" />
                  </div>
                ) : (
                  <p className="text-2xl font-semibold text-gray-900">
                    {summary?.pending_requests ?? 0}
                  </p>
                )}
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Package className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Processing</p>
                {summaryLoading ? (
                  <div className="h-8 flex items-center">
                    <LoadingSpinner size="sm" />
                  </div>
                ) : (
                  <p className="text-2xl font-semibold text-gray-900">
                    {summary?.processing_requests ?? 0}
                  </p>
                )}
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Assigned</p>
                {summaryLoading ? (
                  <div className="h-8 flex items-center">
                    <LoadingSpinner size="sm" />
                  </div>
                ) : (
                  <p className="text-2xl font-semibold text-gray-900">
                    {summary?.assigned_requests ?? 0}
                  </p>
                )}
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <User className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Today</p>
                {summaryLoading ? (
                  <div className="h-8 flex items-center">
                    <LoadingSpinner size="sm" />
                  </div>
                ) : (
                  <p className="text-2xl font-semibold text-gray-900">
                    {summary?.total_requests ?? 0}
                  </p>
                )}
              </div>
            </div>
          </Card>
        </div>

        {/* Error Message */}
        {requestsError && (
          <Card className="border-red-200 bg-red-50">
            <div className="p-4 flex items-center text-red-700">
              <AlertCircle className="h-5 w-5 mr-2" />
              <span>Failed to load requests: {requestsError}</span>
            </div>
          </Card>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Pending Requests List */}
          <div className="lg:col-span-2">
            <Card>
              <Card.Header title="Pending Requests" />
              <Card.Content>
                {requestsLoading ? (
                  <div className="flex justify-center py-8">
                    <LoadingSpinner />
                  </div>
                ) : (
                  <PendingRequestsList 
                    requests={pendingRequests || []} 
                    onProcessRequest={handleProcessRequest}
                    onRefresh={refetch}
                  />
                )}
              </Card.Content>
            </Card>
          </div>

          {/* Processing Panel */}
          <div className="lg:col-span-1">
            <RequestProcessingPanel 
              selectedRequestId={selectedRequest}
              onRequestProcessed={handleRequestProcessed}
            />
          </div>
        </div>

        {/* Instructions */}
        <Card className="bg-blue-50 border-blue-200">
          <Card.Content>
            <div className="flex items-start space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Package className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <h3 className="font-semibold text-blue-900 mb-2">How It Works</h3>
                <div className="text-sm text-blue-800 space-y-1">
                  <p>1. <strong>Customers submit requests</strong> through the mobile app</p>
                  <p>2. <strong>Requests appear here</strong> as "Pending" status</p>
                  <p>3. <strong>AI processes each request</strong> to analyze requirements and find optimal trucks</p>
                  <p>4. <strong>Trucks get automatically assigned</strong> with cost estimates and timing</p>
                  <p>5. <strong>Customers receive updates</strong> via SMS/email with tracking info</p>
                </div>
              </div>
            </div>
          </Card.Content>
        </Card>
      </div>
    </DashboardLayout>
  );
}