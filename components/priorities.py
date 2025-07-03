"""
Priority visualization component for the dashboard
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config.settings import COLORS, PRIORITY_MAPPING


def show_priorities_dashboard(jira_client, project_key):
    """Display comprehensive priorities dashboard for a specific project"""
    st.header(f"🎯 Priority Analysis: {project_key}")
    
    # Get data for the specified project
    df = jira_client.get_board_issues(project_key=project_key)
    if df.empty:
        st.warning("No data available for this project.")
        return
    
    # Priority metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        highest_priority = len(df[df['priority'] == 'Highest'])
        st.metric("Highest Priority", highest_priority, delta=None)
    
    with col2:
        high_priority = len(df[df['priority'] == 'High'])
        st.metric("High Priority", high_priority, delta=None)
    
    with col3:
        critical_open = len(df[(df['priority'].isin(['Highest', 'High'])) & (df['status'] != 'Done')])
        st.metric("Critical Open Issues", critical_open, delta=None)
    
    with col4:
        avg_priority = df['priority'].map(PRIORITY_MAPPING).mean()
        st.metric("Average Priority Score", f"{avg_priority:.1f}", delta=None)
    
    st.markdown("---")
    
    # Priority distribution charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Overall priority distribution
        st.subheader("Priority Distribution")
        priority_counts = df['priority'].value_counts()
        
        priority_colors = {
            'Highest': '#8B0000',
            'High': '#FF4500', 
            'Medium': '#FFD700',
            'Low': '#32CD32',
            'Lowest': '#87CEEB'
        }
        
        fig_priority = px.pie(
            values=priority_counts.values,
            names=priority_counts.index,
            title="All Issues by Priority",
            color=priority_counts.index,
            color_discrete_map=priority_colors
        )
        fig_priority.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_priority, use_container_width=True)
    
    with col2:
        # Priority by status
        st.subheader("Priority vs Status")
        priority_status = df.groupby(['priority', 'status']).size().reset_index(name='count')
        
        fig_priority_status = px.bar(
            priority_status,
            x='priority',
            y='count',
            color='status',
            title="Priority Distribution by Status",
            category_orders={'priority': ['Highest', 'High', 'Medium', 'Low', 'Lowest']}
        )
        st.plotly_chart(fig_priority_status, use_container_width=True)
    
    # Priority by area analysis
    st.subheader("Priority Analysis by Area")
    
    # Create priority heatmap by area
    priority_area = df.groupby(['areas', 'priority']).size().unstack(fill_value=0)
    
    if not priority_area.empty:
        # Reorder columns by priority importance
        priority_order = ['Highest', 'High', 'Medium', 'Low', 'Lowest']
        existing_priorities = [p for p in priority_order if p in priority_area.columns]
        priority_area = priority_area[existing_priorities]
        
        fig_heatmap = px.imshow(
            priority_area.values,
            x=priority_area.columns,
            y=priority_area.index,
            color_continuous_scale='Reds',
            title="Priority Heatmap by Area",
            text_auto=True
        )
        fig_heatmap.update_layout(
            xaxis_title="Priority",
            yaxis_title="Area"
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Critical issues alert
    st.subheader("🚨 Critical Issues Alert")
    
    critical_issues = df[
        (df['priority'].isin(['Highest', 'High'])) & 
        (df['status'] != 'Done')
    ].sort_values('priority', key=lambda x: x.map({'Highest': 0, 'High': 1}))
    
    if not critical_issues.empty:
        st.warning(f"⚠️ {len(critical_issues)} critical issues require attention!")
        
        # Show critical issues table
        display_columns = ['key', 'summary', 'priority', 'status', 'assignee', 'areas', 'created']
        st.dataframe(
            critical_issues[display_columns].head(10),
            use_container_width=True
        )
        
        if len(critical_issues) > 10:
            st.info(f"Showing top 10 of {len(critical_issues)} critical issues")
    else:
        st.success("✅ No critical issues open!")
    
    # Priority trends over time
    st.subheader("Priority Trends Over Time")
    
    # Group by month and priority
    df['created_month'] = df['created'].dt.to_period('M').astype(str)
    priority_trends = df.groupby(['created_month', 'priority']).size().reset_index(name='count')
    
    if not priority_trends.empty:
        fig_trends = px.line(
            priority_trends,
            x='created_month',
            y='count',
            color='priority',
            title="Priority Trends Over Time",
            color_discrete_map=priority_colors
        )
        fig_trends.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_trends, use_container_width=True)
    
    # Priority by assignee
    st.subheader("Priority Distribution by Assignee")
    
    assignee_priority = df.groupby(['assignee', 'priority']).size().reset_index(name='count')
    top_assignees = df['assignee'].value_counts().head(10).index
    assignee_priority_filtered = assignee_priority[assignee_priority['assignee'].isin(top_assignees)]
    
    if not assignee_priority_filtered.empty:
        fig_assignee_priority = px.bar(
            assignee_priority_filtered,
            x='assignee',
            y='count',
            color='priority',
            title="Priority Distribution by Top Assignees",
            color_discrete_map=priority_colors
        )
        fig_assignee_priority.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_assignee_priority, use_container_width=True)
    
    # Filters section
    st.subheader("🔍 Filter Issues by Type")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.multiselect(
            "Filter by Status",
            options=df['status'].unique(),
            default=df['status'].unique(),
            key="priority_status_filter"
        )
    
    with col2:
        priority_filter = st.multiselect(
            "Filter by Priority",
            options=df['priority'].unique(),
            default=df['priority'].unique(),
            key="priority_priority_filter"
        )
    
    with col3:
        area_filter = st.multiselect(
            "Filter by Area",
            options=df['areas'].unique(),
            default=df['areas'].unique(),
            key="priority_area_filter"
        )
    
    with col4:
        type_filter = st.multiselect(
            "Filter by Type",
            options=df['issue_type'].unique(),
            default=df['issue_type'].unique(),
            key="priority_type_filter"
        )
    
    # Apply filters
    filtered_df = df[
        (df['status'].isin(status_filter)) &
        (df['priority'].isin(priority_filter)) &
        (df['areas'].isin(area_filter)) &
        (df['issue_type'].isin(type_filter))
    ]
    
    # Show filtered results
    st.subheader("Filtered Issues")
    st.write(f"Showing {len(filtered_df)} issues")
    
    if not filtered_df.empty:
        display_columns = ['key', 'summary', 'priority', 'status', 'issue_type', 'assignee', 'areas', 'created']
        st.dataframe(
            filtered_df[display_columns].sort_values('created', ascending=False),
            use_container_width=True
        )
    else:
        st.info("No issues match the selected filters.")
