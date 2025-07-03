"""
Bug visualization component for the dashboard
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
from config.settings import COLORS, STATUS_COLORS


def show_bugs_dashboard(jira_client):
    """Display comprehensive bugs dashboard"""
    st.header("🐛 Bug Analysis Dashboard")
    
    # For bugs tab, get ALL bugs from the main dataset and filter for bugs
    try:
        all_issues_df = jira_client.get_board_issues()
        bugs_df = all_issues_df[all_issues_df['is_bug'] == True].copy()
        
    except Exception as e:
        st.error(f"Error fetching bugs: {str(e)}")
        return
    
    if bugs_df.empty:
        st.info("No bugs found in the current dataset.")
        return
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_bugs = len(bugs_df)
        st.metric("Total Bugs", total_bugs)
    
    with col2:
        open_bugs = len(bugs_df[bugs_df['status'] != 'Done'])
        st.metric("Open Bugs", open_bugs)
    
    with col3:
        closed_bugs = len(bugs_df[bugs_df['status'] == 'Done'])
        st.metric("Closed Bugs", closed_bugs)
    
    with col4:
        if total_bugs > 0:
            resolution_rate = (closed_bugs / total_bugs) * 100
            st.metric("Resolution Rate", f"{resolution_rate:.1f}%")
        else:
            st.metric("Resolution Rate", "0%")
    
    st.markdown("---")
    
    st.subheader("📊 Bug Distribution Analysis")
    
    # Charts row with filter integrated
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Bug status distribution
        st.subheader("Bug Status Distribution")
        status_counts = bugs_df['status'].value_counts()
        
        colors = [STATUS_COLORS.get(status, COLORS['primary']) for status in status_counts.index]
        
        fig_status = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Bugs by Status",
            color_discrete_sequence=colors
        )
        fig_status.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Bug priority distribution with clickable legend filter
        st.subheader("Bug Priority Distribution")
        
        # Create a stacked bar chart by status and priority with clickable legend
        priority_status_df = bugs_df.groupby(['priority', 'status']).size().reset_index(name='count')
        
        priority_colors = {
            'Highest': '#d62728',
            'High': '#ff7f0e', 
            'Medium': '#2ca02c',
            'Low': '#1f77b4',
            'Lowest': '#9467bd'
        }
        
        fig_priority = px.bar(
            priority_status_df,
            x='priority',
            y='count',
            color='status',
            title="Bugs by Priority (Click legend to filter)",
            color_discrete_map=STATUS_COLORS,
            hover_data=['priority', 'status', 'count']
        )
        
        # Enable clickable legend
        fig_priority.update_layout(
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02,
                font=dict(size=10)
            ),
            margin=dict(r=150)
        )
        
        st.plotly_chart(fig_priority, use_container_width=True)
    
    # Detailed bugs table
    st.subheader("Bug Details")
    
    # Filter options
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.multiselect(
            "Filter by Status",
            options=bugs_df['status'].unique(),
            default=bugs_df['status'].unique()
        )
    
    with col2:
        priority_filter = st.multiselect(
            "Filter by Priority", 
            options=bugs_df['priority'].unique(),
            default=bugs_df['priority'].unique()
        )
    
    with col3:
        area_filter = st.multiselect(
            "Filter by Area",
            options=bugs_df['areas'].unique(),
            default=bugs_df['areas'].unique()
        )
    
    with col4:
        type_filter = st.multiselect(
            "Filter by Type",
            options=bugs_df['issue_type'].unique(),
            default=bugs_df['issue_type'].unique()
        )
    
    # Apply filters
    filtered_bugs = bugs_df[
        (bugs_df['status'].isin(status_filter)) &
        (bugs_df['priority'].isin(priority_filter)) &
        (bugs_df['areas'].isin(area_filter)) &
        (bugs_df['issue_type'].isin(type_filter))
    ]
    
    # Display filtered results count
    st.write(f"Showing {len(filtered_bugs)} bugs")
    
    # Display table
    if not filtered_bugs.empty:
        display_columns = ['key', 'summary', 'status', 'priority', 'assignee', 'areas', 'created']
        st.dataframe(
            filtered_bugs[display_columns].sort_values('created', ascending=False),
            use_container_width=True
        )
    else:
        st.info("No bugs match the selected filters.")
