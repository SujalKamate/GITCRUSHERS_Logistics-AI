#!/usr/bin/env python3
"""
Two-Link Deployment Script for Logistics AI System
Deploy Backend (Railway) + Frontend (Vercel) separately
"""

import os
import json
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def print_banner():
    print("🚀 Logistics AI System - Two-Link Deployment")
    print("=" * 55)
    print("Deploy Backend + Frontend separately for clean architecture!")
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
                    commit_msg = "Deploy: Two-link deployment ready"
                
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
        print("You need a 