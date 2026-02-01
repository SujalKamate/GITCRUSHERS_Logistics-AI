/**
 * Enhanced Fleet Map with Journey Tracking
 * Shows truck routes from current location to pickup to delivery
 */

'use client';

import React, { useState, useEffect, useCallback } from 'react';
import FleetMapFixed from './FleetMapFixed';
import { MapTruck } from '@/types';
import { API_BASE_URL } from '@/lib/constants';

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

interface FleetMapWithJourneysProps {
  trucks: MapTruck[];
  height?: string;
  onTruckClick?: (truckId: string) => void;
  showControls?: boolean;
  showTraffic?: boolean;
  className?: string;
}

const FleetMapWithJourneys: React.FC<FleetMapWithJourneysProps> = ({
  trucks,
  height = '600px',
  onTruckClick,
  showControls = true,
  showTraffic = true,
  className,
}) => {
  const [journeySegments, setJourneySegments] = useState<JourneySegment[]>([]);
  const [deliveryMarkers, setDeliveryMarkers] = useState<DeliveryMarker[]>([]);
  const [loading, setLoading] = useState(false);

  // Fetch delivery requests and journey data
  const fetchJourneyData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/requests/journeys/active`);
      if (response.ok) {
        const data = await response.json();
        generateJourneyDataFromAPI(data.journeys);
      }
    } catch (error) {
      console.error('Failed to fetch journey data:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  // Generate journey segments and markers from API data
  const generateJourneyDataFromAPI = useCallback((journeys: any[]) => {
    const segments: JourneySegment[] = [];
    const markers: DeliveryMarker[] = [];

    journeys.forEach(journey => {
      // Create journey segments from API data
      journey.segments.forEach((segment: any, index: number) => {
        segments.push({
          id: `${journey.request_id}-${segment.type}`,
          truckId: journey.truck_id,
          type: segment.type,
          coordinates: [
            [segment.from.latitude, segment.from.longitude],
            [segment.to.latitude, segment.to.longitude]
          ],
          color: segment.color,
          status: segment.status
        });
      });

      // Create pickup marker
      markers.push({
        id: `${journey.request_id}-pickup`,
        type: 'pickup',
        position: [journey.pickup_location.latitude, journey.pickup_location.longitude],
        address: journey.pickup_location.address,
        requestId: journey.request_id,
        customerName: journey.customer_name,
        status: 'pending'
      });

      // Create delivery marker
      markers.push({
        id: `${journey.request_id}-delivery`,
        type: 'delivery',
        position: [journey.delivery_location.latitude, journey.delivery_location.longitude],
        address: journey.delivery_location.address,
        requestId: journey.request_id,
        customerName: journey.customer_name,
        status: 'pending'
      });
    });

    setJourneySegments(segments);
    setDeliveryMarkers(markers);
  }, []);

  // Fetch data on mount and when trucks change
  useEffect(() => {
    fetchJourneyData();
  }, [fetchJourneyData]);

  // Refresh data every 30 seconds
  useEffect(() => {
    const interval = setInterval(fetchJourneyData, 30000);
    return () => clearInterval(interval);
  }, [fetchJourneyData]);

  return (
    <FleetMapFixed
      trucks={trucks}
      height={height}
      journeySegments={journeySegments}
      deliveryMarkers={deliveryMarkers}
      showJourneys={true}
      onTruckClick={onTruckClick}
      showControls={showControls}
      showTraffic={showTraffic}
      className={className}
    />
  );
};

export default FleetMapWithJourneys;