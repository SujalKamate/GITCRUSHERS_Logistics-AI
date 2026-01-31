#!/usr/bin/env python3
"""
Script to configure Groq API key for LLM integration.
"""
import os
import sys
from pathlib import Path

def configure_api_key():
    """Configure the Groq API key."""
    print("🔑 Groq API Key Configuration")
    print("="*50)
    
    # Check if .env file exists
    env_file = Path(".env")
    
    print("\nTo get your Groq API key:")
    print("1. Visit: https://console.groq.com/keys")
    print("2. Sign up or log in (it's FREE!)")
    print("3. Click 'Create API Key'")
    print("4. Copy the key (starts with 'gsk_')")
    print("\n✨ Groq is FREE and FAST - perfect for development!")
    
    print("\nCurrent configuration:")
    
    # Check current API key
    current_key = os.getenv("GROQ_API_KEY", "")
    if current_key and len(current_key) > 10:
        masked_key = current_key[:8] + "..." + current_key[-4:]
        print(f"✅ API Key configured: {masked_key}")
    else:
        print("❌ No API key configured")
    
    # Ask user if they want to configure
    response = input("\nDo you want to configure your API key now? (y/n): ").lower().strip()
    
    if response != 'y':
        print("Configuration skipped. System will use fallback mode.")
        return False
    
    # Get API key from user
    print("\nEnter your Groq API key:")
    print("(The key will be saved to .env file)")
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Configuration cancelled.")
        return False
    
    if not api_key.startswith('gsk_'):
        print("⚠️  Warning: API key doesn't start with 'gsk_'. Are you sure this is correct?")
        confirm = input("Continue anyway? (y/n): ").lower().strip()
        if confirm != 'y':
            print("Configuration cancelled.")
            return False
    
    # Update .env file
    try:
        # Read existing .env content
        env_content = ""
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_content = f.read()
        
        # Update or add API key
        lines = env_content.split('\n')
        updated = False
        
        for i, line in enumerate(lines):
            if line.startswith('GROQ_API_KEY='):
                lines[i] = f'GROQ_API_KEY={api_key}'
                updated = True
                break
        
        if not updated:
            lines.append(f'GROQ_API_KEY={api_key}')
        
        # Write back to file
        with open(env_file, 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"✅ API key saved to {env_file}")
        
        # Test the configuration
        print("\nTesting API key...")
        test_api_key(api_key)
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to save API key: {e}")
        return False

def test_api_key(api_key):
    """Test the API key configuration."""
    try:
        # Set environment variable for testing
        os.environ['GROQ_API_KEY'] = api_key
        
        from src.reasoning.grok_client import get_groq_client
        
        client = get_groq_client()
        
        if client.is_available:
            print("✅ API key configuration successful!")
            print("🚀 Groq client is ready for use")
            
            # Try a simple test call
            try:
                response = client.complete(
                    prompt="Hello, this is a test. Please respond with 'API connection successful'.",
                    system_prompt="You are a test assistant."
                )
                
                if response.get("success"):
                    print("✅ API connection test successful!")
                    print(f"📝 Response: {response.get('content', '')[:100]}...")
                    print(f"🏃‍♂️ Model: {response.get('model', 'unknown')}")
                else:
                    print("⚠️  API key valid but connection test failed")
                    print("   This might be due to rate limits or network issues")
                    
            except Exception as e:
                print(f"⚠️  API key valid but test call failed: {e}")
                print("   The key should still work for normal operations")
        else:
            print("❌ API key configuration failed")
            print("   Please check that the key is correct")
            
    except Exception as e:
        print(f"❌ Failed to test API key: {e}")

def show_current_status():
    """Show current system status."""
    print("\n" + "="*50)
    print("📊 CURRENT SYSTEM STATUS")
    print("="*50)
    
    try:
        from src.reasoning.grok_client import get_groq_client
        
        client = get_groq_client()
        
        if client.is_available:
            print("🤖 AI Status: ✅ Groq LLM Available")
            stats = client.get_stats()
            print(f"📈 Model: {stats['model']}")
            print(f"📊 Requests: {stats['total_requests']}")
            print(f"🔢 Tokens: {stats['total_tokens_used']}")
        else:
            print("🤖 AI Status: ⚠️  Fallback Mode (No API Key)")
            print("   System will use rule-based analysis")
        
        # Check other components
        from src.api.services.state_manager import state_manager
        print(f"🚛 Fleet: {len(state_manager.trucks)} trucks")
        print(f"📦 Loads: {len(state_manager.loads)} loads")
        
    except Exception as e:
        print(f"❌ Status check failed: {e}")

def main():
    """Main function."""
    print("🚀 Logistics AI - Groq API Configuration")
    print("="*50)
    
    # Show current status
    show_current_status()
    
    # Configure API key
    success = configure_api_key()
    
    if success:
        print("\n🎉 Configuration complete!")
        print("\nNext steps:")
        print("1. Restart your API server if it's running")
        print("2. Test the system: python test_system.py")
        print("3. Start the server: python -m uvicorn src.api.main:app --reload")
        print("\n💡 Groq Benefits:")
        print("   - FREE API with generous limits")
        print("   - FAST inference (much faster than OpenAI)")
        print("   - High-quality Llama models")
    else:
        print("\n⚠️  Configuration incomplete")
        print("System will continue to work in fallback mode")
        print("You can run this script again anytime to configure the API key")

if __name__ == "__main__":
    main()