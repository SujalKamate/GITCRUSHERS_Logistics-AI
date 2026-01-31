/**
 * Fleet Management page with map and list views.
 */

'use client';

import React, { useState, useEffect, useCallback } from 'react';
import dynamic from 'next/dynamic';
import { Map, List, Truck as TruckIcon, RefreshCw } from 'lucide-react';
import { DashboardLayout } from '@/components/layout';
import { Card, Button, LoadingSpinner } from '@/components/ui';
import { TruckList, TruckDetail } from '@/components/fleet';
import { Truck, TruckStatus, MapTruck } from '@/types';
import { useFleetStatus } from '@/lib/hooks/useApi';
import { WS_BASE_URL } from '@/lib/constants';

// Dynamically import FleetMap to avoid SSR issues with Leaflet
const FleetMap = dynamic(
  () => import('@/components/fleet/FleetMap'),
  {
    ssr: false,
    loading: () => (
      <div className="h-96 flex items-center justify-center bg-gray-100 rounded-lg">
        <LoadingSpinner text="Loading map..." />
      </div>
    )
  }
);

const FleetPage: React.FC = () => {
  const [viewMode, setViewMode] = useState<'map' | 'list'>('map');
  const [selectedTruck, setSelectedTruck] = useState<Truck | null>(null);

  // Fetch fleet data from API
  const { data: fleetStatus, loading, error, refetch } = useFleetStatus();

  // Extract trucks from API response
  const trucks: Truck[] = fleetStatus?.trucks ?? [];

  // WebSocket connection for real-time updates
  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimeout: NodeJS.Timeout;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 5;

    const connect = () => {
      // Don't try to reconnect if we've exceeded max attempts
      if (reconnectAttempts >= maxReconnectAttempts) {
        console.log('Max WebSocket reconnection attempts reached. Falling back to polling.');
        return;
      }

      try {
        console.log(`Attempting WebSocket connection (attempt ${reconnectAttempts + 1}/${maxReconnectAttempts})`);
        ws = new WebSocket(`${WS_BASE_URL}/ws`);

        ws.onopen = () => {
          console.log('Fleet WebSocket connected');
          reconnectAttempts = 0; // Reset attempts on successful connection
          // Subscribe to truck location updates
          ws?.send(JSON.stringify({
            type: 'subscribe',
            events: ['truck_location_update', 'truck_status_update']
          }));
        };

        ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            if (message.type === 'truck_location_update') {
              // Refetch to get updated data
              // In a production app, you'd update state directly
              refetch();
            }
          } catch (e) {
            console.error('Failed to parse WebSocket message:', e);
          }
        };

        ws.onclose = (event) => {
          console.log(`WebSocket disconnected (code: ${event.code}, reason: ${event.reason})`);
          if (reconnectAttempts < maxReconnectAttempts) {
            reconnectAttempts++;
            const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 10000); // Exponential backoff
            console.log(`Reconnecting in ${delay}ms...`);
            reconnectTimeout = setTimeout(connect, delay);
          }
        };

        ws.onerror = (error) => {
          console.warn('WebSocket connection failed - this is normal if the backend server is not running');
          console.debug('WebSocket error details:', error);
        };
      } catch (e) {
        console.warn('WebSocket connection failed - this is normal if the backend server is not running');
        console.debug('WebSocket connection error:', e);
        reconnectAttempts++;
        if (reconnectAttempts < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 10000);
          reconnectTimeout = setTimeout(connect, delay);
        }
      }
    };

    // Only attempt WebSocket connection if WS_BASE_URL is configured
    if (WS_BASE_URL && WS_BASE_URL !== 'ws://localhost:8000') {
      connect();
    } else {
      console.log('WebSocket URL not configured or using default. Skipping WebSocket connection.');
    }

    return () => {
      if (ws) {
        ws.close();
      }
      clearTimeout(reconnectTimeout);
    };
  }, [refetch]);

  // Convert trucks to map format
  const mapTrucks: MapTruck[] = trucks.map(truck => ({
    id: truck.id,
    name: truck.name,
    position: truck.current_location
      ? [truck.current_location.latitude, truck.current_location.longitude]
      : [40.7128, -74.0060], // Default to NYC
    status: truck.status,
    heading: truck.last_gps_reading?.heading,
    speed: truck.last_gps_reading?.speed_kmh,
    loadId: truck.current_load_id,
  }));

  // Handle truck selection
  const handleTruckSelect = useCallback((truckId: string) => {
    const truck = trucks.find(t => t.id === truckId);
    setSelectedTruck(truck || null);
  }, [trucks]);

  // Handle truck selection from list
  const handleTruckSelectFromList = useCallback((truck: Truck) => {
    setSelectedTruck(truck);
    setViewMode('map'); // Switch to map view to show selected truck
  }, []);

  // Calculate stats
  const stats = {
    total: trucks.length,
    enRoute: trucks.filter(t => t.status === TruckStatus.EN_ROUTE).length,
    loading: trucks.filter(t => t.status === TruckStatus.LOADING).length,
    issues: trucks.filter(t => t.status === TruckStatus.STUCK || t.status === TruckStatus.DELAYED).length,
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Fleet Management</h1>
            <p className="text-gray-600">Monitor and manage your truck fleet in real-time</p>
          </div>

          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => refetch()}
              icon={<RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />}
              disabled={loading}
            >
              Refresh
            </Button>
            <Button
              variant={viewMode === 'map' ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setViewMode('map')}
              icon={<Map className="w-4 h-4" />}
            >
              Map View
            </Button>
            <Button
              variant={viewMode === 'list' ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setViewMode('list')}
              icon={<List className="w-4 h-4" />}
            >
              List View
            </Button>
          </div>
        </div>

        {/* Fleet Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card padding="sm">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-primary-100 rounded-lg">
                <TruckIcon className="w-5 h-5 text-primary-600" />
              </div>
              <div>
                <div className="text-sm text-gray-600">Total Trucks</div>
                <div className="text-xl font-semibold">
                  {loading ? <LoadingSpinner size="sm" /> : stats.total}
                </div>
              </div>
            </div>
          </Card>

          <Card padding="sm">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-success-100 rounded-lg">
                <TruckIcon className="w-5 h-5 text-success-600" />
              </div>
              <div>
                <div className="text-sm text-gray-600">En Route</div>
                <div className="text-xl font-semibold">
                  {loading ? <LoadingSpinner size="sm" /> : stats.enRoute}
                </div>
              </div>
            </div>
          </Card>

          <Card padding="sm">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-warning-100 rounded-lg">
                <TruckIcon className="w-5 h-5 text-warning-600" />
              </div>
              <div>
                <div className="text-sm text-gray-600">Loading</div>
                <div className="text-xl font-semibold">
                  {loading ? <LoadingSpinner size="sm" /> : stats.loading}
                </div>
              </div>
            </div>
          </Card>

          <Card padding="sm">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-danger-100 rounded-lg">
                <TruckIcon className="w-5 h-5 text-danger-600" />
              </div>
              <div>
                <div className="text-sm text-gray-600">Issues</div>
                <div className="text-xl font-semibold">
                  {loading ? <LoadingSpinner size="sm" /> : stats.issues}
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Error State */}
        {error && (
          <Card className="border-danger-200 bg-danger-50">
            <div className="p-4 text-danger-700">
              Failed to load fleet data: {error}
              <Button
                variant="outline"
                size="sm"
                className="ml-4"
                onClick={() => refetch()}
              >
                Retry
              </Button>
            </div>
          </Card>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          {/* Map/List View */}
          <div className="xl:col-span-2">
            {loading && trucks.length === 0 ? (
              <Card>
                <div className="h-96 flex items-center justify-center">
                  <LoadingSpinner text="Loading fleet data..." />
                </div>
              </Card>
            ) : viewMode === 'map' ? (
              <FleetMap
                trucks={mapTrucks}
                height="600px"
                onTruckClick={handleTruckSelect}
                showControls={true}
                showTraffic={true}
              />
            ) : (
              <TruckList
                trucks={trucks}
                loading={loading}
                onTruckSelect={handleTruckSelectFromList}
              />
            )}
          </div>

          {/* Truck Detail Sidebar */}
          <div className="xl:col-span-1">
            {selectedTruck ? (
              <TruckDetail
                truck={selectedTruck}
                onClose={() => setSelectedTruck(null)}
                onTrack={() => {
                  setViewMode('map');
                  // Map will automatically center on selected truck
                }}
              />
            ) : (
              <Card>
                <Card.Content>
                  <div className="text-center py-8">
                    <TruckIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      Select a Truck
                    </h3>
                    <p className="text-gray-600">
                      Click on a truck marker or row to view detailed information
                    </p>
                  </div>
                </Card.Content>
              </Card>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default FleetPage;
