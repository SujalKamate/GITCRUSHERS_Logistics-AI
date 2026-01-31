/**
 * Simple connection status indicator component.
 */

import React from 'react';

interface ConnectionStatusProps {
  isConnected: boolean;
  isConnecting: boolean;
  error?: string | null;
  className?: string;
  showText?: boolean;
}

const ConnectionStatus: React.FC<ConnectionStatusProps> = ({
  isConnected,
  isConnecting,
  error,
  className = '',
  showText = false
}) => {
  let statusText = 'Disconnected';
  let statusColor = 'bg-gray-400';
  
  if (isConnecting) {
    statusText = 'Connecting...';
    statusColor = 'bg-yellow-400';
  } else if (isConnected) {
    statusText = 'Connected';
    statusColor = 'bg-green-400';
  }

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <div className={`w-3 h-3 rounded-full ${statusColor}`}></div>
      {showText && (
        <span className="text-xs font-medium text-gray-600">
          {statusText}
        </span>
      )}
    </div>
  );
};

export default ConnectionStatus;