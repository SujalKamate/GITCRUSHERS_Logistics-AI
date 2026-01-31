#!/usr/bin/env python3
"""
System setup script for Logistics AI Control System.
Run this to configure and initialize the complete system.
"""
import os
import sys
import asyncio
import subprocess
from pathlib import Path

def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_dependencies():
    """Install Python dependencies."""
    print_header("INSTALLING DEPENDENCIES")
    
    try:
        # Install main dependencies
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        
        # Install additional production dependencies
        additional_deps = [
            "asyncpg",  # PostgreSQL async driver
            "psycopg2-binary",  # PostgreSQL sync driver
            "redis",  # For caching (optional)
            "celery",  # For background tasks (optional)
        ]
        
        for dep in additional_deps:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
                print(f"✅ Installed {dep}")
            except subprocess.CalledProcessError:
                print(f"⚠️  Failed to install {dep} (optional)")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Set up environment configuration."""
    print_header("ENVIRONMENT SETUP")
    
    env_file = Path(".env")
    env_production = Path(".env.production")
    
    if not env_file.exists():
        if env_production.exists():
            # Copy production template
            with open(env_production, 'r') as src, open(env_file, 'w') as dst:
                dst.write(src.read())
            print("✅ Created .env from production template")
        else:
            # Create basic .env
            env_content = """# Logistics AI Environment Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/logistics_ai
XAI_API_KEY=
GROK_MODEL=grok-beta
LLM_TEMPERATURE=0.7
API_PORT=8000
LOG_LEVEL=INFO
"""
            with open(env_file, 'w') as f:
                f.write(env_content)
            print("✅ Created basic .env file")
    else:
        print("✅ .env file already exists")
    
    # Check for API key
    with open(env_file, 'r') as f:
        content = f.read()
        if "XAI_API_KEY=" in content and not "XAI_API_KEY=your_" in content:
            api_key_line = [line for line in content.split('\n') if line.startswith('XAI_API_KEY=')]
            if api_key_line and len(api_key_line[0].split('=')[1].strip()) > 10:
                print("✅ xAI API key configured")
            else:
                print("⚠️  xAI API key not configured - will use fallback mode")
        else:
            print("⚠️  xAI API key not configured - will use fallback mode")

def check_database():
    """Check database connectivity."""
    print_header("DATABASE CHECK")
    
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        # Try to connect to PostgreSQL
        db_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/logistics_ai")
        parsed = urlparse(db_url)
        
        try:
            # Try connecting to postgres database first
            postgres_url = f"postgresql://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port}/postgres"
            conn = psycopg2.connect(postgres_url)
            conn.close()
            print("✅ PostgreSQL server accessible")
            return True
        except psycopg2.OperationalError:
            print("❌ Cannot connect to PostgreSQL server")
            print("   Please ensure PostgreSQL is running and accessible")
            print(f"   Connection string: {parsed.hostname}:{parsed.port}")
            return False
            
    except ImportError:
        print("❌ psycopg2 not installed")
        return False

async def initialize_database():
    """Initialize the database."""
    print_header("DATABASE INITIALIZATION")
    
    try:
        from database_setup import init_database
        await init_database()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def test_api_server():
    """Test if the API server can start."""
    print_header("API SERVER TEST")
    
    try:
        # Import main components to check for errors
        from src.api.main import app
        from src.models import Truck, Load
        from src.reasoning.grok_client import get_groq_client
        
        print("✅ API imports successful")
        
        # Test Groq client
        client = get_groq_client()
        if client.is_available:
            print("✅ Grok client configured")
        else:
            print("⚠️  Grok client not available - using fallback mode")
        
        return True
    except Exception as e:
        print(f"❌ API server test failed: {e}")
        return False

def create_sample_data():
    """Create sample data for testing."""
    print_header("SAMPLE DATA CREATION")
    
    try:
        from src.api.services.simulation import simulation_service
        simulation_service.generate_initial_data(num_trucks=5)
        print("✅ Sample data created")
        return True
    except Exception as e:
        print(f"❌ Sample data creation failed: {e}")
        return False

def print_next_steps():
    """Print next steps for the user."""
    print_header("SETUP COMPLETE")
    
    print("🎉 System setup completed!")
    print("\nNext steps:")
    print("1. Configure your xAI API key in .env file:")
    print("   XAI_API_KEY=your_actual_api_key_here")
    print("\n2. Start the backend server:")
    print("   cd GITCRUSHERS_Logistics-AI")
    print("   python -m uvicorn src.api.main:app --reload --port 8000")
    print("\n3. Start the frontend (in another terminal):")
    print("   cd frontend")
    print("   npm install")
    print("   npm run dev")
    print("\n4. Open your browser to:")
    print("   http://localhost:3000")
    print("\n5. Test the AI control loop:")
    print("   - Click 'Start Control Loop' in the AI Control page")
    print("   - Monitor the fleet on the Fleet Management page")

async def main():
    """Main setup function."""
    print_header("LOGISTICS AI CONTROL SYSTEM SETUP")
    print("This script will configure and initialize the complete system.")
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Setup environment
    setup_environment()
    
    # Check database
    db_ok = check_database()
    
    # Initialize database if available
    if db_ok:
        db_init_ok = await initialize_database()
    else:
        print("⚠️  Skipping database initialization - will use in-memory storage")
        db_init_ok = False
    
    # Test API server
    api_ok = test_api_server()
    
    # Create sample data
    if api_ok:
        create_sample_data()
    
    # Print results
    print_header("SETUP SUMMARY")
    print(f"✅ Dependencies: Installed")
    print(f"✅ Environment: Configured")
    print(f"{'✅' if db_ok else '⚠️ '} Database: {'Ready' if db_ok else 'Fallback mode'}")
    print(f"{'✅' if api_ok else '❌'} API Server: {'Ready' if api_ok else 'Failed'}")
    
    if api_ok:
        print_next_steps()
        return True
    else:
        print("\n❌ Setup incomplete. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)