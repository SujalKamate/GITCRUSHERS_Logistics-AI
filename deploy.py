#!/usr/bin/env python3
"""
Deployment Helper Script for Logistics AI System
Helps prepare and deploy the system to get live URLs
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def print_banner():
    print("🚀 Logistics AI System - Deployment Helper")
    print("=" * 50)
    print()

def check_requirements():
    """Check if all requirements are met"""
    print("📋 Checking requirements...")
    
    # Check if git is available
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        print("✅ Git is available")
    except:
        print("❌ Git is not available. Please install Git first.")
        return False
    
    # Check if we're in a git repository
    if not os.path.exists(".git"):
        print("❌ Not in a git repository. Please initialize git first:")
        print("   git init")
        print("   git add .")
        print("   git commit -m 'Initial commit'")
        return False
    else:
        print("✅ Git repository detected")
    
    # Check if Groq API key is available
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print("⚠️  GROQ_API_KEY not found in environment")
        print("   You'll need to set this in your deployment platform")
    else:
        print("✅ GROQ_API_KEY found")
    
    return True

def create_deployment_files():
    """Create necessary deployment configuration files"""
    print("\n📝 Creating deployment configuration files...")
    
    # Railway configuration
    railway_config = {
        "build": {
            "builder": "NIXPACKS"
        },
        "deploy": {
            "startCommand": "pip install -r requirements.txt && uvicorn src.api.main:app --host 0.0.0.0 --port $PORT",
            "healthcheckPath": "/health",
            "healthcheckTimeout": 100,
            "restartPolicyType": "on_failure",
            "restartPolicyMaxRetries": 10
        }
    }
    
    with open("railway.json", "w") as f:
        json.dump(railway_config, f, indent=2)
    print("✅ Created railway.json")
    
    # Vercel configuration
    vercel_config = {
        "builds": [
            {
                "src": "frontend/package.json",
                "use": "@vercel/next"
            }
        ],
        "routes": [
            {
                "src": "/(.*)",
                "dest": "frontend/$1"
            }
        ]
    }
    
    with open("vercel.json", "w") as f:
        json.dump(vercel_config, f, indent=2)
    print("✅ Created vercel.json")
    
    # Heroku Procfile
    with open("Procfile", "w") as f:
        f.write("web: uvicorn src.api.main:app --host 0.0.0.0 --port $PORT\n")
    print("✅ Created Procfile")
    
    # Runtime specification for Heroku
    with open("runtime.txt", "w") as f:
        f.write("python-3.11.0\n")
    print("✅ Created runtime.txt")

def show_deployment_options():
    """Show available deployment options"""
    print("\n🚀 Deployment Options:")
    print()
    
    print("1. 🚄 Railway + Vercel (Recommended)")
    print("   - API: Railway (Free tier: 500 hours/month)")
    print("   - Frontend: Vercel (Free tier: 100GB bandwidth)")
    print("   - Time: ~30 minutes")
    print("   - Cost: Free for development")
    print()
    
    print("2. 🎨 Render (All-in-One)")
    print("   - Both API and Frontend on Render")
    print("   - Time: ~45 minutes")
    print("   - Cost: Free tier available")
    print()
    
    print("3. 🟣 Heroku (Classic)")
    print("   - Reliable but paid")
    print("   - Time: ~1 hour")
    print("   - Cost: $7/month per service")
    print()

def show_railway_steps():
    """Show Railway deployment steps"""
    print("📋 Railway Deployment Steps:")
    print()
    print("1. Go to https://railway.app")
    print("2. Sign up/Login with GitHub")
    print("3. Click 'New Project' → 'Deploy from GitHub repo'")
    print("4. Select your repository")
    print("5. Configure service:")
    print("   - Name: logistics-ai-api")
    print("   - Start Command: uvicorn src.api.main:app --host 0.0.0.0 --port $PORT")
    print("6. Add Environment Variables:")
    print("   - GROQ_API_KEY: your_groq_api_key")
    print("   - PORT: 8000")
    print("   - CORS_ORIGINS: *")
    print("7. Deploy and get your URL!")
    print()

def show_vercel_steps():
    """Show Vercel deployment steps"""
    print("📋 Vercel Deployment Steps:")
    print()
    print("1. Go to https://vercel.com")
    print("2. Sign up/Login with GitHub")
    print("3. Click 'New Project' → 'Import Git Repository'")
    print("4. Select your repository")
    print("5. Configure:")
    print("   - Framework: Next.js")
    print("   - Root Directory: frontend")
    print("   - Build Command: npm run build")
    print("6. Add Environment Variables:")
    print("   - NEXT_PUBLIC_API_BASE_URL: https://your-railway-url.railway.app")
    print("   - NEXT_PUBLIC_WS_BASE_URL: wss://your-railway-url.railway.app")
    print("7. Deploy and get your URL!")
    print()

def show_final_urls():
    """Show what the final URLs will look like"""
    print("🎉 Your Final URLs will be:")
    print()
    print("📊 Logistics Dashboard:")
    print("   https://your-app-name.vercel.app")
    print("   (For logistics team to manage requests)")
    print()
    print("📱 Customer Mobile App:")
    print("   https://your-api-name.railway.app/customer-app/")
    print("   (For customers to submit delivery requests)")
    print()
    print("🚛 Driver Mobile App:")
    print("   https://your-api-name.railway.app/driver-app/")
    print("   (For drivers to receive and manage deliveries)")
    print()
    print("🔧 API Health Check:")
    print("   https://your-api-name.railway.app/health")
    print("   (To verify system is running)")
    print()

def main():
    print_banner()
    
    if not check_requirements():
        print("\n❌ Requirements not met. Please fix the issues above and try again.")
        sys.exit(1)
    
    create_deployment_files()
    show_deployment_options()
    
    choice = input("Which deployment option would you like instructions for? (1/2/3): ").strip()
    
    if choice == "1":
        print("\n🚄 Railway + Vercel Deployment")
        print("=" * 40)
        show_railway_steps()
        show_vercel_steps()
    elif choice == "2":
        print("\n🎨 Render Deployment")
        print("=" * 25)
        print("1. Go to https://render.com")
        print("2. Create account and connect GitHub")
        print("3. Create Web Service for API")
        print("4. Create Static Site for Frontend")
        print("5. Configure environment variables")
    elif choice == "3":
        print("\n🟣 Heroku Deployment")
        print("=" * 25)
        print("1. Install Heroku CLI")
        print("2. heroku create your-api-name")
        print("3. heroku create your-frontend-name")
        print("4. Configure buildpacks and deploy")
    else:
        print("Invalid choice. Please run the script again.")
        sys.exit(1)
    
    show_final_urls()
    
    print("📚 For detailed instructions, see:")
    print("   - QUICK_DEPLOYMENT_GUIDE.md")
    print("   - DEPLOYMENT_PLAN.md")
    print()
    print("🚀 Happy deploying!")

if __name__ == "__main__":
    main()