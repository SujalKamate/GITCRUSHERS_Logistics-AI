/**
 * Detailed truck information component with real-time updates.
 */

import React from 'react';
import { 
  MapPin, 
  Fuel, 
  Package, 
  Clock, 
  Navigation, 
  Gauge,
  User,
  Calendar,
  TrendingUp
} from 'lucide-react';
import { Truck, TruckStatus } from '@/types';
import { 
  formatDistance, 
  formatPercentage, 
  formatRelativeTime, 
  formatDate 
} from '@/lib/utils';
import { Card, StatusBadge, Button } from '@/components/ui';

interface TruckDetailProps {
  truck: Truck;
  onClose?: () => void;
  onEdit?: () => void;
  onTrack?: () => void;
  className?: string;
}

const TruckDetail: React.FC<TruckDetailProps> = ({
  truck,
  onClose,
  onEdit,
  onTrack,
  className,
}) => {
  const lastUpdate = truck.last_gps_reading?.timestamp;
  const isOnline = lastUpdate && 
    new Date().getTime() - new Date(lastUpdate).getTime() < 5 * 60 * 1000; // 5 minutes

  return (
    <div className={className}>
      <Card>
        <Card.Header
          title={truck.name}
          subtitle={`ID: ${truck.id}`}
          action={
            <div className="flex space-x-2">
              {onTrack && (
                <Button variant="primary" size="sm" onClick={onTrack}>
                  <MapPin className="w-4 h-4 mr-1" />
                  Track
                </Button>
              )}
              {onEdit && (
                <Button variant="outline" size="sm" onClick={onEdit}>
                  Edit
                </Button>
              )}
              {onClose && (
                <Button variant="ghost" size="sm" onClick={onClose}>
                  ×
                </Button>
              )}
            </div>
          }
        />

        <Card.Content>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Status & Location */}
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Current Status</h4>
                <div className="flex items-center space-x-3">
                  <StatusBadge status={truck.status} size="lg" />
                  <div className="flex items-center space-x-1">
                    <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-success-500' : 'bg-gray-400'}`}></div>
                    <span className="text-sm text-gray-600">
                      {isOnline ? 'Online' : 'Offline'}
                    </span>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Location</h4>
                {truck.current_location ? (
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <MapPin className="w-4 h-4 text-gray-400" />
                      <span className="text-sm text-gray-900">
                        {truck.current_location.latitude.toFixed(6)}, {truck.current_location.longitude.toFixed(6)}
                      </span>
                    </div>
                    {truck.current_location.address && (
                      <p className="text-sm text-gray-600 ml-6">
                        {truck.current_location.address}
                      </p>
                    )}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">Location unknown</p>
                )}
              </div>

              {truck.last_gps_reading && (
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Movement</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex items-center space-x-2">
                      <Gauge className="w-4 h-4 text-gray-400" />
                      <div>
                        <p className="text-sm text-gray-600">Speed</p>
                        <p className="font-medium">{truck.last_gps_reading.speed_kmh} km/h</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Navigation className="w-4 h-4 text-gray-400" />
                      <div>
                        <p className="text-sm text-gray-600">Heading</p>
                        <p className="font-medium">{truck.last_gps_reading.heading}°</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Vehicle Info */}
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Vehicle Information</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Fuel className="w-4 h-4 text-gray-400" />
                      <span className="text-sm text-gray-600">Fuel Level</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium">
                        {formatPercentage(truck.fuel_level_percent)}
                      </span>
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            truck.fuel_level_percent > 50 
                              ? 'bg-success-500' 
                              : truck.fuel_level_percent > 25 
                              ? 'bg-warning-500' 
                              : 'bg-danger-500'
                          }`}
                          style={{ width: `${truck.fuel_level_percent}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Package className="w-4 h-4 text-gray-400" />
                      <span className="text-sm text-gray-600">Capacity</span>
                    </div>
                    <span className="text-sm font-medium">
                      {(truck.capacity_kg / 1000).toFixed(1)}t
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Package className="w-4 h-4 text-gray-400" />
                      <span className="text-sm text-gray-600">Current Load</span>
                    </div>
                    <span className="text-sm font-medium">
                      {truck.current_load_id || 'None'}
                    </span>
                  </div>

                  {truck.driver_id && (
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <User className="w-4 h-4 text-gray-400" />
                        <span className="text-sm text-gray-600">Driver</span>
                      </div>
                      <span className="text-sm font-medium">{truck.driver_id}</span>
                    </div>
                  )}
                </div>
              </div>

              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Performance</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center space-x-2">
                    <TrendingUp className="w-4 h-4 text-gray-400" />
                    <div>
                      <p className="text-sm text-gray-600">Total Distance</p>
                      <p className="font-medium">{formatDistance(truck.total_distance_km)}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Package className="w-4 h-4 text-gray-400" />
                    <div>
                      <p className="text-sm text-gray-600">Deliveries</p>
                      <p className="font-medium">{truck.total_deliveries}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Last Update */}
          {lastUpdate && (
            <div className="mt-6 pt-4 border-t border-gray-200">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-2 text-gray-600">
                  <Clock className="w-4 h-4" />
                  <span>Last updated: {formatRelativeTime(lastUpdate)}</span>
                </div>
                <span className="text-gray-500">
                  {formatDate(lastUpdate)}
                </span>
              </div>
            </div>
          )}
        </Card.Content>
      </Card>
    </div>
  );
};

export default TruckDetail;