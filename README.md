# AICockpit Dashboard

A comprehensive Streamlit dashboard for visualizing and analyzing Jira project data with advanced filtering and interactive charts.

## Features

- **🔐 Secure Authentication**: Login with Jira email and API key
- **📈 Overview Dashboard**: Project metrics and recent activity
- **🐛 Bug Analysis**: Comprehensive bug tracking and visualization
- **🎯 Priority Management**: Priority-based issue analysis
- **📅 Quarter Timeline**: Quarterly project roadmap and progress
- **📊 Interactive Gantt Chart**: Timeline visualization with area filtering

## Areas Supported

- Desenvolvimento (Development)
- Arquitetura (Architecture)
- Dados (Data)
- Qualidade (Quality)
- DevOps

## Project Structure

```
AICockpitDashboard/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── config_template.py       # Configuration template
├── run_dashboard.bat        # Windows startup script
├── run_dashboard.sh         # Linux/Mac startup script
├── auth/
│   └── login.py            # Authentication module
├── components/
│   ├── bugs.py             # Bug analysis dashboard
│   ├── priorities.py       # Priority management dashboard
│   ├── quarters.py         # Quarter timeline dashboard
│   └── gantt.py            # Gantt chart with area filtering
├── config/
│   └── settings.py         # Configuration settings
└── jira/
    └── client.py           # Jira API client
```

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your Jira settings**:
   - Copy `config_template.py` to `config/settings.py`
   - Update the following in `config/settings.py`:
     - `JIRA_SERVER`: Your Jira instance URL (e.g., "https://compasso.atlassian.net")
     - `PROJECT_KEY`: Your project key (e.g., "AICP")
     - `BOARD_ID`: Your board ID (e.g., 3462)

## Usage

1. **Run the application**:
   ```bash
   streamlit run app.py
   ```

2. **Login with your credentials**:
   - Email: Your Jira account email
   - API Key: Your Jira API key

3. **Navigate through the dashboard tabs**:
   - **Overview**: General project metrics and recent activity
   - **Bugs**: Detailed bug analysis and trends
   - **Priorities**: Priority-based issue breakdown
   - **Quarters**: Timeline and quarterly progress
   - **Gantt Chart**: Interactive project timeline with area filtering

## Jira API Key Setup

To get your Jira API key:

1. Go to your Jira account settings
2. Navigate to Security → API tokens
3. Create a new API token
4. Copy the generated token for use in the dashboard

## Configuration

### Project Settings

Edit `config/settings.py` to customize:

- **Jira Connection**: Server URL, project key, board ID
- **Areas**: Customize the area labels for your project
- **Colors**: Modify visualization colors
- **UI Settings**: Page title, icon, layout

### Custom Areas

To modify the areas/labels, update the `AREAS` list in `config/settings.py`:

```python
AREAS = [
    "Your_Area_1",
    "Your_Area_2",
    "Your_Area_3",
    # Add more areas as needed
]
```

## Features Detail

### Bug Analysis
- Bug metrics and KPIs
- Status and priority distribution
- Trend analysis over time
- Bug distribution by area and assignee
- Detailed filtering and search

### Priority Management
- Priority-based metrics
- Critical issues alerts
- Priority trends over time
- Heatmap analysis by area
- Priority distribution by assignee

### Quarter Timeline
- Quarterly issue distribution
- Completion rate tracking
- Quarter comparison
- Detailed quarter breakdown
- Roadmap visualization

### Gantt Chart
- Interactive timeline visualization
- Area-based filtering (Desenvolvimento, Arquitetura, Dados, Qualidade, DevOps)
- Status and priority filtering
- Date range selection
- Area-specific timeline views
- Task completion tracking

## Data Refresh

- **Auto-refresh**: Data is cached for 5 minutes for performance
- **Manual refresh**: Use the "🔄 Refresh Data" button in the sidebar
- **Real-time**: All data is fetched directly from Jira API

## Troubleshooting

### Common Issues

1. **Authentication Error**:
   - Verify your email and API key are correct
   - Check if your API key has expired
   - Ensure you have access to the specified Jira project

2. **No Data Displayed**:
   - Verify the project key and board ID in settings
   - Check if there are issues in your Jira project
   - Ensure your account has read access to the project

3. **Slow Performance**:
   - Data is cached for 5 minutes to improve performance
   - Large projects may take longer to load initially
