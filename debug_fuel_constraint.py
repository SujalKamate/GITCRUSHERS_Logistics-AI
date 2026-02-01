#!/usr/bin/env python3
"""
Debug script to test fuel constraints for the failing request.
"""

import asyncio
from src.api.services.request_processor import request_processor
from src.api.services.state_manager import state_manager
from src.api.services.simulation import simulation_service
from src.models import Location, TruckStatus

async def debug_fuel_constraint():
    """Debug fuel constraints for the failing request."""
    print("🔍 Debugging fuel constraints...")
    
    # Initialize simulation data
    simulation_service.generate_initial_data(num_trucks=10)
    
    # Get the request that we just processed
    request = request_processor.get_request("REQ-C3075BAB")
    if not request:
        print("❌ Request not found")
        return
    
    print(f"✅ Found request: {request.id}")
    print(f"   Pickup: {request.pickup_location.latitude}, {request.pickup_location.longitude}")
    print(f"   Delivery: {request.delivery_location.latitude}, {request.delivery_location.longitude}")
    
    # Calculate distance
    distance = request.pickup_location.distance_to(request.delivery_location)
    print(f"   Distance: {distance:.1f}km")
    
    # Get available trucks
    available_trucks = [
        truck for truck in state_manager.trucks 
        if truck.status in [TruckStatus.IDLE, TruckStatus.EN_ROUTE]
        and truck.capacity_kg >= request.weight_kg
    ]
    
    print(f"\n🚛 Testing fuel constraints for {len(available_trucks)} trucks:")
    
    for truck in available_trucks:
        print(f"\n   Truck {truck.id} ({truck.name}):")
        print(f"     Fuel level: {truck.fuel_level_percent:.1f}%")
        
        if truck.current_location:
            # Calculate distances
            distance_to_pickup = truck.current_location.distance_to(request.pickup_location)
            delivery_distance = request.pickup_location.distance_to(request.delivery_location)
            total_distance = distance_to_pickup + delivery_distance
            
            print(f"     Distance to pickup: {distance_to_pickup:.1f}km")
            print(f"     Delivery distance: {delivery_distance:.1f}km")
            print(f"     Total distance: {total_distance:.1f}km")
            
            # Calculate fuel requirements
            fuel_needed = total_distance * 0.3  # L/km (0.3L per km consumption)
            fuel_available = 200 * (truck.fuel_level_percent / 100)  # 200L tank
            fuel_usable = fuel_available * 0.8  # Keep 20% buffer
            
            print(f"     Fuel needed: {fuel_needed:.1f}L")
            print(f"     Fuel available: {fuel_available:.1f}L")
            print(f"     Fuel usable (80%): {fuel_usable:.1f}L")
            
            fuel_ok = fuel_needed <= fuel_usable
            print(f"     Fuel constraint: {'✅' if fuel_ok else '❌'}")
            
            if not fuel_ok:
                print(f"     ⚠️  Fuel shortage: {fuel_needed - fuel_usable:.1f}L")
        else:
            print(f"     ❌ No current location")

if __name__ == "__main__":
    asyncio.run(debug_fuel_constraint())