'use client';

import { X, User, Package, MapPin, Clock, Truck, Brain, DollarSign } from 'lucide-react';
import { Button, StatusBadge } from '@/components/ui';

interface Request {
  id: string;
  customer_name: string;
  customer_phone?: string;
  customer_email?: string;
  description: string;
  weight_kg: number;
  volume_m3?: number;
  priority: string;
  status: string;
  pickup_address: string;
  delivery_address: string;
  created_at: string;
  processed_at?: string;
  estimated_cost?: number;
  estimated_pickup_time?: string;
  estimated_delivery_time?: string;
  assigned_truck_id?: string;
  assigned_load_id?: string;
  ai_analysis?: any;
  allocation_reasoning?: string;
  special_instructions?: string;
  fragile?: boolean;
  temperature_controlled?: boolean;
}

interface RequestModalProps {
  request: Request;
  onClose: () => void;
}

export function RequestModal({ request, onClose }: RequestModalProps) {
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

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b">
          <div className="flex items-center space-x-4">
            <h2 className="text-2xl font-bold text-gray-900">Request Details</h2>
            <StatusBadge status={request.status} color={getStatusColor(request.status)} />
          </div>
          <Button onClick={onClose} variant="ghost" className="text-gray-500 hover:text-gray-700">
            <X className="h-5 w-5" />
          </Button>
        </div>

        <div className="p-6 space-y-8">
          {/* Basic Info */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Customer Information */}
            <div className="space-y-4">
              <div className="flex items-center space-x-2 text-lg font-semibold text-gray-900">
                <User className="h-5 w-5" />
                <span>Customer Information</span>
              </div>
              <div className="space-y-2 text-sm">
                <div><span className="font-medium">Name:</span> {request.customer_name}</div>
                {request.customer_phone && (
                  <div><span className="font-medium">Phone:</span> {request.customer_phone}</div>
                )}
                {request.customer_email && (
                  <div><span className="font-medium">Email:</span> {request.customer_email}</div>
                )}
                <div><span className="font-medium">Request ID:</span> {request.id}</div>
              </div>
            </div>

            {/* Package Information */}
            <div className="space-y-4">
              <div className="flex items-center space-x-2 text-lg font-semibold text-gray-900">
                <Package className="h-5 w-5" />
                <span>Package Details</span>
              </div>
              <div className="space-y-2 text-sm">
                <div><span className="font-medium">Description:</span> {request.description}</div>
                <div><span className="font-medium">Weight:</span> {request.weight_kg} kg</div>
                {request.volume_m3 && (
                  <div><span className="font-medium">Volume:</span> {request.volume_m3} m³</div>
                )}
                <div><span className="font-medium">Priority:</span> 
                  <span className={`ml-1 font-semibold ${
                    request.priority === 'critical' ? 'text-red-800' :
                    request.priority === 'urgent' ? 'text-red-600' :
                    request.priority === 'high' ? 'text-orange-600' :
                    request.priority === 'normal' ? 'text-blue-600' : 'text-gray-600'
                  }`}>
                    {request.priority.toUpperCase()}
                  </span>
                </div>
                {(request.fragile || request.temperature_controlled) && (
                  <div className="flex space-x-2">
                    {request.fragile && (
                      <span className="px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded">Fragile</span>
                    )}
                    {request.temperature_controlled && (
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">Temperature Controlled</span>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Locations */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2 text-lg font-semibold text-gray-900">
              <MapPin className="h-5 w-5" />
              <span>Locations</span>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium text-green-600">Pickup:</span>
                <div className="text-gray-700 mt-1">{request.pickup_address}</div>
              </div>
              <div>
                <span className="font-medium text-red-600">Delivery:</span>
                <div className="text-gray-700 mt-1">{request.delivery_address}</div>
              </div>
            </div>
          </div>

          {/* Timing */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2 text-lg font-semibold text-gray-900">
              <Clock className="h-5 w-5" />
              <span>Timeline</span>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 text-sm">
              <div className="space-y-2">
                <div><span className="font-medium">Created:</span> {formatDateTime(request.created_at)}</div>
                {request.processed_at && (
                  <div><span className="font-medium">Processed:</span> {formatDateTime(request.processed_at)}</div>
                )}
              </div>
              <div className="space-y-2">
                {request.estimated_pickup_time && (
                  <div><span className="font-medium">Est. Pickup:</span> {formatDateTime(request.estimated_pickup_time)}</div>
                )}
                {request.estimated_delivery_time && (
                  <div><span className="font-medium">Est. Delivery:</span> {formatDateTime(request.estimated_delivery_time)}</div>
                )}
              </div>
            </div>
          </div>

          {/* Assignment & Cost */}
          {(request.assigned_truck_id || request.estimated_cost) && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Assignment */}
              {request.assigned_truck_id && (
                <div className="space-y-4">
                  <div className="flex items-center space-x-2 text-lg font-semibold text-gray-900">
                    <Truck className="h-5 w-5" />
                    <span>Assignment</span>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div><span className="font-medium">Truck:</span> {request.assigned_truck_id}</div>
                    {request.assigned_load_id && (
                      <div><span className="font-medium">Load ID:</span> {request.assigned_load_id}</div>
                    )}
                  </div>
                </div>
              )}

              {/* Cost */}
              {request.estimated_cost && (
                <div className="space-y-4">
                  <div className="flex items-center space-x-2 text-lg font-semibold text-gray-900">
                    <DollarSign className="h-5 w-5" />
                    <span>Pricing</span>
                  </div>
                  <div className="text-2xl font-bold text-green-600">
                    {formatCurrency(request.estimated_cost)}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* AI Analysis */}
          {(request.ai_analysis || request.allocation_reasoning) && (
            <div className="space-y-4">
              <div className="flex items-center space-x-2 text-lg font-semibold text-gray-900">
                <Brain className="h-5 w-5" />
                <span>AI Analysis</span>
              </div>
              
              {request.ai_analysis && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-3">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Risk Level:</span>
                      <span className={`ml-2 px-2 py-1 rounded text-xs ${
                        request.ai_analysis.risk_level === 'high' ? 'bg-red-100 text-red-800' :
                        request.ai_analysis.risk_level === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {request.ai_analysis.risk_level?.toUpperCase()}
                      </span>
                    </div>
                    <div>
                      <span className="font-medium">Complexity Score:</span>
                      <span className="ml-2">{request.ai_analysis.complexity_score}/10</span>
                    </div>
                  </div>
                  
                  {request.ai_analysis.special_requirements?.length > 0 && (
                    <div>
                      <span className="font-medium text-sm">Special Requirements:</span>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {request.ai_analysis.special_requirements.map((req: string, index: number) => (
                          <span key={index} className="px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded">
                            {req.replace('_', ' ')}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {request.ai_analysis.reasoning && (
                    <div>
                      <span className="font-medium text-sm">AI Reasoning:</span>
                      <p className="text-sm text-gray-700 mt-1">{request.ai_analysis.reasoning}</p>
                    </div>
                  )}
                </div>
              )}

              {request.allocation_reasoning && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <span className="font-medium text-sm">Allocation Reasoning:</span>
                  <p className="text-sm text-gray-700 mt-1">{request.allocation_reasoning}</p>
                </div>
              )}
            </div>
          )}

          {/* Special Instructions */}
          {request.special_instructions && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">Special Instructions</h3>
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <p className="text-sm text-gray-700">{request.special_instructions}</p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end p-6 border-t">
          <Button onClick={onClose}>Close</Button>
        </div>
      </div>
    </div>
  );
}