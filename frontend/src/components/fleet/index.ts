/**
 * Fleet components export file.
 */

// Note: FleetMap is NOT exported here because it uses Leaflet which requires browser APIs.
// Import FleetMap directly using dynamic() with ssr: false
// Example: const FleetMap = dynamic(() => import('@/components/fleet/FleetMap'), { ssr: false })

export { default as TruckList } from './TruckList';
export { default as TruckDetail } from './TruckDetail';