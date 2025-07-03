"""
Configuration settings for the AICockpit Dashboard
"""
import streamlit as st
import os

def get_jira_config():
    """Get Jira configuration from Streamlit secrets or environment variables"""
    try:
        # Try Streamlit Cloud secrets first
        if hasattr(st, 'secrets') and 'jira' in st.secrets:
            return {
                'email': st.secrets["jira"]["email"],
                'api_key': st.secrets["jira"]["api_key"],
                'server': st.secrets["jira"]["server"]
            }
    except:
        pass
    
    # Fallback to environment variables or defaults
    return {
        'email': os.getenv('JIRA_EMAIL', 'lidinei@compasso.com.br'),
        'api_key': os.getenv('JIRA_API_KEY', ''),
        'server': os.getenv('JIRA_SERVER', 'https://compasso.atlassian.net')
    }

# Load configuration
jira_config = get_jira_config()
JIRA_EMAIL = jira_config['email']
JIRA_API_KEY = jira_config['api_key']

# Jira Configuration
JIRA_SERVER = jira_config['server']
PROJECT_KEY = "AICP"

# Dashboard Configuration
AREAS = [
    "Desenvolvimento",
    "Arquitetura", 
    "Dados",
    "Qualidade",
    "DevOps"
]

PRIORITY_MAPPING = {
    "Highest": 5,
    "High": 4,
    "Medium": 3,
    "Low": 2,
    "Lowest": 1
}

# UI Configuration
PAGE_TITLE = "AICockpit Dashboard"
PAGE_ICON = "📊"
LAYOUT = "wide"

# Colors for visualizations
COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e", 
    "success": "#2ca02c",
    "danger": "#d62728",
    "warning": "#ff9800",
    "info": "#17a2b8",
    "light": "#f8f9fa",
    "dark": "#343a40"
}

# Area colors for Gantt chart
AREA_COLORS = {
    "Desenvolvimento": "#2E8B57",
    "Arquitetura": "#4682B4",
    "Dados": "#DAA520",
    "Qualidade": "#DC143C",
    "DevOps": "#9370DB"
}

# Status colors
STATUS_COLORS = {
    "To Do": "#6c757d",
    "In Progress": "#007bff",
    "Done": "#28a745",
    "Blocked": "#dc3545",
    "Review": "#ffc107"
}
