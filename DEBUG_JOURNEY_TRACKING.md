# 🐛 Journey Tracking Debug Guide

## Current Status

✅ **Backend API Working**
- `/api/requests/journeys/active` returns journey data
- Request REQ-6F82079E is assigned to TRK-008
- Journey segments and coordinates are correct

✅ **Driver App Fixed**
- Changed from TRK-001 to TRK-008
- Should now show the assigned delivery

❓ **Frontend Map** - Need to verify
- FleetMapWithJourneys component created
- Debug logging added
- Fleet page updated to use journey map

## Testing Steps

### 1. Test API Endpoints
```bash
# Test journey endpoint
curl "http://localhost:8000/api/requests/journeys/active"

# Test truck-specific requests
curl "http://localhost:8000/api/requests/?assigned_truck=TRK-008"
```

### 2. Test Driver App
1. Open: `http://localhost:8000/driver-app/`
2. Should show delivery for Sarthak Godse
3. Check browser console for errors

### 3. Test Fleet Map
1. Open: `http://localhost:3002/fleet`
2. Switch to Map View
3. Check browser console for:
   - "Fetching journey data from: ..."
   - "Journey data received: ..."
   - "Processing journeys: 1"
   - "Generated segments: 2 markers: 2"
   - "Updating journey segments: 2"
   - "Updating delivery markers: 2"

### 4. Test Journey Tracking Page
1. Open: `http://localhost:8000/test_journey_tracking.html`
2. Click all buttons to test API endpoints
3. Verify data is returned correctly

## Expected Results

### Driver App Should Show:
```
Current Deliveries:
- REQ-6F82079E
- Customer: Sarthak Godse
- Description: Boxes (5.0kg)
- Pickup: 15 Indradhanu Apt, Manikbaug, Sinhgad Road
- Delivery: Talegoan
- Status: Assigned
```

### Fleet Map Should Show:
- Blue line from truck TRK-008 to pickup location
- Purple line from pickup to delivery location
- 📦 Pickup marker at pickup address
- 🏠 Delivery marker at delivery address
- Interactive popups with journey details

### Journey API Should Return:
```json
{
  "journeys": [
    {
      "request_id": "REQ-6F82079E",
      "truck_id": "TRK-008",
      "customer_name": "Sarthak Godse",
      "segments": [
        {
          "type": "to_pickup",
          "status": "active",
          "color": "#3b82f6"
        },
        {
          "type": "to_delivery", 
          "status": "pending",
          "color": "#8b5cf6"
        }
      ]
    }
  ]
}
```

## Troubleshooting

### If Driver App Shows "No active deliveries":
1. Check truck ID is TRK-008
2. Verify API endpoint returns data
3. Check browser console for errors

### If Fleet Map Shows No Journey:
1. Check browser console for debug logs
2. Verify API_BASE_URL is correct
3. Check CORS settings
4. Verify FleetMapWithJourneys is being used

### If API Returns Empty:
1. Check if request is still assigned
2. Verify truck and location data exists
3. Check server logs for errors

## Quick Fixes

### Force Refresh Journey Data:
```javascript
// In browser console on fleet page
window.location.reload();
```

### Test API Directly:
```javascript
// In browser console
fetch('http://localhost:8000/api/requests/journeys/active')
  .then(r => r.json())
  .then(console.log);
```

### Check Map Component:
```javascript
// In browser console on fleet page
console.log('Journey segments:', window.journeySegments);
console.log('Delivery markers:', window.deliveryMarkers);
```

## Files Modified

1. `driver-app/index.html` - Changed truck ID to TRK-008
2. `frontend/src/components/fleet/FleetMapFixed.tsx` - Added journey support
3. `frontend/src/components/fleet/FleetMapWithJourneys.tsx` - New journey component
4. `frontend/src/app/fleet/page.tsx` - Uses journey map
5. `src/api/routes/requests.py` - Added journey endpoint

The journey tracking should now be working! 🚛📦🗺️