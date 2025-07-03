"""
Authentication module for Jira login
"""

import streamlit as st
from jira import JIRA
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
                        if authenticate_user(email, api_key):
                            st.success("✅ Login successful!")
                            st.session_state.authenticated = True
                            st.session_state.email = email
                            st.session_state.api_key = api_key
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials. Please check your email and API key.")
                    else:
                        st.warning("⚠️ Please fill in both email and API key.")


def authenticate_user(email, api_key):
    """Authenticate user with Jira API"""
    try:
        # Create JIRA client with provided credentials and timeout
        jira = JIRA(
            server=JIRA_SERVER,
            basic_auth=(email, api_key),
            timeout=15,  # 15 second timeout
            max_retries=1
        )
        
        # Test connection by getting current user info
        current_user = jira.current_user()
        
        if current_user:
            return True
        else:
            return False
            
    except Exception as e:
        # Log the full error to the console for debugging
        print(f"An exception occurred: {type(e).__name__} - {e}")
        st.error("An unexpected error occurred during authentication. Please check the logs for details.")
        return False


def is_authenticated():
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)


def logout():
    """Logout user and clear session"""
    for key in ['authenticated', 'email', 'api_key']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()


def get_credentials():
    """Get stored credentials from session"""
    if is_authenticated():
        return st.session_state.email, st.session_state.api_key
    return None, None


def show_logout_button():
    """Display logout button in sidebar"""
    if is_authenticated():
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**Logged in as:** {st.session_state.email}")
        if st.sidebar.button("🚪 Logout"):
            logout()
