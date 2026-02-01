#!/usr/bin/env python3
"""
Startup script for the complete Logistics AI system.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Print startup banner."""
    print("🚀 LOGISTICS AI - COMPLETE SYSTEM STARTUP")
    print("="*60)
    print("Starting all components of the delivery request system...")
    print()

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    # Check Python packages
    try:
        import uvicorn
        import fastapi
        import geopy
        print("✅ Python dependencies installed")
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False
    
    # Check Node.js for frontend
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Node.js/npm available")
        else:
            print("⚠️  Node.js/npm not found - frontend may not work")
    except FileNotFoundError:
        print("⚠️  Node.js/npm not found - frontend may not work")
    
    return True

def start_api_server():
    """Start the API server."""
    print("🔧 Starting API server...")
    print("   URL: http://localhost:8000")
    print("   Docs: http://localhost:8000/docs")
    print()
    
    # Start API server in background
    api_process = subprocess.Popen([
        sys.executable, '-m', 'uvicorn', 
        'src.api.main:app', 
        '--reload', 
        '--host', '0.0.0.0', 
        '--port', '8000'
    ])
    
    return api_process

def start_customer_app():
    """Start the customer app server."""
    print("📱 Starting customer app...")
    print("   URL: http://localhost:3001")
    print()
    
    # Start customer app server in background
    customer_process = subprocess.Popen([
        sys.executable, 
        'customer-app/server.py'
    ])
    
    return customer_process

def print_instructions():
    """Print usage instructions."""
    print("🌐 SYSTEM ACCESS POINTS")
    print("-" * 40)
    print("📱 Customer App: http://localhost:3001")
    print("   - Mobile interface for customers to request deliveries")
    print("   - Beautiful, responsive design")
    print("   - Real-time submission to AI system")
    print()
    print("📊 Dashboard: http://localhost:3000/requests")
    print("   - Internal logistics dashboard")
    print("   - View pending requests from customers")
    print("   - AI processing and truck allocation")
    print("   - Real-time status monitoring")
    print()
    print("🔧 API Server: http://localhost:8000")
    print("   - RESTful API for all operations")
    print("   - Interactive docs at /docs")
    print("   - WebSocket for real-time updates")
    print()
    
    print("🎯 WORKFLOW")
    print("-" * 40)
    print("1. Customer submits request via mobile app (port 3001)")
    print("2. Request appears in dashboard as 'Pending' (port 3000)")
    print("3. AI processes request and allocates truck automatically")
    print("4. Status updates to 'Assigned' with cost and timing")
    print("5. Customer receives updates via SMS/email")
    print()
    
    print("🚀 NEXT STEPS")
    print("-" * 40)
    print("1. Open customer app: http://localhost:3001")
    print("2. Submit a test delivery request")
    print("3. Open dashboard: http://localhost:3000/requests")
    print("4. Watch AI process the request automatically")
    print()
    
    print("💡 FRONTEND SETUP (Optional)")
    print("-" * 40)
    print("To run the full dashboard frontend:")
    print("1. Open new terminal")
    print("2. cd frontend")
    print("3. npm install")
    print("4. npm run dev")
    print("5. Open http://localhost:3000")
    print()

def main():
    """Main startup function."""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print("🚀 Starting system components...")
    print()
    
    # Start API server
    api_process = start_api_server()
    time.sleep(3)  # Give API time to start
    
    # Start customer app
    customer_process = start_customer_app()
    time.sleep(2)  # Give customer app time to start
    
    print("✅ All components started successfully!")
    print()
    
    # Print instructions
    print_instructions()
    
    print("Press Ctrl+C to stop all services")
    print("="*60)
    
    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down system...")
        
        # Terminate processes
        if api_process:
            api_process.terminate()
        if customer_process:
            customer_process.terminate()
        
        print("👋 System stopped. Thank you!")

if __name__ == "__main__":
    main()