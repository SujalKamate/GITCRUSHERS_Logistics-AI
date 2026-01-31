#!/usr/bin/env python3
"""
System test script to verify all components are working.
"""
import asyncio
import sys
from datetime import datetime

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        # Core models
        from src.models import Truck, Load, Location, TruckStatus
        print("✅ Core models imported")
        
        # API components
        from src.api.main import app
        print("✅ FastAPI app imported")
        
        # Algorithms
        from src.algorithms.route_optimizer import RouteOptimizer
        from src.algorithms.load_assignment import LoadAssignmentEngine
        print("✅ Optimization algorithms imported")
        
        # AI components
        from src.reasoning.grok_client import get_groq_client
        print("✅ Groq client imported")
        
        # Optional database service
        try:
            from database_setup import get_database_service
            print("✅ Database service imported")
        except ImportError as e:
            print(f"⚠️  Database service not available: {e}")
        
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_algorithms():
    """Test optimization algorithms."""
    print("\nTesting algorithms...")
    
    try:
        from src.models import Truck, Load, Location, TruckStatus, LoadPriority
        from src.algorithms.route_optimizer import RouteOptimizer
        from src.algorithms.load_assignment import LoadAssignmentEngine
        
        # Create test data
        truck = Truck(
            id="TEST-001",
            name="Test Truck",
            status=TruckStatus.IDLE,
            current_location=Location(latitude=40.7128, longitude=-74.0060),
            capacity_kg=15000,
            fuel_level_percent=80.0
        )
        
        load = Load(
            id="TEST-LOAD-001",
            description="Test Load",
            weight_kg=5000,
            priority=LoadPriority.NORMAL,
            pickup_location=Location(latitude=40.7589, longitude=-73.9851),
            delivery_location=Location(latitude=40.6782, longitude=-73.9442)
        )
        
        # Test route optimizer
        optimizer = RouteOptimizer()
        route = optimizer.optimize_route(truck, [load])
        print(f"✅ Route optimization: {route.total_distance_km:.1f}km, {route.total_time_minutes:.0f}min")
        
        # Test load assignment
        assignment_engine = LoadAssignmentEngine()
        solution = assignment_engine.assign_loads_to_trucks([truck], [load])
        print(f"✅ Load assignment: {len(solution.assignments)} assignments, {solution.utilization_rate:.1%} utilization")
        
        return True
    except Exception as e:
        print(f"❌ Algorithm test failed: {e}")
        return False

def test_ai_client():
    """Test AI client."""
    print("\nTesting AI client...")
    
    try:
        from src.reasoning.grok_client import get_groq_client
        
        client = get_groq_client()
        
        if client.is_available:
            print("✅ Groq client configured and available")
            
            # Test a simple completion
            response = client.complete(
                prompt="Analyze this logistics situation: Truck T001 is stuck in traffic.",
                system_prompt="You are a logistics expert."
            )
            
            if response.get("success"):
                print("✅ LLM response received")
            else:
                print("⚠️  LLM unavailable, using fallback")
        else:
            print("⚠️  Groq client not configured - will use fallback mode")
            
        return True
    except Exception as e:
        print(f"❌ AI client test failed: {e}")
        return False

def test_simulation():
    """Test simulation service."""
    print("\nTesting simulation...")
    
    try:
        from src.api.services.enhanced_simulation import enhanced_simulation_service
        
        # Generate test data
        enhanced_simulation_service.generate_initial_data(num_trucks=3, num_loads=5)
        
        from src.api.services.state_manager import state_manager
        
        print(f"✅ Generated {len(state_manager.trucks)} trucks")
        print(f"✅ Generated {len(state_manager.loads)} loads")
        print(f"✅ Generated {len(state_manager.traffic_conditions)} traffic conditions")
        
        # Check assignments
        assigned_loads = [l for l in state_manager.loads if l.assigned_truck_id]
        print(f"✅ Assigned {len(assigned_loads)} loads to trucks")
        
        return True
    except Exception as e:
        print(f"❌ Simulation test failed: {e}")
        return False

async def test_api_server():
    """Test API server startup."""
    print("\nTesting API server...")
    
    try:
        from src.api.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"⚠️  Health endpoint returned {response.status_code}")
        
        # Test fleet endpoint
        response = client.get("/api/fleet/trucks")
        if response.status_code == 200:
            trucks = response.json().get("trucks", [])
            print(f"✅ Fleet endpoint working ({len(trucks)} trucks)")
        else:
            print(f"⚠️  Fleet endpoint returned {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ API server test failed: {e}")
        return False

def print_system_status():
    """Print overall system status."""
    print("\n" + "="*60)
    print(" SYSTEM STATUS SUMMARY")
    print("="*60)
    
    try:
        from src.reasoning.grok_client import get_groq_client
        from src.api.services.state_manager import state_manager
        
        client = get_groq_client()
        
        print(f"🤖 AI Client: {'✅ Available' if client.is_available else '⚠️  Fallback Mode'}")
        print(f"🚛 Fleet Size: {len(state_manager.trucks)} trucks")
        print(f"📦 Active Loads: {len(state_manager.loads)} loads")
        print(f"🚦 Traffic Segments: {len(state_manager.traffic_conditions)} segments")
        print(f"⚡ Control Loop: {'✅ Ready' if hasattr(state_manager, 'control_loop_running') else '⚠️  Not initialized'}")
        
        # Database status
        try:
            from database_setup import get_database_service
            print("💾 Database: ✅ Available")
        except:
            print("💾 Database: ⚠️  In-memory mode")
        
        print(f"\n🕒 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ Status check failed: {e}")

async def main():
    """Run all tests."""
    print("🚀 LOGISTICS AI SYSTEM TEST")
    print("="*60)
    
    tests = [
        ("Imports", test_imports),
        ("Algorithms", test_algorithms),
        ("AI Client", test_ai_client),
        ("Simulation", test_simulation),
        ("API Server", test_api_server),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Print results
    print("\n" + "="*60)
    print(" TEST RESULTS")
    print("="*60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! System is ready.")
    elif passed >= len(tests) * 0.8:
        print("⚠️  Most tests passed. System functional with minor issues.")
    else:
        print("❌ Multiple test failures. Check configuration.")
    
    print_system_status()
    
    return passed == len(tests)

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)