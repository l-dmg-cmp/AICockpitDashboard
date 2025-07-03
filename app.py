"""
AICockpit Dashboard - Main Streamlit Application
"""

import streamlit as st
from auth.login import show_login_form, is_authenticated, show_logout_button, get_credentials
from jira_api.client import JiraClient
from components.bugs import show_bugs_dashboard
from components.incidents import show_incidents_dashboard
from components.priorities import show_priorities_dashboard
from components.quarters import show_quarters_dashboard
from components.gantt import show_gantt_dashboard
from config.settings import PAGE_TITLE, PAGE_ICON, LAYOUT


def main():
    """Main application function"""
    # Page configuration
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=LAYOUT,
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    /* Hide Streamlit elements - Updated selectors */
    .reportview-container {
        margin-top: -2em;
    }
    
    /* Hide main menu */
    #MainMenu {visibility: hidden !important;}
    [data-testid="stMainMenu"] {display: none !important;}
    
    /* Hide deploy button */
    .stDeployButton {display: none !important;}
    [data-testid="stAppDeployButton"] {display: none !important;}
    button[data-testid="stBaseButton-header"] {display: none !important;}
    
    /* Hide footer */
    footer {visibility: hidden !important;}
    .stApp > footer {display: none !important;}
    
    /* Hide decoration */
    #stDecoration {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    
    /* Hide toolbar */
    .stToolbar {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    
    /* Hide header */
    header[data-testid="stHeader"] {display: none !important;}
    
    /* Custom styling */
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .metric-container {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    
    .sidebar .sidebar-content {
        background: #f8f9fa;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #f8f9fa;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 20px;
        color: #495057;
        font-weight: 500;
        border: 1px solid #dee2e6;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #e9ecef;
        color: #212529;
    }
    
    .stTabs [aria-selected="true"] {
        background: #007bff;
        color: white !important;
        font-weight: 600;
        border: 1px solid #007bff;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Check authentication
    if not is_authenticated():
        show_login_form()
        return
    
    # Get credentials
    email, api_key = get_credentials()
    
    # Initialize Jira client
    try:
        jira_client = JiraClient(email, api_key)
    except Exception as e:
        st.error(f"Failed to initialize Jira client: {str(e)}")
        return
    
    # Header
    st.markdown(f"""
    <div class="main-header">
        <h1>{PAGE_ICON} AICockpit Dashboard</h1>
        <p>Comprehensive Jira Project Analytics & Visualization</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Dashboard Navigation")
        
        # Refresh button
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        # Show logout button
        show_logout_button()
        
        st.markdown("---")
        
        # Quick stats
        try:
            stats = jira_client.get_project_statistics()
            if stats:
                st.subheader("📊 Quick Stats")
                st.metric("Total Issues", stats.get('total_issues', 0))
                st.metric("Open Issues", stats.get('open_issues', 0))
                st.metric("Bugs", stats.get('bugs_count', 0))
                
                # Top priority breakdown
                priorities = stats.get('by_priority', {})
                if priorities:
                    st.subheader("🎯 Priority Breakdown")
                    for priority, count in list(priorities.items())[:3]:
                        st.write(f"**{priority}:** {count}")
                
                # Debug: Show areas found in data
                areas = stats.get('by_area', {})
                if areas:
                    st.subheader("🏷️ Areas Found")
                    for area, count in list(areas.items())[:5]:
                        st.write(f"**{area}:** {count}")
        except Exception as e:
            st.warning("Could not load quick stats")
    
    # Main dashboard tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Overview", 
        "🐛 Bugs", 
        "🚨 Incidents",
        "🎯 Priorities", 
        "📅 Quarters", 
        "📊 Gantt Chart"
    ])
    
    with tab1:
        # Overview dashboard
        st.header("📈 Project Overview")
        
        try:
            # Get basic stats
            df = jira_client.get_board_issues()
            if not df.empty:
                # Key metrics
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    total_issues = len(df)
                    st.metric("Total Issues", total_issues)
                
                with col2:
                    open_issues = len(df[df['status'] != 'Done'])
                    st.metric("Open Issues", open_issues)
                
                with col3:
                    closed_issues = len(df[df['status'] == 'Done'])
                    st.metric("Closed Issues", closed_issues)
                
                with col4:
                    bugs_count = len(df[df['is_bug'] == True])
                    st.metric("Total Bugs", bugs_count)
                
                with col5:
                    if total_issues > 0:
                        completion_rate = (closed_issues / total_issues) * 100
                        st.metric("Completion Rate", f"{completion_rate:.1f}%")
                
                st.markdown("---")
                
                # Overview charts
                col1, col2 = st.columns(2)
                
                with col1:
                    # Status distribution
                    import plotly.express as px
                    status_counts = df['status'].value_counts()
                    
                    fig_status = px.pie(
                        values=status_counts.values,
                        names=status_counts.index,
                        title="Issues by Status"
                    )
                    st.plotly_chart(fig_status, use_container_width=True)
                
                with col2:
                    # Area distribution
                    area_counts = df['areas'].value_counts()
                    
                    fig_areas = px.bar(
                        x=area_counts.values,
                        y=area_counts.index,
                        orientation='h',
                        title="Issues by Area"
                    )
                    st.plotly_chart(fig_areas, use_container_width=True)
                
                # Issues by Area breakdown
                st.subheader("📋 Issues by Area")
                
                # Show total issues fetched
                st.write(f"**Total de issues carregadas:** {len(df)}")
                st.markdown("---")
                
                all_labels = []
                for labels_str in df['areas']:
                    if labels_str != 'No Area':
                        labels_list = labels_str.split(', ')
                        all_labels.extend(labels_list)
                
                if all_labels:
                    unique_labels = list(set(all_labels))
                    
                    # Create expandable sections for each area
                    for label in sorted(unique_labels):
                        count = all_labels.count(label)
                        area_issues = df[df['areas'].str.contains(label, na=False)]
                        
                        with st.expander(f"📊 {label} ({count} issues)"):
                            # Area metrics
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                area_open = len(area_issues[area_issues['status'] != 'Done'])
                                st.metric("Open", area_open)
                            
                            with col2:
                                area_done = len(area_issues[area_issues['status'] == 'Done'])
                                st.metric("Done", area_done)
                            
                            with col3:
                                area_bugs = len(area_issues[area_issues['is_bug'] == True])
                                st.metric("Bugs", area_bugs)
                            
                            with col4:
                                if count > 0:
                                    completion_rate = (area_done / count) * 100
                                    st.metric("Completion", f"{completion_rate:.1f}%")
                            
                            # Area charts
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # Status distribution for this area
                                area_status = area_issues['status'].value_counts()
                                if not area_status.empty:
                                    fig_area_status = px.pie(
                                        values=area_status.values,
                                        names=area_status.index,
                                        title=f"{label} - Status Distribution"
                                    )
                                    st.plotly_chart(fig_area_status, use_container_width=True)
                            
                            with col2:
                                # Priority distribution for this area
                                area_priority = area_issues['priority'].value_counts()
                                if not area_priority.empty:
                                    priority_colors = {
                                        'Highest': '#8B0000',
                                        'High': '#FF4500', 
                                        'Medium': '#FFD700',
                                        'Low': '#32CD32',
                                        'Lowest': '#87CEEB'
                                    }
                                    fig_area_priority = px.pie(
                                        values=area_priority.values,
                                        names=area_priority.index,
                                        title=f"{label} - Priority Distribution",
                                        color_discrete_map=priority_colors
                                    )
                                    st.plotly_chart(fig_area_priority, use_container_width=True)
                            
                            # Area issues table
                            st.subheader(f"Recent {label} Issues")
                            area_recent = area_issues.sort_values('updated', ascending=False).head(5)
                            display_columns = ['key', 'summary', 'status', 'priority', 'assignee', 'updated']
                            st.dataframe(
                                area_recent[display_columns],
                                use_container_width=True
                            )
                else:
                    st.write("❌ **Nenhuma área encontrada nos dados**")
                
                # Recent activity
                st.subheader("Recent Activity")
                recent_issues = df.sort_values('updated', ascending=False).head(10)
                display_columns = ['key', 'summary', 'status', 'priority', 'assignee', 'areas', 'updated']
                st.dataframe(
                    recent_issues[display_columns],
                    use_container_width=True
                )
            else:
                st.warning("No data available")
        except Exception as e:
            st.error(f"Error loading overview: {str(e)}")
    
    with tab2:
        # Bugs dashboard
        show_bugs_dashboard(jira_client)
    
    with tab3:
        # Incidents dashboard
        show_incidents_dashboard(jira_client)
    
    with tab4:
        # Priorities dashboard
        show_priorities_dashboard(jira_client)
    
    with tab5:
        # Quarters dashboard
        show_quarters_dashboard(jira_client)
    
    with tab6:
        # Gantt chart dashboard
        show_gantt_dashboard(jira_client)


if __name__ == "__main__":
    main()
