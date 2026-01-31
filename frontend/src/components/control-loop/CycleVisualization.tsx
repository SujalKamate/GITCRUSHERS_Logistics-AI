/**
 * Visual representation of the control loop cycle with animated progress.
 */

'use client';

import React, { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { ControlLoopPhase } from '@/types';
import { PHASE_LABELS } from '@/lib/constants';
import { Card } from '@/components/ui';
import { 
  Eye, 
  Brain, 
  FileText, 
  CheckCircle, 
  Zap, 
  RotateCcw,
  ArrowRight,
  Play,
  Pause
} from 'lucide-react';

interface CycleVisualizationProps {
  currentPhase?: ControlLoopPhase;
  isRunning?: boolean;
  cycleProgress?: number;
  onPhaseClick?: (phase: ControlLoopPhase) => void;
  className?: string;
}

const phaseConfig: Record<ControlLoopPhase, {
  icon: React.ComponentType<any>;
  color: ColorKey;
  description: string;
  duration: number;
}> = {
  [ControlLoopPhase.OBSERVE]: {
    icon: Eye,
    color: 'blue',
    description: 'Collecting real-time data from trucks, routes, and traffic',
    duration: 2000,
  },
  [ControlLoopPhase.REASON]: {
    icon: Brain,
    color: 'purple',
    description: 'Analyzing data to identify issues and opportunities',
    duration: 3000,
  },
  [ControlLoopPhase.PLAN]: {
    icon: FileText,
    color: 'yellow',
    description: 'Generating scenarios and evaluating options',
    duration: 4000,
  },
  [ControlLoopPhase.DECIDE]: {
    icon: CheckCircle,
    color: 'green',
    description: 'Selecting optimal action based on analysis',
    duration: 1500,
  },
  [ControlLoopPhase.ACT]: {
    icon: Zap,
    color: 'red',
    description: 'Executing decisions and sending commands',
    duration: 2000,
  },
  [ControlLoopPhase.FEEDBACK]: {
    icon: RotateCcw,
    color: 'gray',
    description: 'Learning from outcomes and updating models',
    duration: 1500,
  },
};

type ColorKey = 'blue' | 'purple' | 'yellow' | 'green' | 'red' | 'gray';

const colorClasses: Record<ColorKey, {
  bg: string;
  text: string;
  border: string;
  ring: string;
}> = {
  blue: {
    bg: 'bg-blue-100',
    text: 'text-blue-600',
    border: 'border-blue-200',
    ring: 'ring-blue-500',
  },
  purple: {
    bg: 'bg-purple-100',
    text: 'text-purple-600',
    border: 'border-purple-200',
    ring: 'ring-purple-500',
  },
  yellow: {
    bg: 'bg-yellow-100',
    text: 'text-yellow-600',
    border: 'border-yellow-200',
    ring: 'ring-yellow-500',
  },
  green: {
    bg: 'bg-green-100',
    text: 'text-green-600',
    border: 'border-green-200',
    ring: 'ring-green-500',
  },
  red: {
    bg: 'bg-red-100',
    text: 'text-red-600',
    border: 'border-red-200',
    ring: 'ring-red-500',
  },
  gray: {
    bg: 'bg-gray-100',
    text: 'text-gray-600',
    border: 'border-gray-200',
    ring: 'ring-gray-500',
  },
};

const CycleVisualization: React.FC<CycleVisualizationProps> = ({
  currentPhase = ControlLoopPhase.OBSERVE,
  isRunning = false,
  cycleProgress = 0,
  onPhaseClick,
  className,
}) => {
  const [animatedPhase, setAnimatedPhase] = useState<ControlLoopPhase>(currentPhase);
  const [phaseProgress, setPhaseProgress] = useState(0);
  const [hoveredPhase, setHoveredPhase] = useState<ControlLoopPhase | null>(null);

  // Simulate phase progression
  useEffect(() => {
    if (!isRunning) return;

    const phases = Object.values(ControlLoopPhase);
    let currentIndex = phases.indexOf(animatedPhase);
    let progress = 0;

    const interval = setInterval(() => {
      progress += 2; // 2% per tick
      setPhaseProgress(progress);

      if (progress >= 100) {
        // Move to next phase
        currentIndex = (currentIndex + 1) % phases.length;
        setAnimatedPhase(phases[currentIndex]);
        progress = 0;
        setPhaseProgress(0);
      }
    }, 50); // Update every 50ms for smooth animation

    return () => clearInterval(interval);
  }, [isRunning, animatedPhase]);

  const phases = Object.values(ControlLoopPhase);
  const currentPhaseIndex = phases.indexOf(animatedPhase);

  return (
    <div className={className}>
      <Card>
        <Card.Header
          title="Control Loop Visualization"
          subtitle="Real-time cycle progression"
          action={
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1">
                <div className={cn(
                  'w-2 h-2 rounded-full',
                  isRunning ? 'bg-success-500 animate-pulse' : 'bg-gray-400'
                )} />
                <span className="text-sm text-gray-600">
                  {isRunning ? 'Running' : 'Stopped'}
                </span>
              </div>
            </div>
          }
        />

        <Card.Content>
          <div className="space-y-8">
            {/* Circular Progress Visualization */}
            <div className="flex justify-center">
              <div className="relative w-64 h-64">
                {/* Background Circle */}
                <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                  <circle
                    cx="50"
                    cy="50"
                    r="45"
                    fill="none"
                    stroke="#e5e7eb"
                    strokeWidth="2"
                  />
                  
                  {/* Progress Circle */}
                  <circle
                    cx="50"
                    cy="50"
                    r="45"
                    fill="none"
                    stroke="#3b82f6"
                    strokeWidth="3"
                    strokeDasharray={`${2 * Math.PI * 45}`}
                    strokeDashoffset={`${2 * Math.PI * 45 * (1 - phaseProgress / 100)}`}
                    className="transition-all duration-100 ease-linear"
                  />
                </svg>

                {/* Center Content */}
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <div className={cn(
                      'w-16 h-16 rounded-full flex items-center justify-center mb-2 mx-auto',
                      colorClasses[phaseConfig[animatedPhase].color].bg,
                      colorClasses[phaseConfig[animatedPhase].color].border,
                      'border-2'
                    )}>
                      {React.createElement(phaseConfig[animatedPhase].icon, {
                        className: cn('w-8 h-8', colorClasses[phaseConfig[animatedPhase].color].text)
                      })}
                    </div>
                    <div className="text-sm font-medium text-gray-900">
                      {PHASE_LABELS[animatedPhase]}
                    </div>
                    <div className="text-xs text-gray-500">
                      {Math.round(phaseProgress)}%
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Phase Description */}
            <div className="text-center">
              <p className="text-sm text-gray-600 max-w-md mx-auto">
                {hoveredPhase 
                  ? phaseConfig[hoveredPhase].description
                  : phaseConfig[animatedPhase].description
                }
              </p>
            </div>

            {/* Linear Phase Indicators */}
            <div className="space-y-4">
              <h4 className="text-sm font-medium text-gray-700">Cycle Phases</h4>
              
              <div className="grid grid-cols-1 gap-2">
                {phases.map((phase, index) => {
                  const config = phaseConfig[phase];
                  const colors = colorClasses[config.color];
                  const isActive = phase === animatedPhase;
                  const isCompleted = index < currentPhaseIndex;
                  const Icon = config.icon;

                  return (
                    <div
                      key={phase}
                      className={cn(
                        'flex items-center p-3 rounded-lg border transition-all cursor-pointer',
                        isActive 
                          ? `${colors.bg} ${colors.border} ring-2 ${colors.ring} ring-opacity-50`
                          : isCompleted
                          ? 'bg-success-50 border-success-200'
                          : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
                      )}
                      onClick={() => onPhaseClick?.(phase)}
                      onMouseEnter={() => setHoveredPhase(phase)}
                      onMouseLeave={() => setHoveredPhase(null)}
                    >
                      <div className={cn(
                        'p-2 rounded-lg mr-3',
                        isActive 
                          ? colors.bg
                          : isCompleted
                          ? 'bg-success-100'
                          : 'bg-gray-100'
                      )}>
                        <Icon className={cn(
                          'w-4 h-4',
                          isActive 
                            ? colors.text
                            : isCompleted
                            ? 'text-success-600'
                            : 'text-gray-400'
                        )} />
                      </div>

                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <span className={cn(
                            'text-sm font-medium',
                            isActive ? colors.text : 'text-gray-700'
                          )}>
                            {PHASE_LABELS[phase]}
                          </span>
                          
                          {isActive && (
                            <div className="flex items-center space-x-2">
                              <div className="w-16 bg-gray-200 rounded-full h-1">
                                <div
                                  className={cn('h-1 rounded-full transition-all duration-100', 
                                    `bg-${config.color}-500`
                                  )}
                                  style={{ width: `${phaseProgress}%` }}
                                />
                              </div>
                              <span className="text-xs text-gray-500 w-8">
                                {Math.round(phaseProgress)}%
                              </span>
                            </div>
                          )}
                        </div>
                        
                        <p className="text-xs text-gray-500 mt-1">
                          {config.description}
                        </p>
                      </div>

                      {index < phases.length - 1 && (
                        <ArrowRight className="w-4 h-4 text-gray-300 ml-2" />
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </Card.Content>
      </Card>
    </div>
  );
};

export default CycleVisualization;