/**
 * Wrapper component to handle Leaflet map initialization issues with React Strict Mode.
 */

'use client';

import React, { useEffect, useRef, useState } from 'react';
import { MapProps } from '@/types';
import { LoadingSpinner } from '@/components/ui';

// Lazy load the actual FleetMap component
const FleetMapFixed = React.lazy(() => import('./FleetMapFixed'));

const FleetMapWrapper: React.FC<MapProps> = (props) => {
  const [mounted, setMounted] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Only mount after initial render to avoid Strict Mode double-initialization
    setMounted(true);

    return () => {
      setMounted(false);
    };
  }, []);

  if (!mounted) {
    return (
      <div
        ref={containerRef}
        style={{ height: props.height || '400px' }}
        className="flex items-center justify-center bg-gray-100 rounded-lg"
      >
        <LoadingSpinner text="Loading map..." />
      </div>
    );
  }

  return (
    <React.Suspense
      fallback={
        <div
          style={{ height: props.height || '400px' }}
          className="flex items-center justify-center bg-gray-100 rounded-lg"
        >
          <LoadingSpinner text="Loading map..." />
        </div>
      }
    >
      <FleetMapFixed {...props} />
    </React.Suspense>
  );
};

export default FleetMapWrapper;
