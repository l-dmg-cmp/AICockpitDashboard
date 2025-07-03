#!/usr/bin/env python3
"""
Test script to isolate Jira authentication issues
"""

from jira import JIRA
from config.settings import JIRA_SERVER
import sys

def test_authentication():
    """Test Jira authentication with user input"""
    print("=== Jira Authentication Test ===")
    print(f"Testing connection to: {JIRA_SERVER}")
    print()
    
    # Get credentials from user
    email = input("Enter your email: ").strip()
    api_key = input("Enter your API key: ").strip()
    
    if not email or not api_key:
        print("❌ Error: Email and API key are required")
        return False
    
    print(f"\n🔍 Testing authentication for: {email}")
    print(f"🌐 Connecting to: {JIRA_SERVER}")
    
    try:
        # Create JIRA client with provided credentials
        print("📡 Creating JIRA client...")
        jira = JIRA(
            server=JIRA_SERVER,
            basic_auth=(email, api_key)
        )
        
        print("✅ JIRA client created successfully")
        
        # Test connection by getting current user info
        print("👤 Getting current user info...")
        current_user = jira.current_user()
        
        if current_user:
            print(f"✅ Authentication successful!")
            print(f"👤 Logged in as: {current_user}")
            
            # Try to get some basic info
            try:
                print("\n📊 Testing API access...")
                projects = jira.projects()
                print(f"📁 Found {len(projects)} projects")
                
                # Try to access the specific project
                from config.settings import PROJECT_KEY
                try:
                    project = jira.project(PROJECT_KEY)
                    print(f"🎯 Successfully accessed project: {project.name} ({PROJECT_KEY})")
                except Exception as proj_error:
                    print(f"⚠️  Could not access project {PROJECT_KEY}: {proj_error}")
                
            except Exception as api_error:
                print(f"⚠️  API access test failed: {api_error}")
            
            return True
        else:
            print("❌ Authentication failed: current_user() returned None")
            return False
            
    except Exception as e:
        print(f"❌ Authentication failed with exception:")
        print(f"   Exception type: {type(e).__name__}")
        print(f"   Exception message: {str(e)}")
        
        # Additional debugging info
        if hasattr(e, 'status_code'):
            print(f"   HTTP Status Code: {e.status_code}")
        if hasattr(e, 'text'):
            print(f"   Response text: {e.text}")
        
        return False

def main():
    """Main function"""
    success = test_authentication()
    
    print("\n" + "="*50)
    if success:
        print("🎉 Authentication test PASSED")
        print("The issue might be in the Streamlit session handling.")
    else:
        print("❌ Authentication test FAILED")
        print("Check your credentials and network connection.")
    
    print("="*50)
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
