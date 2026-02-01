'use client';

import { Clock, MapPin, Package, User, AlertTriangle, RefreshCw } from 'lucide-react';
import { Button, StatusBadge } from '@/components/ui';

interface PendingRequest {
  id: string;
  customer_name: string;
  customer_phone?: string;
  description: string;
  weight_kg: number;
  priority: string;
  pickup_address: string;
  delivery_address: string;
  created_at: string;
  fragile?: boolean;
  temperature_controlled?: boolean;
  special_instructions?: string;
}

interface PendingRequestsListProps {
  requests: PendingRequest[];
  onProcessRequest: (requestId: string) => void;
  onRefresh: () => void;
}

export function PendingRequestsList({ requests, onProcessRequest, onRefresh }: PendingRequestsListProps) {
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'text-red-600 bg-red-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'normal': return 'text-blue-600 bg-blue-100';
      case 'low': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return date.toLocaleDateString();
  };

  if (requests.length === 0) {
    return (
      <div className="text-center py-12">
        <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No pending requests</h3>
        <p className="text-gray-600 mb-4">
          All customer requests have been processed
        </p>
        <Button onClick={onRefresh} variant="ghost" className="flex items-center space-x-2">
          <RefreshCw className="h-4 w-4" />
          <span>Refresh</span>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium text-gray-900">
          {requests.length} Pending Request{requests.length !== 1 ? 's' : ''}
        </h3>
        <Button onClick={onRefresh} variant="ghost" size="sm" className="flex items-center space-x-2">
          <RefreshCw className="h-4 w-4" />
          <span>Refresh</span>
        </Button>
      </div>

      {/* Request Cards */}
      <div className="space-y-3">
        {requests.map((request) => (
          <div
            key={request.id}
            className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow bg-yellow-50 border-yellow-200"
          >
            <div className="flex justify-between items-start mb-3">
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2">
                  <User className="h-4 w-4 text-gray-500" />
                  <span className="font-medium text-gray-900">{request.customer_name}</span>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(request.priority)}`}>
                  {request.priority.toUpperCase()}
                </span>
                {(request.fragile || request.temperature_controlled) && (
                  <div className="flex space-x-1">
                    {request.fragile && (
                      <span className="px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded">
                        <AlertTriangle className="h-3 w-3 inline mr-1" />
                        Fragile
                      </span>
                    )}
                    {request.temperature_controlled && (
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                        🌡️ Temp Control
                      </span>
                    )}
                  </div>
                )}
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-500">#{request.id}</span>
                <Button
                  onClick={() => onProcessRequest(request.id)}
                  size="sm"
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                >
                  Process
                </Button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
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
                  <div className="text-gray-600 text-xs">
                    <span className="font-medium text-green-600">From:</span> {request.pickup_address.substring(0, 40)}...
                  </div>
                  <div className="text-gray-600 text-xs">
                    <span className="font-medium text-red-600">To:</span> {request.delivery_address.substring(0, 40)}...
                  </div>
                </div>
              </div>

              <div className="flex items-start space-x-2">
                <Clock className="h-4 w-4 text-gray-500 mt-0.5" />
                <div>
                  <div className="text-gray-600">Submitted: {formatTime(request.created_at)}</div>
                  {request.customer_phone && (
                    <div className="text-gray-600 text-xs">📞 {request.customer_phone}</div>
                  )}
                </div>
              </div>
            </div>

            {request.special_instructions && (
              <div className="mt-3 p-2 bg-gray-50 rounded text-sm">
                <span className="font-medium text-gray-700">Instructions:</span> {request.special_instructions}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}