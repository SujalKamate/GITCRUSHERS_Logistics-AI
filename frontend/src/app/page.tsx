'use client';

import { MapPin, Activity, AlertTriangle } from 'lucide-react'
import { DashboardLayout } from '@/components/layout'
import { Card, LoadingSpinner } from '@/components/ui'
import { useFleetStatus, useControlLoopStatus } from '@/lib/hooks/useApi'

export default function HomePage() {
  const { data: fleetStatus, loading: fleetLoading, error: fleetError } = useFleetStatus();
  const { data: controlLoopStatus, loading: controlLoopLoading } = useControlLoopStatus();

  const summary = fleetStatus?.summary;
  const isControlLoopRunning = controlLoopStatus?.is_running ?? false;

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Welcome to Logistics AI Control System
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl">
            Continuous decision-making for road logistics. Our agentic AI system
            observes, reasons, plans, and acts to optimize your fleet operations in real-time.
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <div className="flex items-center">
              <div className="p-2 bg-primary-100 rounded-lg">
                <MapPin className="h-6 w-6 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active Trucks</p>
                {fleetLoading ? (
                  <div className="h-8 flex items-center">
                    <LoadingSpinner size="sm" />
                  </div>
                ) : (
                  <p className="text-2xl font-semibold text-gray-900">
                    {summary?.total_trucks ?? 0}
                  </p>
                )}
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center">
              <div className="p-2 bg-success-100 rounded-lg">
                <MapPin className="h-6 w-6 text-success-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">En Route</p>
                {fleetLoading ? (
                  <div className="h-8 flex items-center">
                    <LoadingSpinner size="sm" />
                  </div>
                ) : (
                  <p className="text-2xl font-semibold text-gray-900">
                    {summary?.active_trucks ?? 0}
                  </p>
                )}
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center">
              <div className="p-2 bg-warning-100 rounded-lg">
                <Activity className="h-6 w-6 text-warning-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active Loads</p>
                {fleetLoading ? (
                  <div className="h-8 flex items-center">
                    <LoadingSpinner size="sm" />
                  </div>
                ) : (
                  <p className="text-2xl font-semibold text-gray-900">
                    {summary?.total_loads ?? 0}
                  </p>
                )}
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center">
              <div className="p-2 bg-danger-100 rounded-lg">
                <AlertTriangle className="h-6 w-6 text-danger-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Issues</p>
                {fleetLoading ? (
                  <div className="h-8 flex items-center">
                    <LoadingSpinner size="sm" />
                  </div>
                ) : (
                  <p className="text-2xl font-semibold text-gray-900">
                    {summary?.trucks_with_issues ?? 0}
                  </p>
                )}
              </div>
            </div>
          </Card>
        </div>

        {/* Error Message */}
        {fleetError && (
          <Card className="mb-8 border-danger-200 bg-danger-50">
            <div className="p-4 flex items-center text-danger-700">
              <AlertTriangle className="h-5 w-5 mr-2" />
              <span>Failed to load fleet data: {fleetError}</span>
            </div>
          </Card>
        )}

        {/* Control Loop Status */}
        <Card className="mb-8">
          <Card.Header title="AI Control Loop Status" />
          <Card.Content>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-6">
                <div className="flex items-center">
                  <div className={`h-3 w-3 rounded-full mr-2 ${
                    isControlLoopRunning
                      ? 'bg-success-500 animate-pulse'
                      : 'bg-gray-300'
                  }`}></div>
                  <span className="text-sm text-gray-600">
                    {controlLoopStatus?.current_state?.current_phase === 'observe' ? 'Observing' : 'Observe'}
                  </span>
                </div>
                <div className="flex items-center">
                  <div className={`h-3 w-3 rounded-full mr-2 ${
                    controlLoopStatus?.current_state?.current_phase === 'reason'
                      ? 'bg-primary-500 animate-pulse'
                      : 'bg-gray-300'
                  }`}></div>
                  <span className="text-sm text-gray-600">Reasoning</span>
                </div>
                <div className="flex items-center">
                  <div className={`h-3 w-3 rounded-full mr-2 ${
                    controlLoopStatus?.current_state?.current_phase === 'plan'
                      ? 'bg-warning-500 animate-pulse'
                      : 'bg-gray-300'
                  }`}></div>
                  <span className="text-sm text-gray-600">Planning</span>
                </div>
                <div className="flex items-center">
                  <div className={`h-3 w-3 rounded-full mr-2 ${
                    controlLoopStatus?.current_state?.current_phase === 'act'
                      ? 'bg-success-500 animate-pulse'
                      : 'bg-gray-300'
                  }`}></div>
                  <span className="text-sm text-gray-600">Acting</span>
                </div>
              </div>
              <div className="text-sm text-gray-500">
                {controlLoopLoading ? (
                  <LoadingSpinner size="sm" />
                ) : (
                  <>
                    Cycle #{controlLoopStatus?.current_state?.total_cycles?.toLocaleString() ?? 0} •
                    {isControlLoopRunning ? ' Running' : ' Stopped'}
                  </>
                )}
              </div>
            </div>
          </Card.Content>
        </Card>

        {/* Coming Soon Features */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card>
            <Card.Header title="Real-time Fleet Map" />
            <Card.Content>
              <p className="text-gray-600 mb-4">
                Interactive map showing live truck positions, routes, and traffic conditions.
              </p>
              <div className="bg-gray-100 rounded-lg h-32 flex items-center justify-center">
                <a href="/fleet" className="text-primary-600 hover:underline">
                  View Fleet Map →
                </a>
              </div>
            </Card.Content>
          </Card>

          <Card>
            <Card.Header title="AI Control Loop" />
            <Card.Content>
              <p className="text-gray-600 mb-4">
                Monitor the continuous AI decision-making process with real-time cycle visualization.
              </p>
              <div className="bg-gray-100 rounded-lg h-32 flex items-center justify-center">
                <a href="/ai-control" className="text-primary-600 hover:underline">
                  View AI Control →
                </a>
              </div>
            </Card.Content>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  )
}
