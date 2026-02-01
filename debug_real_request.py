#!/usr/bin/env python3
"""
Debug script to examine the actual failing request data.
"""

import asyncio
from src.api.services.request_processor import request_processor

async def debug_real_request():
    """Debug the actual failing request."""
    print("🔍 Debugging real failing request...")
    
    # Get the failing request
    request = request_processor.get_request("REQ-73382780")
    if not request:
        print("❌ Request not found in processor memory")
        return
    
    print(f"✅ Found request: {request.id}")
    print(f"   Customer: {request.customer_name}")
    print(f"   Weight: {request.weight_kg}kg")
    print(f"   Status: {request.status}")
    print(f"   Pickup Address: {request.pickup_address}")
    print(f"   Delivery Address: {request.delivery_address}")
    
    # Check the actual locations that were geocoded
    print(f"\n🌍 Geocoded locations:")
    if request.pickup_location:
        print(f"   Pickup: {request.pickup_location.latitude}, {request.pickup_location.longitude}")
        print(f"   Pickup Address: {request.pickup_location.address}")
    else:
        print(f"   Pickup: ❌ None")
    
    if request.delivery_location:
        print(f"   Delivery: {request.delivery_location.latitude}, {request.delivery_location.longitude}")
        print(f"   Delivery Address: {request.delivery_location.address}")
    else:
        print(f"   Delivery: ❌ None")
    
    # Check if locations are valid
    if request.pickup_location and request.delivery_location:
        distance = request.pickup_location.distance_to(request.delivery_location)
        print(f"   Distance: {distance:.1f}km")
        
        # Test if this distance is causing issues
        if distance > 10000:  # Very long distance
            print(f"   ⚠️  Very long distance detected: {distance:.1f}km")
    
    print(f"\n🤖 AI Analysis:")
    if request.ai_analysis:
        print(f"   Risk Level: {request.ai_analysis.get('risk_level', 'unknown')}")
        print(f"   Complexity: {request.ai_analysis.get('complexity_score', 'unknown')}/10")
        print(f"   Reasoning: {request.ai_analysis.get('reasoning', 'none')}")
    else:
        print(f"   ❌ No AI analysis")

if __name__ == "__main__":
    asyncio.run(debug_real_request())