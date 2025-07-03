"""
Configuration settings for the AICockpit Dashboard
"""

# Jira Configuration
JIRA_SERVER = "https://compasso.atlassian.net"
PROJECT_KEY = "AICP"
BOARD_ID = 3462

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
