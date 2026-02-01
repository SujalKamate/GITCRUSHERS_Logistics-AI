'use client';

import { useState } from 'react';
import { Plus, Package, Clock, MapPin, User, AlertCircle } from 'lucide-react';
import { DashboardLayout } from '@/components/layout';
import { Card, Button, LoadingSpinner, StatusBadge } from '@/components/ui';
import { RequestForm } from '@/components/requests/RequestForm';
import { RequestList } from '@/components/requests/RequestList';
import { RequestSummary } from '@/components/requests/RequestSummary';
import { useRequests, useRequestSummary } from '@/lib/hooks/useRequests';

export default function RequestsPage() {
  const [showForm, setShowForm] = useState(false);
  const { data: requests, loading: requestsLoading, error: requestsError, refetch } = useRequests();
  const { data: summary, loading: summaryLoading } = useRequestSummary();

  const handleRequestCreated = () => {
    setShowForm(false);
    refetch();
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Delivery Requests</h1>
            <p className="text-gray-600 mt-2">
              Submit and manage delivery requests processed by AI
            </p>
          </div>
          <Button
            onClick={() => setShowForm(true)}
            className="flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>New Request</span>
          </Button>
        </div>

        {/* Summary Cards */}
        <RequestSummary summary={summary} loading={summaryLoading} />

        {/* Request Form Modal */}
        {showForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">New Delivery Request</h2>
                  <Button
                    variant="ghost"
                    onClick={() => setShowForm(false)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    ×
                  </Button>
                </div>
                <RequestForm
                  onSuccess={handleRequestCreated}
                  onCancel={() => setShowForm(false)}
                />
              </div>
            </div>
          </div>
        )}

        {/* Error Message */}
        {requestsError && (
          <Card className="border-red-200 bg-red-50">
            <div className="p-4 flex items-center text-red-700">
              <AlertCircle className="h-5 w-5 mr-2" />
              <span>Failed to load requests: {requestsError}</span>
            </div>
          </Card>
        )}

        {/* Requests List */}
        <Card>
          <Card.Header title="Recent Requests" />
          <Card.Content>
            {requestsLoading ? (
              <div className="flex justify-center py-8">
                <LoadingSpinner />
              </div>
            ) : (
              <RequestList requests={requests || []} onRefresh={refetch} />
            )}
          </Card.Content>
        </Card>
      </div>
    </DashboardLayout>
  );
}