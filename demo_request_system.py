#!/usr/bin/env python3
"""
Demo script showing the AI-powered delivery request system in action.
"""

import asyncio
import json
from datetime import datetime, timedelta

async def demo_request_system():
    """Demonstrate the complete request processing workflow."""
    print("🚀 LOGISTICS AI - DELIVERY REQUEST SYSTEM DEMO")
    print("="*60)
    print("This demo shows how AI processes delivery requests and allocates trucks")
    print()
    
    # Initialize the system
    from src.api.services.request_processor import request_processor
    from src.api.services.enhanced_simulation import enhanced_simulation_service
    
    # Generate some trucks for allocation
    print("🚛 Initializing fleet...")
    enhanced_simulation_service.generate_initial_data(num_trucks=5, num_loads=2)
    print("✅ Fleet ready with 5 trucks")
    print()
    
    # Demo request 1: Urgent medical delivery
    print("📦 DEMO REQUEST 1: Urgent Medical Delivery")
    print("-" * 40)
    
    medical_request = {
        "customer_name": "City Hospital",
        "customer_phone": "+1-555-MEDICAL",
        "customer_email": "logistics@cityhospital.com",
        "description": "Emergency medical supplies - blood bags and medications",
        "weight_kg": 45.0,
        "volume_m3": 1.2,
        "priority": "urgent",
        "pickup_address": "Medical Supply Warehouse, Manhattan, NY",
        "delivery_address": "City Hospital Emergency, Brooklyn, NY",
        "delivery_deadline": (datetime.now() + timedelta(hours=2)).isoformat(),
        "special_instructions": "Temperature sensitive - maintain cold chain",
        "fragile": True,
        "temperature_controlled": True
    }
    
    print(f"Customer: {medical_request['customer_name']}")
    print(f"Description: {medical_request['description']}")
    print(f"Priority: {medical_request['priority'].upper()}")
    print(f"Weight: {medical_request['weight_kg']}kg")
    print(f"Special: Temperature controlled, fragile")
    print()
    
    request1 = await request_processor.submit_request(medical_request)
    print(f"✅ Request submitted: {request1.id}")
    print("🤖 AI is analyzing the request...")
    
    # Wait for processing
    await asyncio.sleep(3)
    
    # Check results
    processed_request = request_processor.get_request(request1.id)
    if processed_request:
        print(f"📊 AI Analysis Results:")
        if processed_request.ai_analysis:
            analysis = processed_request.ai_analysis
            print(f"   Risk Level: {analysis.get('risk_level', 'N/A').upper()}")
            print(f"   Complexity Score: {analysis.get('complexity_score', 'N/A')}/10")
            if analysis.get('special_requirements'):
                print(f"   Special Requirements: {', '.join(analysis['special_requirements'])}")
        
        print(f"💰 Estimated Cost: ${processed_request.estimated_cost:.2f}" if processed_request.estimated_cost else "💰 Cost: Calculating...")
        print(f"🚛 Assigned Truck: {processed_request.assigned_truck_id}" if processed_request.assigned_truck_id else "🚛 Truck: Searching...")
        print(f"📍 Status: {processed_request.status}")
        
        if processed_request.allocation_reasoning:
            print(f"🧠 AI Reasoning: {processed_request.allocation_reasoning}")
    
    print()
    
    # Demo request 2: Regular furniture delivery
    print("📦 DEMO REQUEST 2: Furniture Delivery")
    print("-" * 40)
    
    furniture_request = {
        "customer_name": "Johnson Family",
        "customer_phone": "+1-555-HOME-123",
        "description": "Living room furniture set - sofa, coffee table, lamp",
        "weight_kg": 280.0,
        "volume_m3": 8.5,
        "priority": "normal",
        "pickup_address": "Furniture Warehouse, Queens, NY",
        "delivery_address": "Residential Home, Staten Island, NY",
        "delivery_deadline": (datetime.now() + timedelta(days=2)).isoformat(),
        "special_instructions": "Call customer 30 minutes before arrival"
    }
    
    print(f"Customer: {furniture_request['customer_name']}")
    print(f"Description: {furniture_request['description']}")
    print(f"Priority: {furniture_request['priority'].upper()}")
    print(f"Weight: {furniture_request['weight_kg']}kg, Volume: {furniture_request['volume_m3']}m³")
    print()
    
    request2 = await request_processor.submit_request(furniture_request)
    print(f"✅ Request submitted: {request2.id}")
    print("🤖 AI is analyzing the request...")
    
    await asyncio.sleep(3)
    
    processed_request2 = request_processor.get_request(request2.id)
    if processed_request2:
        print(f"📊 AI Analysis Results:")
        if processed_request2.ai_analysis:
            analysis = processed_request2.ai_analysis
            print(f"   Risk Level: {analysis.get('risk_level', 'N/A').upper()}")
            print(f"   Complexity Score: {analysis.get('complexity_score', 'N/A')}/10")
        
        print(f"💰 Estimated Cost: ${processed_request2.estimated_cost:.2f}" if processed_request2.estimated_cost else "💰 Cost: Calculating...")
        print(f"🚛 Assigned Truck: {processed_request2.assigned_truck_id}" if processed_request2.assigned_truck_id else "🚛 Truck: Searching...")
        print(f"📍 Status: {processed_request2.status}")
    
    print()
    
    # Summary
    print("📊 SYSTEM SUMMARY")
    print("-" * 40)
    
    all_requests = request_processor.get_all_requests()
    print(f"Total Requests Processed: {len(all_requests)}")
    
    status_counts = {}
    total_revenue = 0
    
    for req in all_requests:
        status_counts[req.status] = status_counts.get(req.status, 0) + 1
        if req.estimated_cost:
            total_revenue += req.estimated_cost
    
    for status, count in status_counts.items():
        print(f"   {status}: {count}")
    
    print(f"Total Estimated Revenue: ${total_revenue:.2f}")
    print()
    
    print("🎯 KEY FEATURES DEMONSTRATED:")
    print("✅ AI-powered request analysis and risk assessment")
    print("✅ Automatic truck allocation based on capacity and location")
    print("✅ Dynamic cost estimation with priority-based pricing")
    print("✅ Real-time status tracking and updates")
    print("✅ Special handling requirements detection")
    print("✅ Intelligent reasoning and decision explanations")
    print()
    
    print("🌐 ACCESS THE SYSTEM:")
    print("   Frontend: http://localhost:3000/requests")
    print("   API Docs: http://localhost:8000/docs")
    print("   Start API: python -m uvicorn src.api.main:app --reload")
    print("   Start Frontend: cd frontend && npm run dev")

if __name__ == "__main__":
    asyncio.run(demo_request_system())