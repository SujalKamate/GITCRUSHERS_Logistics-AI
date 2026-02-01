#!/usr/bin/env python3
"""
Quick Demo URL Tester
Tests your deployed demo URL to ensure everything works
"""

import requests
import sys
import time

def test_demo_url():
    """Test the demo URL"""
    print("🔍 Demo URL Tester")
    print("=" * 30)
    
    # Get URL from user
    demo_url = input("Enter your Railway demo URL (e.g., https://logistics-ai-demo-production.up.railway.app): ").strip()
    
    if not demo_url:
        print("❌ Demo URL is required")
        return
    
    if not demo_url.startswith('http'):
        demo_url = 'https://' + demo_url
    
    print(f"\n🚀 Testing: {demo_url}")
    print("-" * 50)
    
    tests = [
        ("Demo Landing Page", ""),
        ("Demo Page Direct", "/demo/"),
        ("Customer App", "/customer-app/"),
        ("Driver App", "/driver-app/"),
        ("API Health", "/health"),
    ]
    
    results = []
    
    for test_name, endpoint in tests:
        url = demo_url + endpoint
        try:
            print(f"Testing {test_name}... ", end="")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print("✅ PASS")
                results.append(True)
                
                # Special handling for health endpoint
                if endpoint == "/health":
                    try:
                        data = response.json()
                        print(f"   Status: {data.get('status', 'unknown')}")
                        print(f"   Trucks: {data.get('trucks', 0)}")
                        print(f"   Loads: {data.get('loads', 0)}")
                    except:
                        pass
            else:
                print(f"❌ FAIL ({response.status_code})")
                results.append(False)
                
        except Exception as e:
            print(f"❌ ERROR ({str(e)[:50]})")
            results.append(False)
        
        time.sleep(1)  # Small delay between tests
    
    # Summary
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print(f"\n✨ Your demo URL is ready: {demo_url}")
        print("\n📋 What judges will find:")
        print("   • Professional landing page with system overview")
        print("   • Interactive tabs for all three interfaces")
        print("   • Complete workflow demonstration")
        print("   • Real-time AI processing and notifications")
        print("\n🎯 Share this URL with judges to showcase your complete system!")
        
    else:
        print(f"⚠️  {passed}/{total} tests passed")
        print("\n🔧 Issues found:")
        
        for i, (test_name, endpoint) in enumerate(tests):
            if not results[i]:
                print(f"   • {test_name}: {demo_url + endpoint}")
        
        print("\n💡 Troubleshooting:")
        print("   1. Wait 2-3 minutes for services to fully start")
        print("   2. Check Railway deployment logs")
        print("   3. Verify environment variables are set")
        print("   4. Ensure GROQ_API_KEY is correct")

def main():
    try:
        test_demo_url()
    except KeyboardInterrupt:
        print("\n\n👋 Test cancelled")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()