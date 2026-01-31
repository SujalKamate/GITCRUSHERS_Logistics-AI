/**
 * AI Control Loop Dashboard page.
 */

'use client';

import React, { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout';
import { Card, Button, LoadingSpinner } from '@/components/ui';
import {
  ControlLoopStatus,
  DecisionStream,
  SystemHealth,
  CycleVisualization
} from '@/components/control-loop';
import { ControlLoopPhase, ControlLoopState, Decision } from '@/types';
import {
  useControlLoopStatus,
  usePendingDecisions,
  useStartControlLoop,
  useStopControlLoop
} from '@/lib/hooks/useApi';
import { WS_BASE_URL } from '@/lib/constants';
import {
  Brain,
  Play,
  Pause,
  Square,
  Settings,
  BarChart3,
  AlertTriangle,
  RefreshCw
} from 'lucide-react';

const AIControlPage: React.FC = () => {
  const [showSettings, setShowSettings] = useState(false);

  // Fetch control loop status from API
  const {
    data: controlLoopStatus,
    loading: statusLoading,
    error: statusError,
    refetch: refetchStatus
  } = useControlLoopStatus();

  // Fetch pending decisions from API
  const {
    data: pendingDecisions,
    loading: decisionsLoading,
    refetch: refetchDecisions
  } = usePendingDecisions();

  // Mutations for start/stop
  const { mutate: startLoop, loading: startLoading } = useStartControlLoop();
  const { mutate: stopLoop, loading: stopLoading } = useStopControlLoop();

  // Derive state from API response
  const isRunning = controlLoopStatus?.is_running ?? false;
  const currentPhase = (controlLoopStatus?.current_state?.current_phase as ControlLoopPhase) ?? ControlLoopPhase.OBSERVE;
  const cycleCount = controlLoopStatus?.current_state?.total_cycles ?? 0;

  // Build control loop state for child components
  const controlLoopState: Partial<ControlLoopState> = {
    current_phase: currentPhase,
    cycle_id: controlLoopStatus?.current_state?.cycle_id ?? '',
    total_cycles: cycleCount,
    continue_loop: isRunning,
    requires_human_intervention: (pendingDecisions?.requires_human_approval?.length ?? 0) > 0,
  };

  // WebSocket connection for real-time updates
  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimeout: NodeJS.Timeout;

    const connect = () => {
      try {
        ws = new WebSocket(`${WS_BASE_URL}/ws`);

        ws.onopen = () => {
          console.log('AI Control WebSocket connected');
          ws?.send(JSON.stringify({
            type: 'subscribe',
            events: ['control_loop_update', 'control_loop_phase_change', 'decision_pending']
          }));
        };

        ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            if (message.type === 'control_loop_update' ||
                message.type === 'control_loop_phase_change') {
              refetchStatus();
            }
            if (message.type === 'decision_pending') {
              refetchDecisions();
            }
          } catch (e) {
            console.error('Failed to parse WebSocket message:', e);
          }
        };

        ws.onclose = () => {
          console.log('WebSocket disconnected, reconnecting...');
          reconnectTimeout = setTimeout(connect, 3000);
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
        };
      } catch (e) {
        console.error('WebSocket connection failed:', e);
        reconnectTimeout = setTimeout(connect, 3000);
      }
    };

    connect();

    return () => {
      if (ws) {
        ws.close();
      }
      clearTimeout(reconnectTimeout);
    };
  }, [refetchStatus, refetchDecisions]);

  const handleStart = async () => {
    await startLoop({});
    refetchStatus();
  };

  const handleStop = async () => {
    await stopLoop('User requested stop');
    refetchStatus();
  };

  const handlePause = async () => {
    await stopLoop('User paused');
    refetchStatus();
  };

  const handlePhaseClick = (phase: ControlLoopPhase) => {
    console.log('Phase clicked:', phase);
  };

  // Convert decisions for DecisionStream
  const decisions: Decision[] = pendingDecisions?.decisions ?? [];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center">
              <Brain className="w-8 h-8 text-primary-600 mr-3" />
              AI Control Loop Dashboard
            </h1>
            <p className="text-gray-600">
              Monitor the continuous decision-making process of your agentic AI system
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                refetchStatus();
                refetchDecisions();
              }}
              icon={<RefreshCw className={`w-4 h-4 ${statusLoading ? 'animate-spin' : ''}`} />}
              disabled={statusLoading}
            >
              Refresh
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowSettings(!showSettings)}
              icon={<Settings className="w-4 h-4" />}
            >
              Settings
            </Button>
            <Button
              variant="outline"
              size="sm"
              icon={<BarChart3 className="w-4 h-4" />}
            >
              Analytics
            </Button>
          </div>
        </div>

        {/* Error State */}
        {statusError && (
          <Card className="border-danger-200 bg-danger-50">
            <div className="p-4 flex items-center text-danger-700">
              <AlertTriangle className="h-5 w-5 mr-2" />
              <span>Failed to load control loop status: {statusError}</span>
              <Button
                variant="outline"
                size="sm"
                className="ml-4"
                onClick={() => refetchStatus()}
              >
                Retry
              </Button>
            </div>
          </Card>
        )}

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card padding="sm">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-primary-100 rounded-lg">
                <Brain className="w-5 h-5 text-primary-600" />
              </div>
              <div>
                <div className="text-sm text-gray-600">Total Cycles</div>
                <div className="text-xl font-semibold">
                  {statusLoading ? <LoadingSpinner size="sm" /> : cycleCount.toLocaleString()}
                </div>
              </div>
            </div>
          </Card>

          <Card padding="sm">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-success-100 rounded-lg">
                <Play className="w-5 h-5 text-success-600" />
              </div>
              <div>
                <div className="text-sm text-gray-600">Decisions/Hour</div>
                <div className="text-xl font-semibold">
                  {statusLoading ? (
                    <LoadingSpinner size="sm" />
                  ) : (
                    Math.round((controlLoopStatus?.cycles_per_minute ?? 0) * 60)
                  )}
                </div>
              </div>
            </div>
          </Card>

          <Card padding="sm">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-warning-100 rounded-lg">
                <AlertTriangle className="w-5 h-5 text-warning-600" />
              </div>
              <div>
                <div className="text-sm text-gray-600">Pending Decisions</div>
                <div className="text-xl font-semibold">
                  {decisionsLoading ? (
                    <LoadingSpinner size="sm" />
                  ) : (
                    pendingDecisions?.decisions?.length ?? 0
                  )}
                </div>
              </div>
            </div>
          </Card>

          <Card padding="sm">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <BarChart3 className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <div className="text-sm text-gray-600">Avg Cycle Time</div>
                <div className="text-xl font-semibold">
                  {statusLoading ? (
                    <LoadingSpinner size="sm" />
                  ) : (
                    `${Math.round(controlLoopStatus?.average_cycle_duration_ms ?? 0)}ms`
                  )}
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Main Dashboard Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          {/* Left Column - Control Loop Status & Visualization */}
          <div className="xl:col-span-2 space-y-6">
            {/* Control Loop Status */}
            <ControlLoopStatus
              controlLoopState={controlLoopState as ControlLoopState}
              isRunning={isRunning}
              onStart={handleStart}
              onStop={handleStop}
              onPause={handlePause}
            />

            {/* Cycle Visualization */}
            <CycleVisualization
              currentPhase={currentPhase}
              isRunning={isRunning}
              onPhaseClick={handlePhaseClick}
            />
          </div>

          {/* Right Column - Decision Stream */}
          <div className="xl:col-span-1">
            <DecisionStream
              decisions={decisions}
              maxItems={8}
              autoScroll={true}
            />
          </div>
        </div>

        {/* Bottom Row - System Health */}
        <SystemHealth />

        {/* Settings Panel (if shown) */}
        {showSettings && (
          <Card>
            <Card.Header
              title="Control Loop Settings"
              subtitle="Configure AI decision-making parameters"
            />
            <Card.Content>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Cycle Interval (seconds)
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="60"
                      defaultValue="5"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Auto-approve Low Risk Decisions
                    </label>
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        defaultChecked
                        className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                      />
                      <span className="ml-2 text-sm text-gray-600">
                        Automatically execute decisions with confidence &gt; 90%
                      </span>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Human Approval Timeout (minutes)
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="60"
                      defaultValue="5"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Max Cycles per Run
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="10000"
                      defaultValue="1000"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    />
                  </div>
                </div>
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <Button variant="outline" onClick={() => setShowSettings(false)}>
                  Cancel
                </Button>
                <Button variant="primary">
                  Save Settings
                </Button>
              </div>
            </Card.Content>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
};

export default AIControlPage;
