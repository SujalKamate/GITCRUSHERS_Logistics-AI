#!/usr/bin/env python3
"""
Deployment Status Checker
Verifies that deployed services are working correctly
"""

import requests
import json
import sys
from urllib.parse import urljoin

def check_api_health(base_url):
    """Check if API is healthy"""
    try:
        health_url = urljoin(base_url, "/health")
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Health Check: {health_url}")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Trucks: {data.get('trucks', 0)}")
            print(f"   Loads: {data.get('loads', 0)}")
            return True
        else:
            print(f"❌ API Health Check Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API Health Check Error: {e}")
        return False

def check_customer_app(base_url):
    """Check if customer app is accessible"""
    try:
        customer_url = urljoin(base_url, "/customer-app/")
        response = requests.get(customer_url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Customer App: {customer_url}")
            return True
        else:
            print(f"❌ Customer App Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Customer App Error: {e}")
        return False

def check_driver_app(base_url):
    """Check if driver app is accessible"""
    try:
        driver_url = urljoin(base_url, "/driver-app/")
        response = requests.get(driver_url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Driver App: {driver_url}")
            return True
        else:
            print(f"❌ Driver App Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Driver App Error: {e}")
        return False

def check_frontend(frontend_url):
    """Check if frontend is accessible"""
    try:
        response = requests.get(frontend_url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Frontend Dashboard: {frontend_url}")
            return True
        else:
            print(f"❌ Frontend Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend Error: {e}")
        return False

def main():
    print("🔍 Deployment Status Checker")
    print("=" * 40)
    
    # Get URLs from user input or environment
    api_url = input("Enter your API URL (e.g., https://your-app.railway.app): ").strip()
    if not api_url:
        print("❌ API URL is required")
        sys.exit(1)
    
    frontend_url = input("Enter your Frontend URL (e.g., https://your-app.vercel.app): ").strip()
    
    print(f"\n🚀 Checking deployment status...")
    print(f"API Base URL: {api_url}")
    if frontend_url:
        print(f"Frontend URL: {frontend_url}")
    print()
    
    # Check API components
    api_healthy = check_api_health(api_url)
    customer_ok = check_customer_app(api_url)
    driver_ok = check_driver_app(api_url)
    
    # Check frontend if provided
    frontend_ok = True
    if frontend_url:
        frontend_ok = check_frontend(frontend_url)
    
    print("\n📊 Summary:")
    print("=" * 20)
    
    if api_healthy and customer_ok and driver_ok and frontend_ok:
        print("🎉 All services are working correctly!")
        print("\n🔗 Your live URLs:")
        if frontend_url:
            print(f"📊 Dashboard: {frontend_url}")
        print(f"📱 Customer App: {api_url}/customer-app/")
        print(f"🚛 Driver App: {api_url}/driver-app/")
        print(f"🔧 API Health: {api_url}/health")
        
        print("\n✨ Your Logistics AI system is live and ready to use!")
        
    else:
        print("⚠️  Some services have issues. Please check the errors above.")
        
        if not api_healthy:
            print("   - Fix API deployment first")
        if not customer_ok:
            print("   - Check customer app static files")
        if not driver_ok:
            print("   - Check driver app static files")
        if not frontend_ok:
            print("   - Check frontend deployment")

if __name__ == "__main__":
    main()