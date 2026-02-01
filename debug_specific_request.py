#!/usr/bin/env python3
"""
Debug script for the specific failing request.
"""

import asyncio
from src.api.services.request_processor import request_processor
from src.api.services.state_manager import state_manager
from src.api.services.simulation import simulation_service

async def debug_specific_request():
    """Debug the specific request that's failing."""
    print("🔍 Debugging specific request REQ-D6242AB2...")
    
    # Get the request
    request = request_processor.get_request("REQ-D6242AB2")
    if not request:
        print("❌ Request not found")
        return
    
    print(f"✅ Found request: {request.id}")
    print(f"   Customer: {request.customer_name}")
    print(f"   Weight: {request.weight_kg}kg")
    print(f"   Status: {request.status}")
    print(f"   Assigned Truck: {request.assigned_truck_id}")
    print(f"   Pickup Location: {request.pickup_location}")
    print(f"   Delivery Location: {request.delivery_location}")
    
    # Check available trucks
    available_trucks = [
        truck for truck in state_manager.trucks 
        if truck.status.value in ['idle', 'en_route']
        and truck.capacity_kg >= request.weight_kg
    ]
    
    print(f"\n🚛 Available trucks: {len(available_trucks)}")
    for truck in available_trucks[:3]:
        print(f"   - {truck.id}: {truck.name} ({truck.status.value}, {truck.capacity_kg}kg)")
    
    if not available_trucks:
        print("❌ No available trucks found!")
        return
    
    # Test the assignment engine directly
    from src.algorithms.load_assignment import LoadAssignmentEngine
    from src.models import Load
    
    engine = LoadAssignmentEngine()
    
    # Create temporary load
    temp_load = Load(
        id=f"TEMP-{request.id}",
        description=request.description,
        weight_kg=request.weight_kg,
        volume_m3=request.volume_m3,
        priority=request.priority,
        pickup_location=request.pickup_location,
        delivery_location=request.delivery_location,
        delivery_deadline=request.delivery_deadline
    )
    
    print(f"\n🧪 Testing assignment engine...")
    print(f"   Temp load: {temp_load.id}")
    print(f"   Weight: {temp_load.weight_kg}kg")
    print(f"   Priority: {temp_load.priority}")
    
    # Test assignment
    solution = engine.assign_loads_to_trucks(available_trucks, [temp_load])
    
    print(f"\n📊 Assignment solution:")
    print(f"   Assignments: {len(solution.assignments)}")
    print(f"   Unassigned: {solution.unassigned_loads}")
    print(f"   Total cost: {solution.total_cost}")
    print(f"   Utilization: {solution.utilization_rate:.2%}")
    
    if solution.assignments:
        assignment = solution.assignments[0]
        print(f"\n✅ Assignment found:")
        print(f"   Truck: {assignment.truck_id}")
        print(f"   Load: {assignment.load_id}")
        print(f"   Cost: ${assignment.estimated_cost:.2f}")
        print(f"   Confidence: {assignment.confidence_score:.2f}")
    else:
        print(f"\n❌ No assignments found!")
        
        # Debug why no assignments
        print(f"\n🔍 Debugging assignment constraints...")
        for i, truck in enumerate(available_trucks[:3]):
            print(f"\n   Truck {truck.id}:")
            
            # Check capacity
            if truck.capacity_kg < temp_load.weight_kg:
                print(f"     ❌ Capacity: {truck.capacity_kg}kg < {temp_load.weight_kg}kg")
            else:
                print(f"     ✅ Capacity: {truck.capacity_kg}kg >= {temp_load.weight_kg}kg")
            
            # Check location
            if not truck.current_location:
                print(f"     ❌ No current location")
            else:
                print(f"     ✅ Location: {truck.current_location.address}")
            
            # Check pickup location
            if not temp_load.pickup_location:
                print(f"     ❌ No pickup location")
            else:
                print(f"     ✅ Pickup: {temp_load.pickup_location.address}")
            
            # Check delivery location
            if not temp_load.delivery_location:
                print(f"     ❌ No delivery location")
            else:
                print(f"     ✅ Delivery: {temp_load.delivery_location.address}")
            
            # Test constraint check
            can_assign = engine._check_assignment_constraints(truck, temp_load)
            print(f"     {'✅' if can_assign else '❌'} Constraint check: {can_assign}")
            
            if can_assign:
                cost = engine._calculate_assignment_cost(truck, temp_load)
                print(f"     💰 Cost: ${cost:.2f}")

if __name__ == "__main__":
    asyncio.run(debug_specific_request())