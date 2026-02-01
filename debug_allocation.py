#!/usr/bin/env python3
"""
Debug script to test truck allocation logic.
"""

import asyncio
from src.api.services.state_manager import state_manager
from src.api.services.simulation import simulation_service
from src.api.services.request_processor import request_processor
from src.models import DeliveryRequest, LoadPriority, Location

async def debug_allocation():
    """Debug the truck allocation process."""
    print("🔍 Debugging truck allocation...")
    
    # Initialize simulation data
    simulation_service.generate_initial_data(num_trucks=10)
    print(f"✅ Generated {len(state_manager.trucks)} trucks")
    
    # Check available trucks
    available_trucks = [
        truck for truck in state_manager.trucks 
        if truck.status.value in ['idle', 'en_route']
        and truck.capacity_kg >= 8.5
    ]
    print(f"✅ Found {len(available_trucks)} available trucks:")
    for truck in available_trucks[:3]:
        print(f"   - {truck.id}: {truck.name} ({truck.status.value}, {truck.capacity_kg}kg)")
        print(f"     Location: {truck.current_location.address if truck.current_location else 'None'}")
    
    # Create a test request
    test_request = DeliveryRequest(
        id="TEST-001",
        customer_name="Debug Test",
        description="Test allocation",
        weight_kg=8.5,
        priority=LoadPriority.HIGH,
        pickup_address="100 Test Street, New York, NY",
        delivery_address="200 Demo Avenue, Brooklyn, NY",
        fragile=True
    )
    
    print(f"\n🧪 Testing request: {test_request.id}")
    print(f"   Weight: {test_request.weight_kg}kg")
    print(f"   Priority: {test_request.priority}")
    
    # Test geocoding
    print("\n🌍 Testing geocoding...")
    await request_processor._geocode_addresses(test_request)
    
    if test_request.pickup_location:
        print(f"✅ Pickup location: {test_request.pickup_location.latitude}, {test_request.pickup_location.longitude}")
    else:
        print("❌ Pickup location not set")
    
    if test_request.delivery_location:
        print(f"✅ Delivery location: {test_request.delivery_location.latitude}, {test_request.delivery_location.longitude}")
    else:
        print("❌ Delivery location not set")
    
    # Test AI analysis
    print("\n🤖 Testing AI analysis...")
    await request_processor._analyze_request_with_ai(test_request)
    
    if test_request.ai_analysis:
        print(f"✅ AI analysis completed: {test_request.ai_analysis['risk_level']} risk")
    else:
        print("❌ AI analysis failed")
    
    # Test truck allocation
    print("\n🚛 Testing truck allocation...")
    await request_processor._allocate_truck(test_request)
    
    if test_request.assigned_truck_id:
        print(f"✅ Truck allocated: {test_request.assigned_truck_id}")
        print(f"   Reasoning: {test_request.allocation_reasoning}")
    else:
        print("❌ Truck allocation failed")
        
        # Debug why allocation failed
        print("\n🔍 Debugging allocation failure...")
        
        # Check if trucks are available
        if not available_trucks:
            print("❌ No available trucks found")
        else:
            print(f"✅ {len(available_trucks)} trucks available")
            
            # Check assignment engine
            from src.algorithms.load_assignment import LoadAssignmentEngine
            from src.models import Load
            
            engine = LoadAssignmentEngine()
            
            # Create temporary load
            temp_load = Load(
                id="TEMP-TEST",
                description=test_request.description,
                weight_kg=test_request.weight_kg,
                priority=test_request.priority,
                pickup_location=test_request.pickup_location,
                delivery_location=test_request.delivery_location
            )
            
            print(f"   Temp load created: {temp_load.id}")
            print(f"   Pickup location: {temp_load.pickup_location}")
            print(f"   Delivery location: {temp_load.delivery_location}")
            
            # Test assignment
            solution = engine.assign_loads_to_trucks(available_trucks, [temp_load])
            
            print(f"   Assignment solution:")
            print(f"     Assignments: {len(solution.assignments)}")
            print(f"     Unassigned: {solution.unassigned_loads}")
            print(f"     Total cost: {solution.total_cost}")
            
            if solution.assignments:
                assignment = solution.assignments[0]
                print(f"     Best assignment: {assignment.truck_id} -> {assignment.load_id}")
                print(f"     Cost: ${assignment.estimated_cost:.2f}")
                print(f"     Confidence: {assignment.confidence_score:.2f}")
            else:
                print("     No valid assignments found")
                
                # Check constraints for each truck
                print("\n   Checking constraints for each truck:")
                for truck in available_trucks[:3]:
                    can_assign = engine._check_assignment_constraints(truck, temp_load)
                    print(f"     {truck.id}: {'✅' if can_assign else '❌'}")
                    
                    if not can_assign:
                        # Check specific constraints
                        if truck.capacity_kg < temp_load.weight_kg:
                            print(f"       ❌ Capacity: {truck.capacity_kg}kg < {temp_load.weight_kg}kg")
                        
                        if not truck.current_location:
                            print(f"       ❌ No current location")
                        elif not temp_load.pickup_location:
                            print(f"       ❌ No pickup location")
                        else:
                            distance = truck.current_location.distance_to(temp_load.pickup_location)
                            print(f"       ✅ Distance to pickup: {distance:.1f}km")

if __name__ == "__main__":
    asyncio.run(debug_allocation())