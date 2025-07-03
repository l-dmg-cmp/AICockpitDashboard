"""
Gantt chart visualization component with area filtering
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
from config.settings import COLORS, AREA_COLORS, AREAS, STATUS_COLORS


def show_gantt_dashboard(jira_client):
    """Display interactive Gantt chart with area filtering"""
    st.header("📊 Gantt Chart - Project Timeline")
    
    # Get data
    df = jira_client.get_board_issues()
    if df.empty:
        st.warning("No data available. Please check your Jira connection.")
        return
    
    # Sidebar filters
    st.sidebar.header("Gantt Chart Filters")
    
    # Area filter - Get all unique areas from the data
    all_areas_in_data = df['areas'].str.split(', ').explode().unique()
    available_areas = []
    
    # Add configured areas that exist in data
    for area in AREAS:
        if area in all_areas_in_data:
            available_areas.append(area)
    
    # Add any other areas found in data that aren't in our config
    for area in all_areas_in_data:
        if area not in AREAS and area != 'No Area' and area not in available_areas:
            available_areas.append(area)
    
    # Always add 'No Area' option
    if 'No Area' in all_areas_in_data:
        available_areas.append('No Area')
    
    
    selected_areas = st.sidebar.multiselect(
        "Filter by Area",
        options=available_areas,
        default=available_areas,
        help="Select areas to display in the Gantt chart"
    )
    
    # Status filter
    selected_statuses = st.sidebar.multiselect(
        "Filter by Status",
        options=df['status'].unique(),
        default=df['status'].unique()
    )
    
    # Priority filter
    selected_priorities = st.sidebar.multiselect(
        "Filter by Priority",
        options=df['priority'].unique(),
        default=df['priority'].unique()
    )
    
    # Date range filter
    min_date = df['created'].min().date()
    max_date = df['created'].max().date()
    
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Apply filters
    filtered_df = df.copy()
    
    # Filter by areas - Fixed for multi-area issues
    if selected_areas:
        def check_area_match(areas_string):
            if areas_string == 'No Area':
                return 'No Area' in selected_areas
            else:
                # Split the areas and check if any selected area is in the issue's areas
                issue_areas = [area.strip() for area in areas_string.split(',')]
                return any(selected_area in issue_areas for selected_area in selected_areas)
        
        area_mask = filtered_df['areas'].apply(check_area_match)
        filtered_df = filtered_df[area_mask]
    
    # Filter by status
    filtered_df = filtered_df[filtered_df['status'].isin(selected_statuses)]
    
    # Filter by priority
    filtered_df = filtered_df[filtered_df['priority'].isin(selected_priorities)]
    
    # Filter by date range
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df['created'].dt.date >= start_date) & 
            (filtered_df['created'].dt.date <= end_date)
        ]
    
    if filtered_df.empty:
        st.warning("No issues match the selected filters.")
        return
    
    # Gantt chart metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Filtered Issues", len(filtered_df))
    
    with col2:
        completed_issues = len(filtered_df[filtered_df['status'] == 'Done'])
        st.metric("Completed", completed_issues)
    
    with col3:
        in_progress = len(filtered_df[filtered_df['status'] == 'In Progress'])
        st.metric("In Progress", in_progress)
    
    with col4:
        if len(filtered_df) > 0:
            completion_rate = (completed_issues / len(filtered_df)) * 100
            st.metric("Completion Rate", f"{completion_rate:.1f}%")
    
    st.markdown("---")
    
    # Prepare Gantt data
    gantt_data = jira_client.get_gantt_data(selected_areas)
    
    if gantt_data.empty:
        st.warning("No data available for Gantt chart with current filters.")
        return
    
    # Apply additional filters to Gantt data
    gantt_filtered = gantt_data[
        (gantt_data['Status'].isin(selected_statuses)) &
        (gantt_data['Priority'].isin(selected_priorities))
    ]
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        gantt_filtered = gantt_filtered[
            (gantt_filtered['Start'].dt.date >= start_date) & 
            (gantt_filtered['Start'].dt.date <= end_date)
        ]
    
    if gantt_filtered.empty:
        st.warning("No tasks match the selected filters for Gantt chart.")
        return
    
    # Create Gantt chart
    st.subheader("Project Timeline")
    
    # Sort by start date and resource
    gantt_filtered = gantt_filtered.sort_values(['Resource', 'Start'])
    
    # Create color mapping for resources (areas)
    resource_colors = {}
    for resource in gantt_filtered['Resource'].unique():
        if resource in AREA_COLORS:
            resource_colors[resource] = AREA_COLORS[resource]
        else:
            resource_colors[resource] = COLORS['primary']
    
    # Create Gantt chart using Plotly
    fig = px.timeline(
        gantt_filtered,
        x_start="Start",
        x_end="Finish",
        y="Task",
        color="Resource",
        title="Project Timeline by Area",
        color_discrete_map=resource_colors,
        hover_data=["Status", "Priority", "Assignee", "Summary"]
    )
    
    # Add current date line using add_shape - Enhanced visibility
    current_date = datetime.now()
    fig.add_shape(
        type="line",
        x0=current_date,
        x1=current_date,
        y0=0,
        y1=1,
        yref="paper",
        line=dict(color="#FF0000", width=4, dash="solid")
    )
    
    # Add annotation for "Today" - Enhanced visibility
    fig.add_annotation(
        x=current_date,
        y=1.02,
        yref="paper",
        text="Today",
        showarrow=True,
        arrowhead=2,
        arrowcolor="#FF0000",
        arrowsize=1.5,
        arrowwidth=2,
        bgcolor="#FFFFFF",
        bordercolor="#FF0000",
        borderwidth=2,
        font=dict(color="#FF0000", size=12, family="Arial Black")
    )
    
    # Update layout
    fig.update_layout(
        height=max(400, len(gantt_filtered) * 25),
        xaxis_title="Timeline",
        yaxis_title="Issues",
        showlegend=True
    )
    
    # Update y-axis to show issue keys
    fig.update_yaxes(categoryorder="total ascending")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Area-based timeline view
    st.subheader("Timeline by Area")
    
    # Group by area and create separate timeline - Fixed for multi-area issues
    for area in selected_areas:
        # Check if any resource contains this area (for multi-area issues)
        area_mask = gantt_filtered['Resource'].str.contains(area, na=False)
        area_data = gantt_filtered[area_mask]
        
        if not area_data.empty:
            
            with st.expander(f"📋 {area} ({len(area_data)} issues)"):
                # Area metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    area_completed = len(area_data[area_data['Status'] == 'Done'])
                    st.metric("Completed", area_completed)
                
                with col2:
                    area_in_progress = len(area_data[area_data['Status'] == 'In Progress'])
                    st.metric("In Progress", area_in_progress)
                
                with col3:
                    if len(area_data) > 0:
                        area_completion = (area_completed / len(area_data)) * 100
                        st.metric("Completion %", f"{area_completion:.1f}%")
                
                # Area timeline
                area_fig = px.timeline(
                    area_data,
                    x_start="Start",
                    x_end="Finish",
                    y="Task",
                    color="Status",
                    title=f"{area} Timeline",
                    color_discrete_map=STATUS_COLORS,
                    hover_data=["Priority", "Assignee", "Summary"]
                )
                
                # Add current date line to area timeline using add_shape - Enhanced visibility
                area_fig.add_shape(
                    type="line",
                    x0=current_date,
                    x1=current_date,
                    y0=0,
                    y1=1,
                    yref="paper",
                    line=dict(color="#FF0000", width=4, dash="solid")
                )
                
                # Add annotation for "Today" in area timeline - Enhanced visibility
                area_fig.add_annotation(
                    x=current_date,
                    y=1.02,
                    yref="paper",
                    text="Today",
                    showarrow=True,
                    arrowhead=2,
                    arrowcolor="#FF0000",
                    arrowsize=1.5,
                    arrowwidth=2,
                    bgcolor="#FFFFFF",
                    bordercolor="#FF0000",
                    borderwidth=2,
                    font=dict(color="#FF0000", size=12, family="Arial Black")
                )
                
                area_fig.update_layout(
                    height=max(300, len(area_data) * 20),
                    showlegend=True
                )
                
                st.plotly_chart(area_fig, use_container_width=True)
                
                # Area issues table
                st.subheader(f"{area} Issues Details")
                display_columns = ['Task', 'Summary', 'Status', 'Priority', 'Assignee', 'Start', 'Finish']
                st.dataframe(
                    area_data[display_columns].sort_values('Start'),
                    use_container_width=True
                )
    
    # Summary statistics
    st.subheader("Timeline Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Issues by status in timeline
        status_counts = gantt_filtered['Status'].value_counts()
        
        fig_status = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Timeline Issues by Status",
            color_discrete_map=STATUS_COLORS
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Issues by priority in timeline
        priority_counts = gantt_filtered['Priority'].value_counts()
        
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
            title="Timeline Issues by Priority",
            color_discrete_map=priority_colors
        )
        st.plotly_chart(fig_priority, use_container_width=True)
