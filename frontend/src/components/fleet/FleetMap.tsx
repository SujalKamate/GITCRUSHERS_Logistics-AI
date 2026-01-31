/**
 * Interactive fleet map component showing real-time truck positions and routes.
 */

'use client';

import React, { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import { cn } from '@/lib/utils';
import { MapProps, MapTruck, MapRoute, MapTrafficSegment } from '@/types';
import { TruckStatus, TrafficLevel } from '@/types';
import { STATUS_COLORS, TRAFFIC_COLORS, MAP_CONFIG } from '@/lib/constants';
import { Card, StatusBadge } from '@/components/ui';

// Fix for default markers in react-leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom truck icon based on status
const createTruckIcon = (status: TruckStatus, heading?: number) => {
  const color = STATUS_COLORS[status] || STATUS_COLORS[TruckStatus.IDLE];
  
  return L.divIcon({
    html: `
      <div style="
        width: 24px; 
        height: 24px; 
        background-color: ${color}; 
        border: 2px solid white; 
        border-radius: 50%; 
        display: flex; 
        align-items: center; 
        justify-content: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        transform: rotate(${heading || 0}deg);
      ">
        <span style="color: white; font-size: 12px;">🚛</span>
      </div>
    `,
    className: 'custom-truck-marker',
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });
};

// Component to handle map updates
const MapUpdater: React.FC<{ center: [number, number]; zoom: number }> = ({ center, zoom }) => {
  const map = useMap();
  
  useEffect(() => {
    map.setView(center, zoom);
  }, [map, center, zoom]);
  
  return null;
};

const FleetMap: React.FC<MapProps> = ({
  center = MAP_CONFIG.DEFAULT_CENTER,
  zoom = MAP_CONFIG.DEFAULT_ZOOM,
  height = '400px',
  trucks = [],
  routes = [],
  traffic = [],
  onTruckClick,
  onRouteClick,
  showControls = true,
  showTraffic = true,
  className,
}) => {
  const [selectedTruck, setSelectedTruck] = useState<string | null>(null);
  const [mapCenter, setMapCenter] = useState<[number, number]>(center);
  const [mapZoom, setMapZoom] = useState(zoom);

  // Handle truck marker click
  const handleTruckClick = (truck: MapTruck) => {
    setSelectedTruck(truck.id);
    onTruckClick?.(truck.id);
    
    // Center map on selected truck
    setMapCenter(truck.position);
    setMapZoom(Math.max(mapZoom, 12));
  };

  // Get route color based on traffic or truck status
  const getRouteColor = (route: MapRoute) => {
    if (route.color) return route.color;
    
    const truck = trucks.find(t => t.id === route.truckId);
    if (truck) {
      return STATUS_COLORS[truck.status] || STATUS_COLORS[TruckStatus.IDLE];
    }
    
    return '#3b82f6'; // Default blue
  };

  // Get traffic segment color
  const getTrafficColor = (level: TrafficLevel) => {
    return TRAFFIC_COLORS[level] || TRAFFIC_COLORS[TrafficLevel.FREE_FLOW];
  };

  return (
    <div className={cn('relative', className)}>
      <Card padding="none" className="overflow-hidden">
        <div style={{ height }}>
          <MapContainer
            center={mapCenter}
            zoom={mapZoom}
            style={{ height: '100%', width: '100%' }}
            zoomControl={showControls}
          >
            <MapUpdater center={mapCenter} zoom={mapZoom} />
            
            <TileLayer
              attribution={MAP_CONFIG.ATTRIBUTION}
              url={MAP_CONFIG.TILE_URL}
            />

            {/* Traffic Segments */}
            {showTraffic && traffic.map((segment) => (
              <Polyline
                key={segment.id}
                positions={segment.coordinates}
                color={getTrafficColor(segment.level)}
                weight={6}
                opacity={0.6}
              >
                <Popup>
                  <div className="p-2">
                    <h4 className="font-medium">Traffic Condition</h4>
                    <StatusBadge status={segment.level} size="sm" />
                    {segment.speed && (
                      <p className="text-sm mt-1">Speed: {segment.speed} km/h</p>
                    )}
                    {segment.incident && (
                      <p className="text-sm text-danger-600">{segment.incident}</p>
                    )}
                  </div>
                </Popup>
              </Polyline>
            ))}

            {/* Routes */}
            {routes.map((route) => (
              <Polyline
                key={route.id}
                positions={route.coordinates}
                color={getRouteColor(route)}
                weight={route.weight || 4}
                opacity={route.opacity || 0.8}
                eventHandlers={{
                  click: () => onRouteClick?.(route.id),
                }}
              >
                <Popup>
                  <div className="p-2">
                    <h4 className="font-medium">Route {route.id}</h4>
                    <p className="text-sm">Truck: {route.truckId}</p>
                  </div>
                </Popup>
              </Polyline>
            ))}

            {/* Truck Markers */}
            {trucks.map((truck) => (
              <Marker
                key={truck.id}
                position={truck.position}
                icon={createTruckIcon(truck.status, truck.heading)}
                eventHandlers={{
                  click: () => handleTruckClick(truck),
                }}
              >
                <Popup>
                  <div className="p-3 min-w-[200px]">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">{truck.name}</h4>
                      <StatusBadge status={truck.status} size="sm" />
                    </div>
                    
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Speed:</span>
                        <span>{truck.speed || 0} km/h</span>
                      </div>
                      
                      {truck.heading && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">Heading:</span>
                          <span>{truck.heading}°</span>
                        </div>
                      )}
                      
                      {truck.loadId && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">Load:</span>
                          <span className="text-primary-600">{truck.loadId}</span>
                        </div>
                      )}
                    </div>
                    
                    <div className="mt-3 pt-2 border-t border-gray-200">
                      <button
                        onClick={() => onTruckClick?.(truck.id)}
                        className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                      >
                        View Details →
                      </button>
                    </div>
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>

        {/* Map Controls */}
        {showControls && (
          <div className="absolute top-4 right-4 space-y-2">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-2">
              <div className="flex items-center space-x-2 text-sm">
                <span className="text-gray-600">Trucks:</span>
                <span className="font-medium">{trucks.length}</span>
              </div>
            </div>
            
            {showTraffic && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-2">
                <div className="text-xs text-gray-600 mb-1">Traffic</div>
                <div className="flex items-center space-x-1">
                  <div className="w-3 h-3 bg-success-500 rounded"></div>
                  <div className="w-3 h-3 bg-warning-500 rounded"></div>
                  <div className="w-3 h-3 bg-danger-500 rounded"></div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Legend */}
        <div className="absolute bottom-4 left-4 bg-white rounded-lg shadow-sm border border-gray-200 p-3">
          <div className="text-xs font-medium text-gray-700 mb-2">Status</div>
          <div className="space-y-1">
            {Object.values(TruckStatus).slice(0, 4).map((status) => (
              <div key={status} className="flex items-center space-x-2 text-xs">
                <div 
                  className="w-3 h-3 rounded-full border border-white"
                  style={{ backgroundColor: STATUS_COLORS[status] }}
                ></div>
                <span className="text-gray-600 capitalize">{status.replace('_', ' ')}</span>
              </div>
            ))}
          </div>
        </div>
      </Card>
    </div>
  );
};

export default FleetMap;