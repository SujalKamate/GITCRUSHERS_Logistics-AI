'use client';

import { useState, useEffect } from 'react';
import { Brain, Truck, DollarSign, Clock, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import { Card, Button, LoadingSpinner } from '@/components/ui';
import { useRequest } from '@/lib/hooks/useRequests';

interface RequestProcessingPanelProps {
  selectedRequestId: string | null;
  onRequestProcessed: () => void;
}

export function RequestProcessingPanel({ selectedRequestId, onRequestProcessed }: RequestProcessingPanelProps) {
  const { data: request, loading, refetch } = useRequest(selectedRequestId || '');
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    if (selectedRequestId) {
      refetch();
      // Poll for updates while processing
      const interval = setInterval(() => {
        if (request?.status === 'processing') {
          refetch();
        }
      }, 2000);
      
      return () => clearInterval(interval);
    }
  }, [selectedRequestId, request?.status, refetch]);

  const handleProcessRequest = async () => {
    if (!selectedRequestId) return;
    
    setProcessing(true);
    try {
      // Trigger AI processing (in real implementation, this would call an API)
      // For now, we'll just simulate the processing
      await new Promise(resolve => setTimeout(resolve, 3000));
      onRequestProcessed();
    } catch (error) {
      console.error('Processing failed:', error);
    } finally {
      setProcessing(false);
    }
  };

  if (!selectedRequestId) {
    return (
      <Card>
        <Card.Header title="AI Processing" />
        <Card.Content>
          <div className="text-center py-8">
            <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Select a Request</h3>
            <p className="text-gray-600">
              Choose a pending request to process with AI
            </p>
          </div>
        </Card.Content>
      </Card>
    );
  }

  if (loading) {
    return (
      <Card>
        <Card.Header title="AI Processing" />
        <Card.Content>
          <div className="flex justify-center py-8">
            <LoadingSpinner />
          </div>
        </Card.Content>
      </Card>
    );
  }

  if (!request) {
    return (
      <Card>
        <Card.Header title="AI Processing" />
        <Card.Content>
          <div className="text-center py-8">
            <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Request Not Found</h3>
            <p className="text-gray-600">
              The selected request could not be loaded
            </p>
          </div>
        </Card.Content>
      </Card>
    );
  }

  const getStatusIcon = () => {
    switch (request.status) {
      case 'pending':
        return <Clock className="h-5 w-5 text-yellow-500" />;
      case 'processing':
        return <Loader className="h-5 w-5 text-blue-500 animate-spin" />;
      case 'assigned':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      default:
        return <AlertCircle className="h-5 w-5 text-gray-500" />;
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  return (
    <Card>
      <Card.Header title="AI Processing" />
      <Card.Content>
        <div className="space-y-6">
          {/* Request Info */}
          <div className="border-b pb-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold text-gray-900">#{request.id}</h3>
              <div className="flex items-center space-x-2">
                {getStatusIcon()}
                <span className="text-sm font-medium capitalize">{request.status}</span>
              </div>
            </div>
            <p className="text-sm text-gray-600">{request.customer_name}</p>
            <p className="text-sm text-gray-600">{request.description}</p>
          </div>

          {/* Processing Steps */}
          <div className="space-y-4">
            <h4 className="font-medium text-gray-900">Processing Steps</h4>
            
            {/* Step 1: AI Analysis */}
            <div className="flex items-start space-x-3">
              <div className={`p-2 rounded-lg ${
                request.ai_analysis ? 'bg-green-100' : 
                request.status === 'processing' ? 'bg-blue-100' : 'bg-gray-100'
              }`}>
                <Brain className={`h-4 w-4 ${
                  request.ai_analysis ? 'text-green-600' : 
                  request.status === 'processing' ? 'text-blue-600' : 'text-gray-400'
                }`} />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">AI Analysis</p>
                <p className="text-xs text-gray-600">
                  {request.ai_analysis ? 'Complete' : 
                   request.status === 'processing' ? 'Analyzing requirements...' : 'Pending'}
                </p>
                {request.ai_analysis && (
                  <div className="mt-2 text-xs space-y-1">
                    <div>Risk: <span className="font-medium">{request.ai_analysis.risk_level}</span></div>
                    <div>Complexity: <span className="font-medium">{request.ai_analysis.complexity_score}/10</span></div>
                  </div>
                )}
              </div>
            </div>

            {/* Step 2: Truck Allocation */}
            <div className="flex items-start space-x-3">
              <div className={`p-2 rounded-lg ${
                request.assigned_truck_id ? 'bg-green-100' : 
                request.status === 'processing' && request.ai_analysis ? 'bg-blue-100' : 'bg-gray-100'
              }`}>
                <Truck className={`h-4 w-4 ${
                  request.assigned_truck_id ? 'text-green-600' : 
                  request.status === 'processing' && request.ai_analysis ? 'text-blue-600' : 'text-gray-400'
                }`} />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">Truck Allocation</p>
                <p className="text-xs text-gray-600">
                  {request.assigned_truck_id ? `Assigned: ${request.assigned_truck_id}` : 
                   request.status === 'processing' && request.ai_analysis ? 'Finding optimal truck...' : 'Pending'}
                </p>
                {request.allocation_reasoning && (
                  <div className="mt-2 text-xs text-gray-600">
                    {request.allocation_reasoning}
                  </div>
                )}
              </div>
            </div>

            {/* Step 3: Cost Calculation */}
            <div className="flex items-start space-x-3">
              <div className={`p-2 rounded-lg ${
                request.estimated_cost ? 'bg-green-100' : 
                request.status === 'processing' && request.assigned_truck_id ? 'bg-blue-100' : 'bg-gray-100'
              }`}>
                <DollarSign className={`h-4 w-4 ${
                  request.estimated_cost ? 'text-green-600' : 
                  request.status === 'processing' && request.assigned_truck_id ? 'text-blue-600' : 'text-gray-400'
                }`} />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">Cost Estimation</p>
                <p className="text-xs text-gray-600">
                  {request.estimated_cost ? formatCurrency(request.estimated_cost) : 
                   request.status === 'processing' && request.assigned_truck_id ? 'Calculating costs...' : 'Pending'}
                </p>
                {request.estimated_pickup_time && (
                  <div className="mt-2 text-xs text-gray-600">
                    ETA: {new Date(request.estimated_pickup_time).toLocaleString()}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Action Button */}
          <div className="pt-4 border-t">
            {request.status === 'pending' && (
              <Button
                onClick={handleProcessRequest}
                disabled={processing}
                className="w-full flex items-center justify-center space-x-2"
              >
                {processing ? (
                  <>
                    <Loader className="h-4 w-4 animate-spin" />
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <Brain className="h-4 w-4" />
                    <span>Start AI Processing</span>
                  </>
                )}
              </Button>
            )}
            
            {request.status === 'processing' && (
              <div className="text-center">
                <Loader className="h-6 w-6 animate-spin mx-auto mb-2 text-blue-500" />
                <p className="text-sm text-gray-600">AI is processing this request...</p>
              </div>
            )}
            
            {request.status === 'assigned' && (
              <div className="text-center">
                <CheckCircle className="h-6 w-6 mx-auto mb-2 text-green-500" />
                <p className="text-sm text-gray-600">Request successfully processed!</p>
                <Button
                  onClick={onRequestProcessed}
                  variant="ghost"
                  size="sm"
                  className="mt-2"
                >
                  Process Next Request
                </Button>
              </div>
            )}
          </div>
        </div>
      </Card.Content>
    </Card>
  );
}