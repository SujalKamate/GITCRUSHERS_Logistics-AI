#!/usr/bin/env python3
"""
Debug script to test assignment constraints for heavy loads.
"""

import asyncio
from src.api.services.state_manager import state_manager
from src.api.services.simulation import simulation_service
from src.algorithms.load_assignment import LoadAssignmentEngine
from src.models import Load, LoadPriority, Location, TruckStatus

async def debug_assignment_constraints():
    """Debug why assignment is failing for heavy loads."""
    print("🔍 Debugging assignment constraints for heavy loads...")
    
    # Initialize simulation data
    simulation_service.generate_initial_data(num_trucks=10)
    
    # Get available trucks
    available_trucks = [
        truck for truck in state_manager.trucks 
        if truck.status in [TruckStatus.IDLE, TruckStatus.EN_ROUTE]
        and truck.capacity_kg >= 500.0
    ]
    
    print(f"✅ Found {len(available_trucks)} available trucks for 500kg load")
    
    # Create test load with fallback locations (same as the failing request)
    test_load = Load(
        id="TEST-HEAVY",
        description="Heavy boxes test",
        weight_kg=500.0,
        priority=LoadPriority.HIGH,
        pickup_location=Location(
            latitude=40.7128, longitude=-74.0060,
            address="15 Indradhanu Apt, Manikbaug, Sinhgad Road"
        ),
        delivery_location=Location(
            latitude=40.7589, longitude=-73.9851,
            address="Talegoan"
        )
    )
    
    print(f"\n🧪 Test load details:")
    print(f"   Weight: {test_load.weight_kg}kg")
    print(f"   Priority: {test_load.priority}")
    print(f"   Pickup: {test_load.pickup_location.latitude}, {test_load.pickup_location.longitude}")
    print(f"   Delivery: {test_load.delivery_location.latitude}, {test_load.delivery_location.longitude}")
    
    # Test assignment engine
    engine = LoadAssignmentEngine()
    
    print(f"\n🔍 Testing constraints for each truck:")
    
    for i, truck in enumerate(available_trucks[:5]):  # Test first 5 trucks
        print(f"\n   Truck {truck.id} ({truck.name}):")
        print(f"     Status: {truck.status}")
        print(f"     Capacity: {truck.capacity_kg}kg")
        print(f"     Current Location: {truck.current_location.address if truck.current_location else 'None'}")
        
        # Test individual constraints
        can_assign = engine._check_assignment_constraints(truck, test_load)
        print(f"     Overall constraint check: {'✅' if can_assign else '❌'}")
        
        if not can_assign:
            # Debug individual constraint failures
            print(f"     Debugging individual constraints:")
            
            # Capacity constraint
            capacity_ok = truck.capacity_kg >= test_load.weight_kg
            print(f"       Capacity: {'✅' if capacity_ok else '❌'} ({truck.capacity_kg}kg >= {test_load.weight_kg}kg)")
            
            # Location constraints
            if not truck.current_location:
                print(f"       Current location: ❌ Missing")
            else:
                print(f"       Current location: ✅ Available")
                
                # Distance and fuel calculation
                try:
                    distance_to_pickup = truck.current_location.distance_to(test_load.pickup_location)
                    delivery_distance = test_load.pickup_location.distance_to(test_load.delivery_location)
                    total_distance = distance_to_pickup + delivery_distance
                    
                    print(f"       Distance to pickup: {distance_to_pickup:.1f}km")
                    print(f"       Delivery distance: {delivery_distance:.1f}km")
                    print(f"       Total distance: {total_distance:.1f}km")
                    
                    # Fuel constraint check
                    fuel_needed = total_distance * 0.3  # L/km
                    fuel_available = 200 * (truck.fuel_level_percent / 100)  # Assume 200L tank
                    fuel_ok = fuel_needed <= fuel_available * 0.8  # Keep 20% buffer
                    
                    print(f"       Fuel needed: {fuel_needed:.1f}L")
                    print(f"       Fuel available: {fuel_available:.1f}L (80% of {200 * (truck.fuel_level_percent / 100):.1f}L)")
                    print(f"       Fuel constraint: {'✅' if fuel_ok else '❌'}")
                    
                except Exception as e:
                    print(f"       Distance calculation error: {e}")
        else:
            # Calculate cost for successful assignments
            try:
                cost = engine._calculate_assignment_cost(truck, test_load)
                print(f"     Estimated cost: ${cost:.2f}")
            except Exception as e:
                print(f"     Cost calculation error: {e}")
    
    # Test full assignment
    print(f"\n📊 Testing full assignment algorithm:")
    solution = engine.assign_loads_to_trucks(available_trucks, [test_load])
    
    print(f"   Assignments: {len(solution.assignments)}")
    print(f"   Unassigned loads: {solution.unassigned_loads}")
    print(f"   Total cost: ${solution.total_cost:.2f}")
    print(f"   Utilization rate: {solution.utilization_rate:.2%}")
    
    if solution.assignments:
        assignment = solution.assignments[0]
        print(f"\n✅ Assignment found:")
        print(f"   Truck: {assignment.truck_id}")
        print(f"   Cost: ${assignment.estimated_cost:.2f}")
        print(f"   Confidence: {assignment.confidence_score:.2f}")
    else:
        print(f"\n❌ No assignments found - this explains the failure!")

if __name__ == "__main__":
    asyncio.run(debug_assignment_constraints())