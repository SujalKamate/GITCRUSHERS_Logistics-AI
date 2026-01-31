/**
 * AI Control Loop Dashboard page.
 */

'use client';

import React, { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout';
import { Card, Button } from '@/components/ui';
import { 
  ControlLoopStatus, 
  DecisionStream, 
  SystemHealth, 
  CycleVisualization 
} from '@/components/control-loop';
import { ControlLoopPhase, ControlLoopState } from '@/types';
import { 
  Brain, 
  Play, 
  Pause, 
  Square, 
  Settings,
  BarChart3,
  AlertTriangle
} from 'lucide-react';

const AIControlPage: React.FC = () => {
  const [isRunning, setIsRunning] = useState(true);
  const [currentPhase, setCurrentPhase] = useState<ControlLoopPhase>(ControlLoopPhase.OBSERVE);
  const [cycleCount, setCycleCount] = useState(1247);
  const [showSettings, setShowSettings] = useState(false);

  // Mock control loop state
  const [controlLoopState, setControlLoopState] = useState<Partial<ControlLoopState>>({
    current_phase: currentPhase,
    cycle_id: `CYCLE-${Date.now()}`,
    total_cycles: cycleCount,
    continue_loop: isRunning,
    requires_human_intervention: false,
  });

  // Update control loop state when running status changes
  useEffect(() => {
    setControlLoopState(prev => ({
      ...prev,
      continue_loop: isRunning,
      current_phase: currentPhase,
      total_cycles: cycleCount,
    }));
  }, [isRunning, currentPhase, cycleCount]);

  const handleStart = () => {
    setIsRunning(true);
    console.log('Control loop started');
  };

  const handleStop = () => {
    setIsRunning(false);
    console.log('Control loop stopped');
  };

  const handlePause = () => {
    setIsRunning(false);
    console.log('Control loop paused');
  };

  const handlePhaseClick = (phase: ControlLoopPhase) => {
    console.log('Phase clicked:', phase);
    // In real implementation, this might show detailed phase information
  };

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

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card padding="sm">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-primary-100 rounded-lg">
                <Brain className="w-5 h-5 text-primary-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Total Cycles</p>
                <p className="text-xl font-semibold">{cycleCount.toLocaleString()}</p>
              </div>
            </div>
          </Card>

          <Card padding="sm">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-success-100 rounded-lg">
                <Play className="w-5 h-5 text-success-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Decisions/Hour</p>
                <p className="text-xl font-semibold">720</p>
              </div>
            </div>
          </Card>

          <Card padding="sm">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-warning-100 rounded-lg">
                <AlertTriangle className="w-5 h-5 text-warning-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Active Issues</p>
                <p className="text-xl font-semibold">2</p>
              </div>
            </div>
          </Card>

          <Card padding="sm">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <BarChart3 className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Success Rate</p>
                <p className="text-xl font-semibold">96.5%</p>
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