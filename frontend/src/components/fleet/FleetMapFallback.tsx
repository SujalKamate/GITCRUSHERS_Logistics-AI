/**
 * Fallback fleet map component for SSR/build compatibility.
 */

import React from 'react';
import { MapProps } from '@/types';
import { Card, LoadingSpinner } from '@/components/ui';

const FleetMapFallback: React.FC<MapProps> = ({
  height = '400px',
  trucks = [],
  className,
}) => {
  return (
    <div className={className}>
      <Card padding="none" className="overflow-hidden">
        <div style={{ height }} className="flex items-center justify-center bg-gray-100">
          <div className="text-center">
            <div className="text-6xl mb-4">🗺️</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Interactive Fleet Map
            </h3>
            <p className="text-gray-600 mb-4">
              {trucks.length} trucks ready to display
            </p>
            <LoadingSpinner text="Loading map components..." />
          </div>
        </div>
      </Card>
    </div>
  );
};

export default FleetMapFallback;