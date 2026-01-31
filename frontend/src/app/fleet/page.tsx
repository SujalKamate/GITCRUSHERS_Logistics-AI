/**
 * Fleet Management page with map and list views.
 */

'use client';

import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { Map, List, Truck as TruckIcon } from 'lucide-react';
import { DashboardLayout } from '@/components/layout';
import { Card, Button, LoadingSpinner } from '@/components/ui';
import { TruckList, TruckDetail } from '@/components/fleet';
import { Truck, TruckStatus, MapTruck } from '@/types';

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

// Mock data for demonstration
const mockTrucks: Truck[] = [
  {
    id: 'TRK-001',
    name: 'Alpha Express',
    status: TruckStatus.EN_ROUTE,
    current_location: {
      latitude: 40.7589,
      longitude: -73.9851,
      address: 'Times Square, New York, NY',
    },
    current_load_id: 'LOAD-123',
    driver_id: 'DRV-001',
    capacity_kg: 15000,
    fuel_level_percent: 75,
    last_gps_reading: {
      truck_id: 'TRK-001',
      timestamp: new Date(Date.now() - 2 * 60 * 1000).toISOString(), // 2 minutes ago
      location: {
        latitude: 40.7589,
        longitude: -73.9851,
      },
      speed_kmh: 45,
      heading: 90,
      accuracy_meters: 5,
    },
    total_distance_km: 12450,
    total_deliveries: 89,
  },
  {
    id: 'TRK-002',
    name: 'Beta Logistics',
    status: TruckStatus.LOADING,
    current_location: {
      latitude: 40.7505,
      longitude: -73.9934,
      address: 'Chelsea Market, New York, NY',
    },
    driver_id: 'DRV-002',
    capacity_kg: 12000,
    fuel_level_percent: 45,
    last_gps_reading: {
      truck_id: 'TRK-002',
      timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(), // 5 minutes ago
      location: {
        latitude: 40.7505,
        longitude: -73.9934,
      },
      speed_kmh: 0,
      heading: 180,
      accuracy_meters: 3,
    },
    total_distance_km: 8920,
    total_deliveries: 67,
  },
  {
    id: 'TRK-003',
    name: 'Gamma Transport',
    status: TruckStatus.STUCK,
    current_location: {
      latitude: 40.7282,
      longitude: -74.0776,
      address: 'Holland Tunnel, New York, NY',
    },
    current_load_id: 'LOAD-456',
    driver_id: 'DRV-003',
    capacity_kg: 18000,
    fuel_level_percent: 20,
    last_gps_reading: {
      truck_id: 'TRK-003',
      timestamp: new Date(Date.now() - 1 * 60 * 1000).toISOString(), // 1 minute ago
      location: {
        latitude: 40.7282,
        longitude: -74.0776,
      },
      speed_kmh: 0,
      heading: 270,
      accuracy_meters: 8,
    },
    total_distance_km: 15670,
    total_deliveries: 102,
  },
  {
    id: 'TRK-004',
    name: 'Delta Freight',
    status: TruckStatus.IDLE,
    current_location: {
      latitude: 40.7831,
      longitude: -73.9712,
      address: 'Central Park, New York, NY',
    },
    driver_id: 'DRV-004',
    capacity_kg: 10000,
    fuel_level_percent: 90,
    last_gps_reading: {
      truck_id: 'TRK-004',
      timestamp: new Date(Date.now() - 10 * 60 * 1000).toISOString(), // 10 minutes ago
      location: {
        latitude: 40.7831,
        longitude: -73.9712,
      },
      speed_kmh: 0,
      heading: 0,
      accuracy_meters: 2,
    },
    total_distance_km: 6780,
    total_deliveries: 45,
  },
];

const FleetPage: React.FC = () => {
  const [viewMode, setViewMode] = useState<'map' | 'list'>('map');
  const [selectedTruck, setSelectedTruck] = useState<Truck | null>(null);
  const [trucks, setTrucks] = useState<Truck[]>(mockTrucks);
  const [loading, setLoading] = useState(false);

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
  const handleTruckSelect = (truckId: string) => {
    const truck = trucks.find(t => t.id === truckId);
    setSelectedTruck(truck || null);
  };

  // Handle truck selection from list
  const handleTruckSelectFromList = (truck: Truck) => {
    setSelectedTruck(truck);
    setViewMode('map'); // Switch to map view to show selected truck
  };

  // Mock real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setTrucks(prevTrucks => 
        prevTrucks.map(truck => {
          // Simulate small position changes for moving trucks
          if (truck.status === TruckStatus.EN_ROUTE && truck.current_location) {
            const latChange = (Math.random() - 0.5) * 0.001; // Small random change
            const lngChange = (Math.random() - 0.5) * 0.001;
            
            return {
              ...truck,
              current_location: {
                ...truck.current_location,
                latitude: truck.current_location.latitude + latChange,
                longitude: truck.current_location.longitude + lngChange,
              },
              last_gps_reading: truck.last_gps_reading ? {
                ...truck.last_gps_reading,
                timestamp: new Date().toISOString(),
                location: {
                  latitude: truck.current_location.latitude + latChange,
                  longitude: truck.current_location.longitude + lngChange,
                },
                speed_kmh: 30 + Math.random() * 40, // Random speed between 30-70
              } : undefined,
            };
          }
          return truck;
        })
      );
    }, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, []);

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
                <p className="text-sm text-gray-600">Total Trucks</p>
                <p className="text-xl font-semibold">{trucks.length}</p>
              </div>
            </div>
          </Card>

          <Card padding="sm">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-success-100 rounded-lg">
                <TruckIcon className="w-5 h-5 text-success-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">En Route</p>
                <p className="text-xl font-semibold">
                  {trucks.filter(t => t.status === TruckStatus.EN_ROUTE).length}
                </p>
              </div>
            </div>
          </Card>

          <Card padding="sm">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-warning-100 rounded-lg">
                <TruckIcon className="w-5 h-5 text-warning-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Loading</p>
                <p className="text-xl font-semibold">
                  {trucks.filter(t => t.status === TruckStatus.LOADING).length}
                </p>
              </div>
            </div>
          </Card>

          <Card padding="sm">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-danger-100 rounded-lg">
                <TruckIcon className="w-5 h-5 text-danger-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Issues</p>
                <p className="text-xl font-semibold">
                  {trucks.filter(t => t.status === TruckStatus.STUCK || t.status === TruckStatus.DELAYED).length}
                </p>
              </div>
            </div>
          </Card>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          {/* Map/List View */}
          <div className="xl:col-span-2">
            {viewMode === 'map' ? (
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