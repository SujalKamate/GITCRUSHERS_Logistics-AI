/**
 * Fleet components export file.
 */

// Note: FleetMap components are NOT exported here because they use Leaflet which requires browser APIs.
// Import FleetMap components directly using dynamic() with ssr: false
// Available components:
// - FleetMap: Basic fleet map
// - FleetMapFixed: Enhanced fleet map with better Leaflet handling
// - FleetMapWithJourneys: Fleet map with delivery journey tracking
// Example: const FleetMap = dynamic(() => import('@/components/fleet/FleetMapWithJourneys'), { ssr: false })

export { default as TruckList } from './TruckList';
export { default as TruckDetail } from './TruckDetail';