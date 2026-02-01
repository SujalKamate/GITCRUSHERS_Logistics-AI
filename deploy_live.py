#!/usr/bin/env python3
"""
Live Deployment Script for Logistics AI System
Automates the complete deployment process to get live URLs
"""

import os
import json
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def print_banner():
    print("🚀 Logistics AI System - Live Deployment")
    print("=" * 50)
    print("Get your system live with public URLs in minutes!")
    print()

def check_git_status():
    """Check git status and ensure code is committed"""
    try:
        # Check if there are uncommitted changes
        result = subprocess.run(["git", "status", "--porcelain"], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            print("⚠️  You have uncommitted changes:")
            print(result.stdout)
            
            commit = input("Would you like to commit all changes? (y/n): ").lower()
            if commit == 'y':
                subprocess.run(["git", "add", "."])
                commit_msg = input("Enter commit message (or press Enter for default): ").strip()
                if not commit_msg:
                    commit_msg = "Deploy: Prepare for production deployment"
                
                subprocess.run(["git", "commit", "-m", commit_msg])
                print("✅ Changes committed")
            else:
                print("❌ Please commit your changes before deploying")
                return False
        
        # Check if we have a remote repository
        result = subprocess.run(["git", "remote", "-v"], 
                              capture_output=True, text=True)
        
        if not result.stdout.strip():
            print("❌ No git remote found. Please push your code to GitHub first:")
            print("   1. Create a repository on GitHub")
            print("   2. git remote add origin https://github.com/username/repo.git")
            print("   3. git push -u origin main")
            return False
        
        print("✅ Git repository is ready for deployment")
        return True
        
    except Exception as e:
        print(f"❌ Git check failed: {e}")
        return False

def get_groq_api_key():
    """Get or validate Groq API key"""
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("🔑 Groq API Key Required")
        print("You need a Groq API key for the AI features to work.")
        print("Get one free at: https://console.groq.com/keys")
        
        api_key = input("Enter your Groq API key: ").strip()
        
        if not api_key:
            print("❌ API key is required for deployment")
            return None
        
        # Save to .env file
        with open(".env", "a") as f:
            f.write(f"\nGROQ_API_KEY={api_key}\n")
        
        print("✅ API key saved to .env file")
    
    return api_key

def deploy_to_railway():
    """Deploy API to Railway"""
    print("\n🚄 Deploying API to Railway...")
    print("=" * 35)
    
    print("1. Go to: https://railway.app")
    print("2. Sign up/Login with GitHub")
    print("3. Click 'New Project' → 'Deploy from GitHub repo'")
    print("4. Select your repository")
    print("5. Configure the service:")
    print("   - Service Name: logistics-ai-api")
    print("   - Root Directory: (leave empty)")
    print("   - Start Command: uvicorn src.api.main:app --host 0.0.0.0 --port $PORT")
    
    print("\n6. Add Environment Variables:")
    api_key = get_groq_api_key()
    if not api_key:
        return None
    
    print(f"   GROQ_API_KEY = {api_key}")
    print("   PORT = 8000")
    print("   CORS_ORIGINS = *")
    print("   PYTHONPATH = /app")
    
    print("\n7. Click 'Deploy'")
    
    # Open Railway in browser
    open_browser = input("\nOpen Railway in browser? (y/n): ").lower()
    if open_browser == 'y':
        webbrowser.open("https://railway.app")
    
    # Wait for user to complete deployment
    input("\nPress Enter after you've deployed to Railway and have your URL...")
    
    api_url = input("Enter your Railway API URL (e.g., https://logistics-ai-production.up.railway.app): ").strip()
    
    if not api_url:
        print("❌ API URL is required")
        return None
    
    # Test the API
    print(f"\n🔍 Testing API at {api_url}...")
    try:
        import requests
        response = requests.get(f"{api_url}/health", timeout=30)
        if response.status_code == 200:
            print("✅ API is working!")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Trucks: {data.get('trucks', 0)}")
            return api_url
        else:
            print(f"❌ API test failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ API test error: {e}")
        print("   The API might still be starting up. You can continue and test later.")
        return api_url

def deploy_to_vercel(api_url):
    """Deploy Frontend to Vercel"""
    print("\n🎨 Deploying Frontend to Vercel...")
    print("=" * 38)
    
    print("1. Go to: https://vercel.com")
    print("2. Sign up/Login with GitHub")
    print("3. Click 'New Project' → 'Import Git Repository'")
    print("4. Select your repository")
    print("5. Configure the project:")
    print("   - Framework Preset: Next.js")
    print("   - Root Directory: GITCRUSHERS_Logistics-AI/frontend")
    print("   - Build Command: npm run build")
    print("   - Output Directory: .next")
    
    print("\n6. Add Environment Variables:")
    print(f"   NEXT_PUBLIC_API_BASE_URL = {api_url}")
    print(f"   NEXT_PUBLIC_WS_BASE_URL = {api_url.replace('https://', 'wss://').replace('http://', 'ws://')}")
    
    print("\n7. Click 'Deploy'")
    
    # Open Vercel in browser
    open_browser = input("\nOpen Vercel in browser? (y/n): ").lower()
    if open_browser == 'y':
        webbrowser.open("https://vercel.com")
    
    # Wait for user to complete deployment
    input("\nPress Enter after you've deployed to Vercel and have your URL...")
    
    frontend_url = input("Enter your Vercel Frontend URL (e.g., https://logistics-ai.vercel.app): ").strip()
    
    if not frontend_url:
        print("❌ Frontend URL is required")
        return None
    
    # Test the frontend
    print(f"\n🔍 Testing Frontend at {frontend_url}...")
    try:
        import requests
        response = requests.get(frontend_url, timeout=30)
        if response.status_code == 200:
            print("✅ Frontend is working!")
            return frontend_url
        else:
            print(f"❌ Frontend test failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Frontend test error: {e}")
        print("   The frontend might still be building. You can continue and test later.")
        return frontend_url

def update_cors_settings(api_url, frontend_url):
    """Update CORS settings in the API"""
    print(f"\n🔧 Updating CORS settings...")
    
    print("You need to update your Railway deployment with the correct CORS origins:")
    print(f"   CORS_ORIGINS = {frontend_url}")
    print("\n1. Go to your Railway project")
    print("2. Click on your service")
    print("3. Go to 'Variables' tab")
    print("4. Update CORS_ORIGINS with your frontend URL")
    print("5. The service will automatically redeploy")
    
    input("Press Enter after updating CORS settings...")

def show_final_results(api_url, frontend_url):
    """Show the final deployment results"""
    print("\n🎉 DEPLOYMENT COMPLETE!")
    print("=" * 50)
    
    print("Your Logistics AI System is now LIVE with these URLs:")
    print()
    
    print("📊 LOGISTICS DASHBOARD (for logistics team):")
    print(f"   {frontend_url}")
    print()
    
    print("📱 CUSTOMER MOBILE APP (for customers):")
    print(f"   {api_url}/customer-app/")
    print()
    
    print("🚛 DRIVER MOBILE APP (for drivers):")
    print(f"   {api_url}/driver-app/")
    print()
    
    print("🔧 API HEALTH CHECK:")
    print(f"   {api_url}/health")
    print()
    
    print("✨ Your system is now accessible worldwide!")
    print("Share these URLs with your users to start using the system.")
    
    # Test all URLs
    test_all = input("\nWould you like to test all URLs now? (y/n): ").lower()
    if test_all == 'y':
        test_deployment(api_url, frontend_url)

def test_deployment(api_url, frontend_url):
    """Test all deployed services"""
    print("\n🔍 Testing all services...")
    
    try:
        import requests
        
        # Test API health
        print(f"Testing API health: {api_url}/health")
        response = requests.get(f"{api_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ API Health Check: PASSED")
        else:
            print(f"❌ API Health Check: FAILED ({response.status_code})")
        
        # Test customer app
        print(f"Testing Customer App: {api_url}/customer-app/")
        response = requests.get(f"{api_url}/customer-app/", timeout=10)
        if response.status_code == 200:
            print("✅ Customer App: PASSED")
        else:
            print(f"❌ Customer App: FAILED ({response.status_code})")
        
        # Test driver app
        print(f"Testing Driver App: {api_url}/driver-app/")
        response = requests.get(f"{api_url}/driver-app/", timeout=10)
        if response.status_code == 200:
            print("✅ Driver App: PASSED")
        else:
            print(f"❌ Driver App: FAILED ({response.status_code})")
        
        # Test frontend
        print(f"Testing Frontend: {frontend_url}")
        response = requests.get(frontend_url, timeout=10)
        if response.status_code == 200:
            print("✅ Frontend Dashboard: PASSED")
        else:
            print(f"❌ Frontend Dashboard: FAILED ({response.status_code})")
        
        print("\n🎯 All tests completed!")
        
    except Exception as e:
        print(f"❌ Testing error: {e}")

def main():
    print_banner()
    
    # Check requirements
    if not check_git_status():
        sys.exit(1)
    
    # Deploy API to Railway
    api_url = deploy_to_railway()
    if not api_url:
        print("❌ API deployment failed")
        sys.exit(1)
    
    # Deploy Frontend to Vercel
    frontend_url = deploy_to_vercel(api_url)
    if not frontend_url:
        print("❌ Frontend deployment failed")
        sys.exit(1)
    
    # Update CORS settings
    update_cors_settings(api_url, frontend_url)
    
    # Show final results
    show_final_results(api_url, frontend_url)
    
    print("\n🚀 Congratulations! Your Logistics AI System is now live!")

if __name__ == "__main__":
    main()