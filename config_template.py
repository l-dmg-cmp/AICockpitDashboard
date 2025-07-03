"""
Configuration Template for AICockpit Dashboard

Copy this file to config/settings.py and update with your Jira details.
"""

# Jira Configuration - UPDATE THESE VALUES
JIRA_SERVER = "https://your-company.atlassian.net"  # Your Jira server URL
PROJECT_KEY = "YOUR_PROJECT"  # Your project key (e.g., "AICP")
BOARD_ID = 1234  # Your board ID number

# Dashboard Configuration - Customize as needed
AREAS = [
    "Desenvolvimento",  # Development
    "Arquitetura",      # Architecture
    "Dados",            # Data
    "Qualidade",        # Quality
    "DevOps"            # DevOps
    # Add or modify areas according to your project labels
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

# Area colors for Gantt chart - Customize to match your areas
AREA_COLORS = {
    "Desenvolvimento": "#2E8B57",  # Sea Green
    "Arquitetura": "#4682B4",     # Steel Blue
    "Dados": "#DAA520",           # Goldenrod
    "Qualidade": "#DC143C",       # Crimson
    "DevOps": "#9370DB"           # Medium Purple
}

# Status colors
STATUS_COLORS = {
    "To Do": "#6c757d",      # Gray
    "In Progress": "#007bff", # Blue
    "Done": "#28a745",       # Green
    "Blocked": "#dc3545",    # Red
    "Review": "#ffc107"      # Yellow
}

# HOW TO FIND YOUR BOARD ID:
# 1. Go to your Jira board
# 2. Look at the URL: https://your-company.atlassian.net/jira/software/c/projects/PROJECT/boards/BOARD_ID
# 3. The number after /boards/ is your BOARD_ID

# HOW TO GET YOUR API KEY:
# 1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
# 2. Click "Create API token"
# 3. Give it a name and copy the generated token
# 4. Use this token as your API key in the dashboard login
