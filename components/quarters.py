"""
Quarter timeline visualization component for the dashboard
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
from config.settings import COLORS, AREA_COLORS


def show_quarters_dashboard(jira_client, project_key):
    """Display comprehensive quarters timeline dashboard for a specific project"""
    st.header(f"📅 Quarter Timeline: {project_key}")
    
    # Get data for the specified project
    df = jira_client.get_board_issues(project_key=project_key)
    if df.empty:
        st.warning("No data available for this project.")
        return
    
    # Debug info about dates
    st.write("**🔍 Debug - Quarter Date Analysis:**")
    total_issues = len(df)
    issues_with_start_date = len(df[df['start_date'].notna()])
    issues_with_due_date = len(df[df['due_date'].notna()])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Issues", total_issues)
    with col2:
        st.metric("With Start Date", f"{issues_with_start_date}/{total_issues}")
    with col3:
        st.metric("With Due Date", f"{issues_with_due_date}/{total_issues}")
    
    if issues_with_start_date == 0:
        st.warning("⚠️ No issues have start_date (customfield_11317). Quarters are based on created date instead.")
    
    st.markdown("---")
    
    # Quarter metrics with proper sorting
    def sort_quarters(quarter_series):
        # Convert quarters to sortable format
        quarter_list = []
        for quarter in quarter_series.index:
            if isinstance(quarter, str) and 'Q' in quarter:
                parts = quarter.split(' ')
                if len(parts) == 2:
                    q_num = int(parts[0][1:])  # Extract number from Q1, Q2, etc.
                    year = int(parts[1])
                    quarter_list.append((year, q_num, quarter))
        
        # Sort by year then quarter
        quarter_list.sort(key=lambda x: (x[0], x[1]))
        
        # Return sorted series
        sorted_quarters = [q[2] for q in quarter_list]
        return quarter_series.reindex(sorted_quarters)
    
    quarter_stats = sort_quarters(df['quarter'].value_counts())
    
    col1, col2, col3, col4 = st.columns(4)
    
    quarters = quarter_stats.index.tolist()
    
    # Calculate actual current quarter based on today's date
    today = datetime.now()
    current_quarter = f"Q{((today.month-1)//3)+1} {today.year}"
    
    if len(quarters) >= 1:
        with col1:
            # Show actual current quarter, not the last in the list
            if current_quarter in quarters:
                current_count = len(df[df['quarter'] == current_quarter])
                st.metric("Current Quarter", current_quarter, current_count)
            else:
                # If current quarter has no issues, show it with 0
                st.metric("Current Quarter", current_quarter, 0)
    
    # Calculate previous quarter based on current quarter for metrics
    current_month = today.month
    current_year = today.year
    
    if current_month <= 3:  # Q1
        prev_quarter_metric = f"Q4 {current_year - 1}"
    elif current_month <= 6:  # Q2
        prev_quarter_metric = f"Q1 {current_year}"
    elif current_month <= 9:  # Q3
        prev_quarter_metric = f"Q2 {current_year}"
    else:  # Q4
        prev_quarter_metric = f"Q3 {current_year}"
    
    with col2:
        # Show actual previous quarter based on current date
        prev_count = len(df[df['quarter'] == prev_quarter_metric])
        current_count = len(df[df['quarter'] == current_quarter])
        delta = current_count - prev_count
        st.metric("Previous Quarter", prev_quarter_metric, prev_count)
    
    with col3:
        total_quarters = len(quarter_stats)
        st.metric("Total Quarters", total_quarters)
    
    with col4:
        avg_per_quarter = df.groupby('quarter').size().mean()
        st.metric("Avg Issues/Quarter", f"{avg_per_quarter:.1f}")
    
    st.markdown("---")
    
    # Quarter distribution
    col1, col2 = st.columns(2)
    
    with col1:
        # Issues by quarter
        st.subheader("Issues by Quarter")
        
        fig_quarters = px.bar(
            x=quarter_stats.index,
            y=quarter_stats.values,
            title="Issue Distribution by Quarter",
            color=quarter_stats.values,
            color_continuous_scale='Blues'
        )
        fig_quarters.update_layout(
            xaxis_title="Quarter",
            yaxis_title="Number of Issues",
            showlegend=False
        )
        st.plotly_chart(fig_quarters, use_container_width=True)
    
    with col2:
        # Quarter completion status
        st.subheader("Quarter Completion Status")
        
        quarter_status = df.groupby(['quarter', 'status']).size().unstack(fill_value=0)
        
        if 'Done' in quarter_status.columns:
            quarter_status['completion_rate'] = (
                quarter_status['Done'] / quarter_status.sum(axis=1) * 100
            )
            
            fig_completion = px.bar(
                x=quarter_status.index,
                y=quarter_status['completion_rate'],
                title="Completion Rate by Quarter (%)",
                color=quarter_status['completion_rate'],
                color_continuous_scale='Greens'
            )
            fig_completion.update_layout(
                xaxis_title="Quarter",
                yaxis_title="Completion Rate (%)",
                showlegend=False
            )
            st.plotly_chart(fig_completion, use_container_width=True)
    
    # Quarter timeline with areas
    st.subheader("Quarter Timeline by Area")
    
    # Create quarter-area breakdown with proper sorting
    quarter_area = df.groupby(['quarter', 'areas']).size().reset_index(name='count')
    
    if not quarter_area.empty:
        # Sort quarters chronologically
        def sort_quarter_key(quarter):
            if isinstance(quarter, str) and 'Q' in quarter:
                parts = quarter.split(' ')
                if len(parts) == 2:
                    q_num = int(parts[0][1:])
                    year = int(parts[1])
                    return (year, q_num)
            return (0, 0)
        
        quarter_area['sort_key'] = quarter_area['quarter'].apply(sort_quarter_key)
        quarter_area = quarter_area.sort_values('sort_key').drop('sort_key', axis=1)
        
        fig_timeline = px.bar(
            quarter_area,
            x='quarter',
            y='count',
            color='areas',
            title="Issues Timeline by Quarter and Area",
            color_discrete_map=AREA_COLORS,
            category_orders={'quarter': sorted(quarter_area['quarter'].unique(), key=sort_quarter_key)}
        )
        fig_timeline.update_layout(
            xaxis_title="Quarter",
            yaxis_title="Number of Issues"
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Quarter roadmap view
    st.subheader("Quarter Roadmap")
    
    # Quarter filters
    col1, col2 = st.columns(2)
    
    with col1:
        # Predefined quarter options
        predefined_quarters = [
            "Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025",
            "Q1 2026", "Q2 2026", "Q3 2026", "Q4 2026"
        ]
        
        # Get available quarters from data
        available_quarters = sorted(df['quarter'].unique(), reverse=True)
        
        # Combine predefined with available quarters
        all_quarter_options = []
        for q in predefined_quarters:
            if q in available_quarters:
                all_quarter_options.append(q)
        
        # Add any other quarters from data not in predefined list
        for q in available_quarters:
            if q not in predefined_quarters and q not in all_quarter_options:
                all_quarter_options.append(q)
        
        # Default to current quarter if available, otherwise first option
        default_quarter = current_quarter if current_quarter in (all_quarter_options if all_quarter_options else available_quarters) else (all_quarter_options[0] if all_quarter_options else available_quarters[0])
        
        selected_quarter = st.selectbox(
            "Select Quarter for Detailed View",
            options=all_quarter_options if all_quarter_options else available_quarters,
            index=(all_quarter_options if all_quarter_options else available_quarters).index(default_quarter) if default_quarter in (all_quarter_options if all_quarter_options else available_quarters) else 0
        )
    
    with col2:
        # Multi-select for quarter comparison
        selected_quarters_multi = st.multiselect(
            "Select Quarters for Comparison",
            options=all_quarter_options if all_quarter_options else available_quarters,
            default=all_quarter_options[:2] if len(all_quarter_options) >= 2 else available_quarters[:2]
        )
    
    quarter_data = df[df['quarter'] == selected_quarter]
    
    if not quarter_data.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Status breakdown for selected quarter
            status_counts = quarter_data['status'].value_counts()
            
            fig_status = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title=f"{selected_quarter} - Status Distribution"
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            # Area breakdown for selected quarter
            area_counts = quarter_data['areas'].value_counts()
            
            fig_areas = px.pie(
                values=area_counts.values,
                names=area_counts.index,
                title=f"{selected_quarter} - Area Distribution",
                color_discrete_map=AREA_COLORS
            )
            st.plotly_chart(fig_areas, use_container_width=True)
        
        # Detailed issues for selected quarter
        st.subheader(f"Issues in {selected_quarter}")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.multiselect(
                "Filter by Status",
                options=quarter_data['status'].unique(),
                default=quarter_data['status'].unique(),
                key="quarter_status_filter"
            )
        
        with col2:
            area_filter = st.multiselect(
                "Filter by Area",
                options=quarter_data['areas'].unique(),
                default=quarter_data['areas'].unique(),
                key="quarter_area_filter"
            )
        
        with col3:
            priority_filter = st.multiselect(
                "Filter by Priority",
                options=quarter_data['priority'].unique(),
                default=quarter_data['priority'].unique(),
                key="quarter_priority_filter"
            )
        
        # Apply filters
        filtered_quarter_data = quarter_data[
            (quarter_data['status'].isin(status_filter)) &
            (quarter_data['areas'].isin(area_filter)) &
            (quarter_data['priority'].isin(priority_filter))
        ]
        
        st.write(f"Showing {len(filtered_quarter_data)} issues in {selected_quarter}")
        
        if not filtered_quarter_data.empty:
            # Show debug info about dates
            st.write("**Debug - Date Information:**")
            issues_with_start_date = len(filtered_quarter_data[filtered_quarter_data['start_date'].notna()])
            issues_with_due_date = len(filtered_quarter_data[filtered_quarter_data['due_date'].notna()])
            st.write(f"- Issues with Start Date: {issues_with_start_date}/{len(filtered_quarter_data)}")
            st.write(f"- Issues with Due Date: {issues_with_due_date}/{len(filtered_quarter_data)}")
            
            display_columns = ['key', 'summary', 'status', 'priority', 'assignee', 'areas', 'start_date', 'due_date', 'created']
            st.dataframe(
                filtered_quarter_data[display_columns].sort_values('created', ascending=False),
                use_container_width=True
            )
        else:
            st.info("No issues match the selected filters.")
    
    # Quarter comparison
    st.subheader("Quarter Comparison")
    
    # Calculate previous quarter based on current quarter
    current_month = today.month
    current_year = today.year
    
    if current_month <= 3:  # Q1
        prev_quarter = f"Q4 {current_year - 1}"
    elif current_month <= 6:  # Q2
        prev_quarter = f"Q1 {current_year}"
    elif current_month <= 9:  # Q3
        prev_quarter = f"Q2 {current_year}"
    else:  # Q4
        prev_quarter = f"Q3 {current_year}"
    
    # Get data for current and previous quarters
    current_data = df[df['quarter'] == current_quarter]
    previous_data = df[df['quarter'] == prev_quarter]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**{current_quarter} (Current)**")
        st.metric("Total Issues", len(current_data))
        st.metric("Completed", len(current_data[current_data['status'] == 'Done']))
        st.metric("In Progress", len(current_data[current_data['status'] == 'In Progress']))
    
    with col2:
        st.write(f"**{prev_quarter} (Previous)**")
        st.metric("Total Issues", len(previous_data))
        st.metric("Completed", len(previous_data[previous_data['status'] == 'Done']))
        st.metric("In Progress", len(previous_data[previous_data['status'] == 'In Progress']))
    
    # Quarter comparison chart
    comparison_data = pd.DataFrame({
        'Quarter': [prev_quarter, current_quarter],
        'Total Issues': [len(previous_data), len(current_data)],
        'Completed': [
            len(previous_data[previous_data['status'] == 'Done']),
            len(current_data[current_data['status'] == 'Done'])
        ]
    })
    
    fig_comparison = px.bar(
        comparison_data,
        x='Quarter',
        y=['Total Issues', 'Completed'],
        title="Current vs Previous Quarter Comparison",
        barmode='group'
    )
    st.plotly_chart(fig_comparison, use_container_width=True)
