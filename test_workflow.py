#!/usr/bin/env python3
"""
Test script to verify the complete delivery request workflow.
"""

import asyncio
import json
import time
from datetime import datetime
import requests

API_BASE = "http://localhost:8000"

def test_create_request():
    """Test creating a new delivery request."""
    print("🧪 Testing request creation...")
    
    request_data = {
        "customer_name": "Workflow Test Customer",
        "customer_phone": "+1555123456",
        "description": "Test package for workflow verification",
        "weight_kg": 8.5,
        "priority": "high",
        "pickup_address": "100 Test Street, New York, NY",
        "delivery_address": "200 Demo Avenue, Brooklyn, NY",
        "fragile": True,
        "temperature_controlled": False,
        "special_instructions": "This is a test request"
    }
    
    response = requests.post(f"{API_BASE}/api/requests/", json=request_data)
    
    if response.status_code == 200:
        request = response.json()
        print(f"✅ Request created: {request['id']}")
        print(f"   Status: {request['status']}")
        print(f"   Customer: {request['customer_name']}")
        return request['id']
    else:
        print(f"❌ Failed to create request: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def test_get_pending_requests():
    """Test getting pending requests."""
    print("\n🧪 Testing pending requests retrieval...")
    
    response = requests.get(f"{API_BASE}/api/requests/?status=pending")
    
    if response.status_code == 200:
        requests_list = response.json()
        print(f"✅ Found {len(requests_list)} pending requests")
        for req in requests_list:
            print(f"   - {req['id']}: {req['customer_name']} ({req['status']})")
        return requests_list
    else:
        print(f"❌ Failed to get pending requests: {response.status_code}")
        return []

def test_process_request(request_id):
    """Test processing a specific request."""
    print(f"\n🧪 Testing request processing for {request_id}...")
    
    response = requests.put(f"{API_BASE}/api/requests/{request_id}/process")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Processing started: {result['message']}")
        
        # Wait for processing to complete
        print("⏳ Waiting for AI processing...")
        for i in range(10):  # Wait up to 10 seconds
            time.sleep(1)
            status_response = requests.get(f"{API_BASE}/api/requests/{request_id}")
            if status_response.status_code == 200:
                request = status_response.json()
                print(f"   Status: {request['status']}")
                
                if request['status'] == 'assigned':
                    print(f"✅ Request processed successfully!")
                    print(f"   Assigned truck: {request['assigned_truck_id']}")
                    print(f"   Estimated cost: ${request['estimated_cost']:.2f}")
                    print(f"   AI analysis: {request['ai_analysis']['risk_level']} risk")
                    return True
                elif request['status'] == 'failed':
                    print(f"❌ Request processing failed")
                    return False
        
        print("⏰ Processing timeout - request may still be processing")
        return False
    else:
        print(f"❌ Failed to start processing: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_request_summary():
    """Test getting request summary."""
    print("\n🧪 Testing request summary...")
    
    response = requests.get(f"{API_BASE}/api/requests/summary")
    
    if response.status_code == 200:
        summary = response.json()
        print("✅ Request summary:")
        print(f"   Total requests: {summary['total_requests']}")
        print(f"   Pending: {summary['pending_requests']}")
        print(f"   Assigned: {summary['assigned_requests']}")
        print(f"   Total revenue: ${summary['total_estimated_revenue']:.2f}")
        return summary
    else:
        print(f"❌ Failed to get summary: {response.status_code}")
        return None

def main():
    """Run the complete workflow test."""
    print("🚀 Starting Delivery Request Workflow Test")
    print("=" * 50)
    
    # Test 1: Create a new request
    request_id = test_create_request()
    if not request_id:
        print("❌ Workflow test failed at request creation")
        return
    
    # Test 2: Verify it appears in pending requests
    pending_requests = test_get_pending_requests()
    if not any(req['id'] == request_id for req in pending_requests):
        print(f"❌ Request {request_id} not found in pending list")
        return
    
    # Test 3: Process the request
    success = test_process_request(request_id)
    if not success:
        print("❌ Workflow test failed at request processing")
        return
    
    # Test 4: Check summary
    summary = test_request_summary()
    if not summary:
        print("❌ Workflow test failed at summary retrieval")
        return
    
    print("\n" + "=" * 50)
    print("🎉 Workflow test completed successfully!")
    print("✅ All components are working correctly:")
    print("   - Customer request submission")
    print("   - Pending request visibility")
    print("   - Manual AI processing trigger")
    print("   - Request status updates")
    print("   - Summary statistics")

if __name__ == "__main__":
    main()