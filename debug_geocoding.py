#!/usr/bin/env python3
"""
Debug script to test geocoding for the failing addresses.
"""

import asyncio
from geopy.geocoders import Nominatim
from src.models import Location

async def debug_geocoding():
    """Debug geocoding for the failing addresses."""
    print("🔍 Debugging geocoding for failing addresses...")
    
    geocoder = Nominatim(user_agent="logistics-ai-debug")
    
    addresses = [
        "15 Indradhanu Apt, Manikbaug, Sinhgad Road",
        "Talegoan"
    ]
    
    for addr in addresses:
        print(f"\n📍 Testing address: {addr}")
        
        try:
            # Try real geocoding
            result = await asyncio.to_thread(geocoder.geocode, addr)
            
            if result:
                print(f"   ✅ Geocoded: {result.latitude}, {result.longitude}")
                print(f"   Address: {result.address}")
            else:
                print(f"   ❌ Geocoding failed - no result")
                
                # Show what fallback coordinates would be used
                fallback_pickup = Location(latitude=40.7128, longitude=-74.0060, address=addr)
                fallback_delivery = Location(latitude=40.7589, longitude=-73.9851, address=addr)
                
                print(f"   Fallback pickup: {fallback_pickup.latitude}, {fallback_pickup.longitude} (NYC)")
                print(f"   Fallback delivery: {fallback_delivery.latitude}, {fallback_delivery.longitude} (NYC)")
                
        except Exception as e:
            print(f"   ❌ Geocoding error: {e}")
    
    # Test the distance calculation with fallback coordinates
    print(f"\n📏 Testing distance with fallback coordinates:")
    
    # These are the fallback coordinates used in the system
    pickup_fallback = Location(latitude=40.7128, longitude=-74.0060, address="Pickup")
    delivery_fallback = Location(latitude=40.7589, longitude=-73.9851, address="Delivery")
    
    distance = pickup_fallback.distance_to(delivery_fallback)
    print(f"   Distance between NYC fallback coordinates: {distance:.1f}km")
    
    # Test with actual Indian coordinates (approximate)
    print(f"\n🇮🇳 Testing with approximate Indian coordinates:")
    
    # Pune area coordinates (where these addresses likely are)
    pune_pickup = Location(latitude=18.5204, longitude=73.8567, address="Pune area")
    pune_delivery = Location(latitude=18.6298, longitude=73.7997, address="Talegaon area")
    
    pune_distance = pune_pickup.distance_to(pune_delivery)
    print(f"   Distance in Pune area: {pune_distance:.1f}km")
    
    # Test distance from NYC to India (this might be the 12634km issue)
    nyc_to_india = pickup_fallback.distance_to(pune_pickup)
    print(f"   Distance NYC to India: {nyc_to_india:.1f}km")

if __name__ == "__main__":
    asyncio.run(debug_geocoding())