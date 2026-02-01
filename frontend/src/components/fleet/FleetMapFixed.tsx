/**
 * Fixed fleet map component that properly handles Leaflet initialization.
 * Enhanced with journey tracking for delivery requests.
 */

'use client';

import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { cn } from '@/lib/utils';
import { MapProps, MapTruck, MapRoute, MapTrafficSegment } from '@/types';
import { TruckStatus, TrafficLevel } from '@/types';
import { STATUS_COLORS, TRAFFIC_COLORS, MAP_CONFIG } from '@/lib/constants';
import { Card, StatusBadge } from '@/components/ui';

// Journey tracking types
interface JourneySegment {
  id: string;
  truckId: string;
  type: 'to_pickup' | 'to_delivery';
  coordinates: [number, number][];
  color: string;
  status: 'pending' | 'active' | 'completed';
}

interface DeliveryMarker {
  id: string;
  type: 'pickup' | 'delivery';
  position: [number, number];
  address: string;
  requestId: string;
  customerName: string;
  status: 'pending' | 'active' | 'completed';
}

// Fix for default markers in Leaflet
if (typeof window !== 'undefined') {
  delete (L.Icon.Default.prototype as any)._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  });
}

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

// Custom pickup/delivery markers
const createDeliveryIcon = (type: 'pickup' | 'delivery', status: 'pending' | 'active' | 'completed') => {
  const colors = {
    pickup: { pending: '#f59e0b', active: '#3b82f6', completed: '#10b981' },
    delivery: { pending: '#ef4444', active: '#8b5cf6', completed: '#10b981' }
  };
  
  const icons = {
    pickup: '📦',
    delivery: '🏠'
  };
  
  const color = colors[type][status];
  
  return L.divIcon({
    html: `
      <div style="
        width: 20px; 
        height: 20px; 
        background-color: ${color}; 
        border: 2px solid white; 
        border-radius: 50%; 
        display: flex; 
        align-items: center; 
        justify-content: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
      ">
        <span style="font-size: 10px;">${icons[type]}</span>
      </div>
    `,
    className: 'custom-delivery-marker',
    iconSize: [20, 20],
    iconAnchor: [10, 10],
  });
};

const FleetMapFixed: React.FC<MapProps & {
  journeySegments?: JourneySegment[];
  deliveryMarkers?: DeliveryMarker[];
  showJourneys?: boolean;
}> = ({
  center = MAP_CONFIG.DEFAULT_CENTER,
  zoom = MAP_CONFIG.DEFAULT_ZOOM,
  height = '400px',
  trucks = [],
  routes = [],
  traffic = [],
  journeySegments = [],
  deliveryMarkers = [],
  showJourneys = true,
  onTruckClick,
  onRouteClick,
  showControls = true,
  showTraffic = true,
  className,
}) => {
  const mapRef = useRef<L.Map | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const markersRef = useRef<L.Marker[]>([]);
  const routesRef = useRef<L.Polyline[]>([]);
  const trafficRef = useRef<L.Polyline[]>([]);
  const journeyRef = useRef<L.Polyline[]>([]);
  const deliveryMarkersRef = useRef<L.Marker[]>([]);

  const [selectedTruck, setSelectedTruck] = useState<string | null>(null);

  // Initialize map
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    // Create map instance
    mapRef.current = L.map(containerRef.current, {
      center: center,
      zoom: zoom,
      zoomControl: showControls,
    });

    // Add tile layer
    L.tileLayer(MAP_CONFIG.TILE_URL, {
      attribution: MAP_CONFIG.ATTRIBUTION,
    }).addTo(mapRef.current);

    return () => {
      // Cleanup map instance
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, [center, zoom, showControls]);

  // Update map view when center/zoom changes
  useEffect(() => {
    if (mapRef.current) {
      mapRef.current.setView(center, zoom);
    }
  }, [center, zoom]);

  // Update truck markers
  useEffect(() => {
    if (!mapRef.current) return;

    // Clear existing markers
    markersRef.current.forEach(marker => {
      mapRef.current?.removeLayer(marker);
    });
    markersRef.current = [];

    // Add new markers
    trucks.forEach(truck => {
      const marker = L.marker(truck.position, {
        icon: createTruckIcon(truck.status, truck.heading)
      });

      // Create popup content
      const popupContent = `
        <div class="p-3 min-w-[200px]">
          <div class="flex items-center justify-between mb-2">
            <h4 class="font-medium">${truck.name}</h4>
            <span class="px-2 py-1 text-xs rounded-full bg-${STATUS_COLORS[truck.status]?.replace('#', '')}-100 text-${STATUS_COLORS[truck.status]?.replace('#', '')}-800">
              ${truck.status.replace('_', ' ')}
            </span>
          </div>
          <div class="space-y-1 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-600">Speed:</span>
              <span>${truck.speed || 0} km/h</span>
            </div>
            ${truck.heading ? `
              <div class="flex justify-between">
                <span class="text-gray-600">Heading:</span>
                <span>${truck.heading}°</span>
              </div>
            ` : ''}
            ${truck.loadId ? `
              <div class="flex justify-between">
                <span class="text-gray-600">Load:</span>
                <span class="text-primary-600">${truck.loadId}</span>
              </div>
            ` : ''}
          </div>
          <div class="mt-3 pt-2 border-t border-gray-200">
            <button onclick="window.selectTruck?.('${truck.id}')" class="text-primary-600 hover:text-primary-700 text-sm font-medium">
              View Details →
            </button>
          </div>
        </div>
      `;

      marker.bindPopup(popupContent);
      
      marker.on('click', () => {
        setSelectedTruck(truck.id);
        onTruckClick?.(truck.id);
      });

      marker.addTo(mapRef.current!);
      markersRef.current.push(marker);
    });

    // Set up global truck selection function
    (window as any).selectTruck = (truckId: string) => {
      setSelectedTruck(truckId);
      onTruckClick?.(truckId);
    };

    return () => {
      delete (window as any).selectTruck;
    };
  }, [trucks, onTruckClick]);

  // Update routes
  useEffect(() => {
    if (!mapRef.current) return;

    // Clear existing routes
    routesRef.current.forEach(route => {
      mapRef.current?.removeLayer(route);
    });
    routesRef.current = [];

    // Add new routes
    routes.forEach(route => {
      const color = route.color || STATUS_COLORS[TruckStatus.EN_ROUTE] || '#3b82f6';
      const polyline = L.polyline(route.coordinates, {
        color: color,
        weight: route.weight || 4,
        opacity: route.opacity || 0.8,
      });

      polyline.bindPopup(`
        <div class="p-2">
          <h4 class="font-medium">Route ${route.id}</h4>
          <p class="text-sm">Truck: ${route.truckId}</p>
        </div>
      `);

      polyline.on('click', () => {
        onRouteClick?.(route.id);
      });

      polyline.addTo(mapRef.current!);
      routesRef.current.push(polyline);
    });
  }, [routes, onRouteClick]);

  // Update traffic
  useEffect(() => {
    if (!mapRef.current || !showTraffic) return;

    // Clear existing traffic
    trafficRef.current.forEach(segment => {
      mapRef.current?.removeLayer(segment);
    });
    trafficRef.current = [];

    // Add new traffic segments
    traffic.forEach(segment => {
      const color = TRAFFIC_COLORS[segment.level] || TRAFFIC_COLORS[TrafficLevel.FREE_FLOW];
      const polyline = L.polyline(segment.coordinates, {
        color: color,
        weight: 6,
        opacity: 0.6,
      });

      polyline.bindPopup(`
        <div class="p-2">
          <h4 class="font-medium">Traffic Condition</h4>
          <p class="text-sm">Level: ${segment.level}</p>
          ${segment.speed ? `<p class="text-sm">Speed: ${segment.speed} km/h</p>` : ''}
          ${segment.incident ? `<p class="text-sm text-red-600">${segment.incident}</p>` : ''}
        </div>
      `);

      polyline.addTo(mapRef.current!);
      trafficRef.current.push(polyline);
    });
  }, [traffic, showTraffic]);

  // Update journey segments
  useEffect(() => {
    if (!mapRef.current || !showJourneys) return;

    // Clear existing journey segments
    journeyRef.current.forEach(segment => {
      mapRef.current?.removeLayer(segment);
    });
    journeyRef.current = [];

    // Add new journey segments
    journeySegments.forEach(segment => {
      const polyline = L.polyline(segment.coordinates, {
        color: segment.color,
        weight: 4,
        opacity: segment.status === 'active' ? 0.9 : 0.6,
        dashArray: segment.status === 'pending' ? '10, 5' : undefined,
      });

      const segmentTypeLabel = segment.type === 'to_pickup' ? 'To Pickup' : 'To Delivery';
      polyline.bindPopup(`
        <div class="p-3 min-w-[200px]">
          <h4 class="font-medium">Journey Segment</h4>
          <div class="space-y-1 text-sm mt-2">
            <div class="flex justify-between">
              <span class="text-gray-600">Truck:</span>
              <span>${segment.truckId}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Type:</span>
              <span>${segmentTypeLabel}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Status:</span>
              <span class="capitalize">${segment.status}</span>
            </div>
          </div>
        </div>
      `);

      polyline.addTo(mapRef.current!);
      journeyRef.current.push(polyline);
    });
  }, [journeySegments, showJourneys]);

  // Update delivery markers
  useEffect(() => {
    if (!mapRef.current) return;

    // Clear existing delivery markers
    deliveryMarkersRef.current.forEach(marker => {
      mapRef.current?.removeLayer(marker);
    });
    deliveryMarkersRef.current = [];

    // Add new delivery markers
    deliveryMarkers.forEach(marker => {
      const leafletMarker = L.marker(marker.position, {
        icon: createDeliveryIcon(marker.type, marker.status)
      });

      const typeLabel = marker.type === 'pickup' ? 'Pickup Location' : 'Delivery Location';
      leafletMarker.bindPopup(`
        <div class="p-3 min-w-[200px]">
          <h4 class="font-medium">${typeLabel}</h4>
          <div class="space-y-1 text-sm mt-2">
            <div class="flex justify-between">
              <span class="text-gray-600">Request:</span>
              <span>${marker.requestId}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Customer:</span>
              <span>${marker.customerName}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Status:</span>
              <span class="capitalize">${marker.status}</span>
            </div>
            <div class="mt-2 pt-2 border-t border-gray-200">
              <p class="text-xs text-gray-600">${marker.address}</p>
            </div>
          </div>
        </div>
      `);

      leafletMarker.addTo(mapRef.current!);
      deliveryMarkersRef.current.push(leafletMarker);
    });
  }, [deliveryMarkers]);

  return (
    <div className={cn('relative', className)}>
      <Card padding="none" className="overflow-hidden">
        <div 
          ref={containerRef}
          style={{ height }}
          className="w-full"
        />

        {/* Map Controls */}
        {showControls && (
          <div className="absolute top-4 right-4 space-y-2">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-2">
              <div className="flex items-center space-x-2 text-sm">
                <span className="text-gray-600">Trucks:</span>
                <span className="font-medium">{trucks.length}</span>
              </div>
            </div>
            
            {showJourneys && journeySegments.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-2">
                <div className="text-xs text-gray-600 mb-1">Active Journeys</div>
                <div className="text-sm font-medium">{journeySegments.filter(j => j.status === 'active').length}</div>
              </div>
            )}
            
            {showTraffic && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-2">
                <div className="text-xs text-gray-600 mb-1">Traffic</div>
                <div className="flex items-center space-x-1">
                  <div className="w-3 h-3 bg-green-500 rounded"></div>
                  <div className="w-3 h-3 bg-yellow-500 rounded"></div>
                  <div className="w-3 h-3 bg-red-500 rounded"></div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Legend */}
        <div className="absolute bottom-4 left-4 bg-white rounded-lg shadow-sm border border-gray-200 p-3">
          <div className="text-xs font-medium text-gray-700 mb-2">Legend</div>
          <div className="space-y-2">
            {/* Truck Status */}
            <div>
              <div className="text-xs text-gray-600 mb-1">Truck Status</div>
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
            
            {/* Journey Legend */}
            {showJourneys && (
              <div>
                <div className="text-xs text-gray-600 mb-1">Journey</div>
                <div className="space-y-1">
                  <div className="flex items-center space-x-2 text-xs">
                    <span style={{ fontSize: '10px' }}>📦</span>
                    <span className="text-gray-600">Pickup</span>
                  </div>
                  <div className="flex items-center space-x-2 text-xs">
                    <span style={{ fontSize: '10px' }}>🏠</span>
                    <span className="text-gray-600">Delivery</span>
                  </div>
                  <div className="flex items-center space-x-2 text-xs">
                    <div className="w-4 h-0.5 bg-blue-500"></div>
                    <span className="text-gray-600">Route</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
};

export default FleetMapFixed;