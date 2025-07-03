#!/usr/bin/env python3
"""
Test script to isolate Jira authentication issues with timeout handling
"""

from jira import JIRA
from config.settings import JIRA_SERVER, PROJECT_KEY
import requests
import sys
import signal
from functools import wraps

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

def with_timeout(timeout_seconds):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Set up the timeout
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_seconds)
            
            try:
                result = func(*args, **kwargs)
                signal.alarm(0)  # Cancel the alarm
                return result
            except TimeoutError:
                print(f"⏰ Operation timed out after {timeout_seconds} seconds")
                return None
            finally:
                signal.signal(signal.SIGALRM, old_handler)
        return wrapper
    return decorator

def test_network_connectivity():
    """Test basic network connectivity to Jira server"""
    print("🌐 Testing network connectivity...")
    
    try:
        # Test basic HTTP connectivity
        response = requests.get(JIRA_SERVER, timeout=10)
        print(f"✅ Successfully connected to {JIRA_SERVER}")
        print(f"   Status Code: {response.status_code}")
        return True
    except requests.exceptions.Timeout:
        print(f"❌ Timeout connecting to {JIRA_SERVER}")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error to {JIRA_SERVER}")
        return False
    except Exception as e:
        print(f"❌ Network test failed: {e}")
        return False

@with_timeout(30)  # 30 second timeout
def test_jira_auth(email, api_key):
    """Test Jira authentication with timeout"""
    print("📡 Creating JIRA client with 30s timeout...")
    
    try:
        # Create JIRA client
        jira = JIRA(
            server=JIRA_SERVER,
            basic_auth=(email, api_key),
            timeout=30,  # Set explicit timeout
            max_retries=1
        )
        
        print("✅ JIRA client created successfully")
        
        # Test connection
        print("👤 Getting current user info...")
        current_user = jira.current_user()
        
        if current_user:
            print(f"✅ Authentication successful!")
            print(f"👤 Logged in as: {current_user}")
            return True
        else:
            print("❌ Authentication failed: current_user() returned None")
            return False
            
    except Exception as e:
        print(f"❌ JIRA authentication failed:")
        print(f"   Exception type: {type(e).__name__}")
        print(f"   Exception message: {str(e)}")
        return False

def main():
    """Main function"""
    print("=== Enhanced Jira Authentication Test ===")
    print(f"Testing connection to: {JIRA_SERVER}")
    print(f"Target project: {PROJECT_KEY}")
    print()
    
    # Step 1: Test network connectivity
    if not test_network_connectivity():
        print("\n❌ Network connectivity test failed. Check your internet connection.")
        return False
    
    print()
    
    # Step 2: Get credentials
    print("Please enter your Jira credentials:")
    email = input("Email: ").strip()
    api_key = input("API Key: ").strip()
    
    if not email or not api_key:
        print("❌ Error: Email and API key are required")
        return False
    
    print(f"\n🔍 Testing authentication for: {email}")
    print("⏰ This test will timeout after 30 seconds if there are connectivity issues")
    
    # Step 3: Test authentication with timeout
    success = test_jira_auth(email, api_key)
    
    print("\n" + "="*60)
    if success:
        print("🎉 Authentication test PASSED")
        print("The issue might be in the Streamlit session handling or timeout configuration.")
    else:
        print("❌ Authentication test FAILED")
        print("This explains why your Streamlit login appears to fail silently.")
        print("\nPossible solutions:")
        print("1. Check if your API key is correct and not expired")
        print("2. Verify you have access to the Jira instance")
        print("3. Check if there are firewall/proxy issues")
        print("4. Try accessing Jira directly in your browser")
    
    print("="*60)
    return success

if __name__ == "__main__":
    try:
        # For Windows, we can't use signal.alarm, so let's use a simpler approach
        if sys.platform == "win32":
            print("⚠️  Running on Windows - timeout handling limited")
            
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
