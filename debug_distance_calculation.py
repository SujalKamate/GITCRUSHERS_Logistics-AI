#!/usr/bin/env python3
"""
Debug script to test distance calculations.
"""

from src.models import Location

def debug_distance_calculation():
    """Debug distance calculations."""
    print("🔍 Debugging distance calculations...")
    
    # Test the coordinates that would be used for the failing request
    # Delivery address geocoded successfully to India
    delivery_location = Location(
        latitude=18.6953472, 
        longitude=74.1376597,
        address="Talegoan, India"
    )
    
    # Pickup address failed, so fallback is near delivery
    pickup_location = Location(
        latitude=18.6953472 + 0.01,  # ~1km offset
        longitude=74.1376597 + 0.01,
        address="Pickup near Talegoan"
    )
    
    print(f"📍 Pickup: {pickup_location.latitude}, {pickup_location.longitude}")
    print(f"📍 Delivery: {delivery_location.latitude}, {delivery_location.longitude}")
    
    try:
        distance = pickup_location.distance_to(delivery_location)
        print(f"📏 Distance: {distance:.2f}km")
        
        if distance > 1000:
            print(f"⚠️  Suspiciously large distance: {distance:.2f}km")
        elif distance < 0:
            print(f"⚠️  Invalid negative distance: {distance:.2f}km")
        else:
            print(f"✅ Reasonable distance: {distance:.2f}km")
            
    except Exception as e:
        print(f"❌ Distance calculation error: {e}")
    
    # Test with NYC truck locations
    print(f"\n🚛 Testing with NYC truck locations:")
    
    nyc_locations = [
        Location(latitude=40.7128, longitude=-74.0060, address="NYC 1"),
        Location(latitude=40.7589, longitude=-73.9851, address="NYC 2"),
        Location(latitude=40.7424, longitude=-74.0061, address="NYC 3"),
    ]
    
    for i, truck_loc in enumerate(nyc_locations):
        try:
            distance_to_pickup = truck_loc.distance_to(pickup_location)
            delivery_distance = pickup_location.distance_to(delivery_location)
            total_distance = distance_to_pickup + delivery_distance
            
            print(f"   Truck {i+1}: {distance_to_pickup:.1f}km to pickup + {delivery_distance:.1f}km delivery = {total_distance:.1f}km total")
            
            # Calculate fuel needed
            fuel_needed = total_distance * 0.3  # L/km
            print(f"   Fuel needed: {fuel_needed:.1f}L")
            
            if fuel_needed > 160:  # 80% of 200L tank
                print(f"   ❌ Too much fuel needed")
            else:
                print(f"   ✅ Fuel requirement OK")
                
        except Exception as e:
            print(f"   ❌ Error for truck {i+1}: {e}")

if __name__ == "__main__":
    debug_distance_calculation()