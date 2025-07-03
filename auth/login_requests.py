"""
Alternative authentication module using requests library instead of jira library
"""

import streamlit as st
import requests
import base64
from config.settings import JIRA_SERVER


def show_login_form():
    """Display login form and handle authentication"""
    st.title("🔐 AICockpit Dashboard Login")
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### Login to access your Jira dashboard")
            
            with st.form("login_form"):
                email = st.text_input(
                    "Email", 
                    placeholder="your.email@compasso.com.br",
                    help="Enter your Jira account email"
                )
                
                api_key = st.text_input(
                    "API Key", 
                    type="password",
                    placeholder="Your Jira API Key",
                    help="Enter your Jira API key for authentication"
                )
                
                submit_button = st.form_submit_button("Login", use_container_width=True)
                
                if submit_button:
                    if email and api_key:
                        with st.spinner("Authenticating..."):
                            auth_result = authenticate_user(email, api_key)
                            
                        if auth_result['success']:
                            st.success("✅ Login successful!")
                            st.session_state.authenticated = True
                            st.session_state.email = email
                            st.session_state.api_key = api_key
                            st.session_state.user_info = auth_result['user_info']
                            st.rerun()
                        else:
                            st.error(f"❌ {auth_result['error']}")
                    else:
                        st.warning("⚠️ Please fill in both email and API key.")


def authenticate_user(email, api_key):
    """Authenticate user with Jira API using requests library"""
    try:
        # Create basic auth header
        auth_str = f'{email}:{api_key}'
        auth_bytes = auth_str.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Test authentication by getting current user info
        response = requests.get(
            f'{JIRA_SERVER}/rest/api/2/myself', 
            headers=headers, 
            timeout=15
        )
        
        if response.status_code == 200:
            user_info = response.json()
            return {
                'success': True,
                'user_info': user_info,
                'error': None
            }
        elif response.status_code == 401:
            return {
                'success': False,
                'user_info': None,
                'error': 'Invalid credentials. Please check your email and API key.'
            }
        elif response.status_code == 403:
            return {
                'success': False,
                'user_info': None,
                'error': 'Access forbidden. You may not have permission to access this Jira instance.'
            }
        else:
            return {
                'success': False,
                'user_info': None,
                'error': f'Authentication failed with HTTP {response.status_code}'
            }
            
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'user_info': None,
            'error': 'Request timed out. Please check your internet connection.'
        }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'user_info': None,
            'error': 'Could not connect to Jira server. Please check your internet connection.'
        }
    except Exception as e:
        return {
            'success': False,
            'user_info': None,
            'error': f'Unexpected error: {str(e)}'
        }


def is_authenticated():
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)


def logout():
    """Logout user and clear session"""
    for key in ['authenticated', 'email', 'api_key', 'user_info']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()


def get_credentials():
    """Get stored credentials from session"""
    if is_authenticated():
        return st.session_state.email, st.session_state.api_key
    return None, None


def get_user_info():
    """Get stored user info from session"""
    if is_authenticated():
        return st.session_state.get('user_info', {})
    return {}


def show_logout_button():
    """Display logout button in sidebar"""
    if is_authenticated():
        user_info = get_user_info()
        display_name = user_info.get('displayName', st.session_state.email)
        
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**Logged in as:** {display_name}")
        if st.sidebar.button("🚪 Logout"):
            logout()
