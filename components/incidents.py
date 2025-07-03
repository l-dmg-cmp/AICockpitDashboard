"""
Incident visualization component for the dashboard
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
from config.settings import COLORS, STATUS_COLORS


def show_incidents_dashboard(jira_client):
    """Display comprehensive incidents dashboard"""
    st.header("🚨 Incident Analysis Dashboard")
    
    # For incidents tab, get ALL incidents including those without area labels
    try:
        all_incidents_issues = jira_client.jira.search_issues(
            f'project = AICP AND type = 10300',
            maxResults=1000
        )
        
        incidents_data = []
        for issue in all_incidents_issues:
            # Extract labels
            all_labels = [str(label) for label in issue.fields.labels] if issue.fields.labels else []
            
            # Filter and normalize labels
            filtered_labels = []
            for label in all_labels:
                label_lower = label.lower()
                if 'desenvolvimento' in label_lower or 'development' in label_lower:
                    filtered_labels.append('Desenvolvimento')
                elif 'devops' in label_lower:
                    filtered_labels.append('DevOps')
                elif 'qualidade' in label_lower or 'quality' in label_lower:
                    filtered_labels.append('Qualidade')
                elif 'dados' in label_lower or 'data' in label_lower:
                    filtered_labels.append('Dados')
                elif 'arquitetura' in label_lower or 'architecture' in label_lower:
                    filtered_labels.append('Arquitetura')
            
            labels = list(set(filtered_labels))
            
            assignee = issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned"
            created = datetime.strptime(issue.fields.created[:19], '%Y-%m-%dT%H:%M:%S')
            updated = datetime.strptime(issue.fields.updated[:19], '%Y-%m-%dT%H:%M:%S')
            
            incidents_data.append({
                'key': issue.key,
                'summary': issue.fields.summary,
                'status': issue.fields.status.name,
                'priority': issue.fields.priority.name if issue.fields.priority else 'Medium',
                'assignee': assignee,
                'reporter': issue.fields.reporter.displayName if issue.fields.reporter else 'Unknown',
                'issue_type': issue.fields.issuetype.name,
                'areas': ', '.join(labels) if labels else 'No Area',
                'created': created,
                'updated': updated,
                'is_incident': True
            })
        
        incidents_df = pd.DataFrame(incidents_data)
        
    except Exception as e:
        st.error(f"Error fetching incidents: {str(e)}")
        return
    
    if incidents_df.empty:
        st.info("No incidents found in the current dataset.")
        return
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_incidents = len(incidents_df)
        st.metric("Total Incidents", total_incidents)
    
    with col2:
        open_incidents = len(incidents_df[incidents_df['status'] != 'Done'])
        st.metric("Open Incidents", open_incidents)
    
    with col3:
        closed_incidents = len(incidents_df[incidents_df['status'] == 'Done'])
        st.metric("Closed Incidents", closed_incidents)
    
    with col4:
        if total_incidents > 0:
            resolution_rate = (closed_incidents / total_incidents) * 100
            st.metric("Resolution Rate", f"{resolution_rate:.1f}%")
        else:
            st.metric("Resolution Rate", "0%")
    
    st.markdown("---")
    
    st.subheader("📊 Incident Distribution Analysis")
    
    # Charts row with filter integrated
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Incident status distribution
        st.subheader("Incident Status Distribution")
        status_counts = incidents_df['status'].value_counts()
        
        colors = [STATUS_COLORS.get(status, COLORS['primary']) for status in status_counts.index]
        
        fig_status = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Incidents by Status",
            color_discrete_sequence=colors
        )
        fig_status.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Incident priority distribution with clickable legend filter
        st.subheader("Incident Priority Distribution")
        
        # Create a stacked bar chart by status and priority with clickable legend
        priority_status_df = incidents_df.groupby(['priority', 'status']).size().reset_index(name='count')
        
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
            title="Incidents by Priority (Click legend to filter)",
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
    
    # Detailed incidents table
    st.subheader("Incident Details")
    
    # Filter options
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.multiselect(
            "Filter by Status",
            options=incidents_df['status'].unique(),
            default=incidents_df['status'].unique(),
            key="incidents_status_filter"
        )
    
    with col2:
        priority_filter = st.multiselect(
            "Filter by Priority", 
            options=incidents_df['priority'].unique(),
            default=incidents_df['priority'].unique(),
            key="incidents_priority_filter"
        )
        
    with col3:
        area_filter = st.multiselect(
            "Filter by Area",
            options=incidents_df['areas'].unique(),
            default=incidents_df['areas'].unique(),
            key="incidents_area_filter"
        )
    
    with col4:
        type_filter = st.multiselect(
            "Filter by Type",
            options=incidents_df['issue_type'].unique(),
            default=incidents_df['issue_type'].unique(),
            key="incidents_type_filter"
        )
    
    # Apply filters
    filtered_incidents = incidents_df[
        (incidents_df['status'].isin(status_filter)) &
        (incidents_df['priority'].isin(priority_filter)) &
        (incidents_df['areas'].isin(area_filter)) &
        (incidents_df['issue_type'].isin(type_filter))
    ]
    
    # Display filtered results count
    st.write(f"Showing {len(filtered_incidents)} incidents")
    
    # Display table
    if not filtered_incidents.empty:
        display_columns = ['key', 'summary', 'status', 'priority', 'assignee', 'areas', 'created']
        st.dataframe(
            filtered_incidents[display_columns].sort_values('created', ascending=False),
            use_container_width=True
        )
    else:
        st.info("No incidents match the selected filters.")
