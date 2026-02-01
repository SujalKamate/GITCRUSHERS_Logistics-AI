/**
 * Connection Test Component
 * Tests API connectivity and displays status
 */

'use client';

import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '@/lib/constants';

interface ConnectionStatus {
  api: 'connecting' | 'connected' | 'error';
  websocket: 'connecting' | 'connected' | 'error';
  lastCheck: string;
  error?: string;
}

const ConnectionTest: React.FC = () => {
  const [status, setStatus] = useState<ConnectionStatus>({
    api: 'connecting',
    websocket: 'connecting',
    lastCheck: new Date().toISOString()
  });
  const [mounted, setMounted] = useState(false);

  // Fix hydration issue by only rendering time after component mounts
  useEffect(() => {
    setMounted(true);
  }, []);

  const testApiConnection = async () => {
    try {
      console.log('Testing API connection to:', API_BASE_URL);
      const response = await fetch(`${API_BASE_URL}/health`);
      
      if (response.ok) {
        setStatus(prev => ({ ...prev, api: 'connected', lastCheck: new Date().toISOString() }));
        console.log('API connection successful');
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error('API connection failed:', error);
      setStatus(prev => ({ 
        ...prev, 
        api: 'error', 
        error: error instanceof Error ? error.message : 'Unknown error',
        lastCheck: new Date().toISOString()
      }));
    }
  };

  const testWebSocketConnection = () => {
    try {
      const ws = new WebSocket(`ws://localhost:8000/ws`);
      
      ws.onopen = () => {
        setStatus(prev => ({ ...prev, websocket: 'connected' }));
        ws.close();
      };
      
      ws.onerror = () => {
        setStatus(prev => ({ ...prev, websocket: 'error' }));
      };
      
      ws.onclose = () => {
        // Connection test complete
      };
    } catch (error) {
      setStatus(prev => ({ ...prev, websocket: 'error' }));
    }
  };

  useEffect(() => {
    if (mounted) {
      testApiConnection();
      testWebSocketConnection();
      
      // Test every 30 seconds
      const interval = setInterval(() => {
        testApiConnection();
        testWebSocketConnection();
      }, 30000);
      
      return () => clearInterval(interval);
    }
  }, [mounted]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'text-green-600 bg-green-100';
      case 'connecting': return 'text-yellow-600 bg-yellow-100';
      case 'error': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected': return '✅';
      case 'connecting': return '🔄';
      case 'error': return '❌';
      default: return '❓';
    }
  };

  // Don't render until mounted to avoid hydration mismatch
  if (!mounted) {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 bg-white border border-gray-200 rounded-lg shadow-lg p-4 min-w-[250px]">
      <h3 className="font-medium text-gray-900 mb-3">Connection Status</h3>
      
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">API Server:</span>
          <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(status.api)}`}>
            {getStatusIcon(status.api)} {status.api}
          </span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">WebSocket:</span>
          <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(status.websocket)}`}>
            {getStatusIcon(status.websocket)} {status.websocket}
          </span>
        </div>
      </div>
      
      {status.error && (
        <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
          Error: {status.error}
        </div>
      )}
      
      <div className="mt-3 pt-2 border-t border-gray-200">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>API URL:</span>
          <span className="font-mono">{API_BASE_URL}</span>
        </div>
        <div className="flex items-center justify-between text-xs text-gray-500 mt-1">
          <span>Last Check:</span>
          <span>{new Date(status.lastCheck).toLocaleTimeString()}</span>
        </div>
      </div>
      
      <button
        onClick={() => {
          testApiConnection();
          testWebSocketConnection();
        }}
        className="mt-3 w-full px-3 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600 transition-colors"
      >
        Test Connection
      </button>
    </div>
  );
};

export default ConnectionTest;