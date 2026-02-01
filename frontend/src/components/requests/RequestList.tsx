'use client';

import { useState } from 'react';
import { Eye, MapPin, Clock, Package, User, Truck, RefreshCw } from 'lucide-react';
import { Button, StatusBadge } from '@/components/ui';
import { RequestModal } from './RequestModal';

interface Request {
  id: string;
  customer_name: string;
  description: string;
  weight_kg: number;
  priority: string;
  status: string;
  pickup_address: string;
  delivery_address: string;
  created_at: string;
  estimated_cost?: number;
  estimated_pickup_time?: string;
  estimated_delivery_time?: string;
  assigned_truck_id?: string;
}

interface RequestListProps {
  requests: Request[];
  onRefresh: () => void;
}

export function RequestList({ requests, onRefresh }: RequestListProps) {
  const [selectedRequest, setSelectedRequest] = useState<Request | null>(null);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'yellow';
      case 'processing': return 'blue';
      case 'assigned': return 'green';
      case 'in_transit': return 'purple';
      case 'delivered': return 'green';
      case 'cancelled': return 'gray';
      case 'failed': return 'red';
      default: return 'gray';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'low': return 'text-gray-600';
      case 'normal': return 'text-blue-600';
      case 'high': return 'text-orange-600';
      case 'urgent': return 'text-red-600';
      case 'critical': return 'text-red-800 font-bold';
      default: return 'text-gray-600';
    }
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  if (requests.length === 0) {
    return (
      <div className="text-center py-12">
        <Package className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No requests yet</h3>
        <p className="text-gray-600 mb-4">
          Create your first delivery request to get started
        </p>
        <Button onClick={onRefresh} variant="ghost" className="flex items-center space-x-2">
          <RefreshCw className="h-4 w-4" />
          <span>Refresh</span>
        </Button>
      </div>
    );
  }

  return (
    <>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-medium text-gray-900">
            {requests.length} Request{requests.length !== 1 ? 's' : ''}
          </h3>
          <Button onClick={onRefresh} variant="ghost" size="sm" className="flex items-center space-x-2">
            <RefreshCw className="h-4 w-4" />
            <span>Refresh</span>
          </Button>
        </div>

        {/* Request Cards */}
        <div className="grid gap-4">
          {requests.map((request) => (
            <div
              key={request.id}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start mb-3">
                <div className="flex items-center space-x-3">
                  <div className="flex items-center space-x-2">
                    <User className="h-4 w-4 text-gray-500" />
                    <span className="font-medium text-gray-900">{request.customer_name}</span>
                  </div>
                  <StatusBadge status={request.status} color={getStatusColor(request.status)} />
                  <span className={`text-sm font-medium ${getPriorityColor(request.priority)}`}>
                    {request.priority.toUpperCase()}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-500">#{request.id}</span>
                  <Button
                    onClick={() => setSelectedRequest(request)}
                    variant="ghost"
                    size="sm"
                    className="flex items-center space-x-1"
                  >
                    <Eye className="h-4 w-4" />
                    <span>View</span>
                  </Button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                <div className="flex items-start space-x-2">
                  <Package className="h-4 w-4 text-gray-500 mt-0.5" />
                  <div>
                    <div className="font-medium text-gray-900">{request.description}</div>
                    <div className="text-gray-600">{request.weight_kg}kg</div>
                  </div>
                </div>

                <div className="flex items-start space-x-2">
                  <MapPin className="h-4 w-4 text-gray-500 mt-0.5" />
                  <div>
                    <div className="text-gray-600 truncate" title={request.pickup_address}>
                      From: {request.pickup_address}
                    </div>
                    <div className="text-gray-600 truncate" title={request.delivery_address}>
                      To: {request.delivery_address}
                    </div>
                  </div>
                </div>

                <div className="flex items-start space-x-2">
                  <Clock className="h-4 w-4 text-gray-500 mt-0.5" />
                  <div>
                    <div className="text-gray-600">
                      Created: {formatDateTime(request.created_at)}
                    </div>
                    {request.estimated_delivery_time && (
                      <div className="text-gray-600">
                        ETA: {formatDateTime(request.estimated_delivery_time)}
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex items-start space-x-2">
                  <div className="flex flex-col space-y-1">
                    {request.estimated_cost && (
                      <div className="font-medium text-green-600">
                        {formatCurrency(request.estimated_cost)}
                      </div>
                    )}
                    {request.assigned_truck_id && (
                      <div className="flex items-center space-x-1 text-gray-600">
                        <Truck className="h-3 w-3" />
                        <span className="text-xs">{request.assigned_truck_id}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Request Detail Modal */}
      {selectedRequest && (
        <RequestModal
          request={selectedRequest}
          onClose={() => setSelectedRequest(null)}
        />
      )}
    </>
  );
}