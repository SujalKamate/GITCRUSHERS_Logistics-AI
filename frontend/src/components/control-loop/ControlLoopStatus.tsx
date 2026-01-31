/**
 * Real-time control loop status component showing current phase and progress.
 */

'use client';

import React, { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { ControlLoopPhase, ControlLoopState } from '@/types';
import { PHASE_LABELS } from '@/lib/constants';
import { Card } from '@/components/ui';
import { 
  Eye, 
  Brain, 
  FileText, 
  CheckCircle, 
  Zap, 
  RotateCcw,
  Play,
  Pause,
  Square
} from 'lucide-react';

interface ControlLoopStatusProps {
  controlLoopState?: ControlLoopState;
  isRunning?: boolean;
  onStart?: () => void;
  onStop?: () => void;
  onPause?: () => void;
  className?: string;
}

const phaseIcons = {
  [ControlLoopPhase.OBSERVE]: Eye,
  [ControlLoopPhase.REASON]: Brain,
  [ControlLoopPhase.PLAN]: FileText,
  [ControlLoopPhase.DECIDE]: CheckCircle,
  [ControlLoopPhase.ACT]: Zap,
  [ControlLoopPhase.FEEDBACK]: RotateCcw,
};

const phaseColors = {
  [ControlLoopPhase.OBSERVE]: 'text-blue-600 bg-blue-100',
  [ControlLoopPhase.REASON]: 'text-purple-600 bg-purple-100',
  [ControlLoopPhase.PLAN]: 'text-yellow-600 bg-yellow-100',
  [ControlLoopPhase.DECIDE]: 'text-green-600 bg-green-100',
  [ControlLoopPhase.ACT]: 'text-red-600 bg-red-100',
  [ControlLoopPhase.FEEDBACK]: 'text-gray-600 bg-gray-100',
};

const ControlLoopStatus: React.FC<ControlLoopStatusProps> = ({
  controlLoopState,
  isRunning = false,
  onStart,
  onStop,
  onPause,
  className,
}) => {
  const [currentPhase, setCurrentPhase] = useState<ControlLoopPhase>(ControlLoopPhase.OBSERVE);
  const [cycleCount, setCycleCount] = useState(0);
  const [progress, setProgress] = useState(0);

  // Simulate control loop progression
  useEffect(() => {
    if (!isRunning) return;

    const phases = Object.values(ControlLoopPhase);
    let phaseIndex = 0;
    let cycleProgress = 0;

    const interval = setInterval(() => {
      cycleProgress += 2; // 2% progress per tick
      
      if (cycleProgress >= 100) {
        // Move to next phase
        phaseIndex = (phaseIndex + 1) % phases.length;
        setCurrentPhase(phases[phaseIndex]);
        cycleProgress = 0;
        
        // If we completed a full cycle
        if (phaseIndex === 0) {
          setCycleCount(prev => prev + 1);
        }
      }
      
      setProgress(cycleProgress);
    }, 100); // Update every 100ms

    return () => clearInterval(interval);
  }, [isRunning]);

  const currentPhaseData = controlLoopState?.current_phase || currentPhase;
  const totalCycles = controlLoopState?.total_cycles || cycleCount;
  const cycleId = controlLoopState?.cycle_id || `CYCLE-${Date.now()}`;

  const PhaseIcon = phaseIcons[currentPhaseData];
  const phaseColorClass = phaseColors[currentPhaseData];

  return (
    <div className={className}>
      <Card>
        <Card.Header
          title="AI Control Loop"
          subtitle="Continuous decision-making system"
          action={
            <div className="flex items-center space-x-2">
              {!isRunning ? (
                <button
                  onClick={onStart}
                  className="flex items-center space-x-1 px-3 py-1 bg-success-600 text-white rounded-lg hover:bg-success-700 transition-colors"
                >
                  <Play className="w-4 h-4" />
                  <span>Start</span>
                </button>
              ) : (
                <>
                  <button
                    onClick={onPause}
                    className="flex items-center space-x-1 px-3 py-1 bg-warning-600 text-white rounded-lg hover:bg-warning-700 transition-colors"
                  >
                    <Pause className="w-4 h-4" />
                    <span>Pause</span>
                  </button>
                  <button
                    onClick={onStop}
                    className="flex items-center space-x-1 px-3 py-1 bg-danger-600 text-white rounded-lg hover:bg-danger-700 transition-colors"
                  >
                    <Square className="w-4 h-4" />
                    <span>Stop</span>
                  </button>
                </>
              )}
            </div>
          }
        />

        <Card.Content>
          <div className="space-y-6">
            {/* Current Phase */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className={cn('p-3 rounded-lg', phaseColorClass)}>
                  <PhaseIcon className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    {PHASE_LABELS[currentPhaseData]}
                  </h3>
                  <p className="text-sm text-gray-600">
                    Current phase in decision cycle
                  </p>
                </div>
              </div>
              
              <div className="text-right">
                <div className="text-2xl font-bold text-gray-900">
                  {totalCycles}
                </div>
                <div className="text-sm text-gray-600">
                  Cycles Completed
                </div>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Phase Progress</span>
                <span className="font-medium">{Math.round(progress)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={cn(
                    'h-2 rounded-full transition-all duration-300',
                    isRunning ? 'bg-primary-600' : 'bg-gray-400'
                  )}
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>

            {/* Phase Indicators */}
            <div className="grid grid-cols-6 gap-2">
              {Object.values(ControlLoopPhase).map((phase) => {
                const Icon = phaseIcons[phase];
                const isActive = phase === currentPhaseData;
                const isCompleted = Object.values(ControlLoopPhase).indexOf(phase) < 
                                  Object.values(ControlLoopPhase).indexOf(currentPhaseData);

                return (
                  <div
                    key={phase}
                    className={cn(
                      'flex flex-col items-center p-2 rounded-lg transition-all',
                      isActive 
                        ? phaseColors[phase]
                        : isCompleted
                        ? 'bg-success-100 text-success-600'
                        : 'bg-gray-100 text-gray-400'
                    )}
                  >
                    <Icon className="w-4 h-4 mb-1" />
                    <span className="text-xs font-medium text-center">
                      {PHASE_LABELS[phase]}
                    </span>
                  </div>
                );
              })}
            </div>

            {/* Cycle Information */}
            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
              <div>
                <div className="text-sm text-gray-600">Current Cycle</div>
                <div className="font-mono text-sm text-gray-900">
                  {cycleId.substring(0, 12)}...
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Status</div>
                <div className="flex items-center space-x-2">
                  <div className={cn(
                    'w-2 h-2 rounded-full',
                    isRunning ? 'bg-success-500 animate-pulse' : 'bg-gray-400'
                  )} />
                  <span className="text-sm font-medium">
                    {isRunning ? 'Running' : 'Stopped'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </Card.Content>
      </Card>
    </div>
  );
};

export default ControlLoopStatus;