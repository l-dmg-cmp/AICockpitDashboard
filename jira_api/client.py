"""
Jira API client for fetching board and issue data
"""

import streamlit as st
import pandas as pd
from jira import JIRA
from datetime import datetime, timedelta
from config.settings import JIRA_SERVER, PROJECT_KEY, BOARD_ID, AREAS


class JiraClient:
    def __init__(self, email, api_key):
        """Initialize Jira client with credentials"""
        self.email = email
        self.api_key = api_key
        self.jira = JIRA(
            server=JIRA_SERVER,
            basic_auth=(email, api_key),
            timeout=30,  # 30 second timeout for data operations
            max_retries=2
        )
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_board_issues(_self):
        """Fetch all issues from the board"""
        try:
            # Search for issues with specific labels regardless of project
            label_queries = [
                'labels = "DevOps"',
                'labels = "Arquitetura"', 
                'labels = "Desenvolvimento"',
                'labels = "Dados"',
                'labels = "Qualidade"'
            ]
            
            all_issues = []
            existing_keys = set()
            
            # Get issues from each label query
            for query in label_queries:
                try:
                    label_issues = _self.jira.search_issues(query, maxResults=500, fields='*all')
                    for issue in label_issues:
                        if issue.key not in existing_keys:
                            all_issues.append(issue)
                            existing_keys.add(issue.key)
                except Exception as e:
                    print(f"DEBUG: Failed to search for {query}: {e}")
                    continue
            
            # Also get issues from AICP project (in case some don't have labels)
            try:
                aicp_issues = _self.jira.search_issues(
                    f'project = {PROJECT_KEY}',
                    maxResults=1000,
                    expand='changelog',
                    fields='*all'
                )
                for issue in aicp_issues:
                    if issue.key not in existing_keys:
                        all_issues.append(issue)
                        existing_keys.add(issue.key)
            except Exception as e:
                print(f"DEBUG: Failed to search AICP project: {e}")
            
            issues = all_issues
            
            issues_data = []
            for issue in issues:
                # Extract and filter labels from Jira issue
                all_labels = [str(label) for label in issue.fields.labels] if issue.fields.labels else []
                
                # Filter and normalize labels to only show configured areas
                filtered_labels = []
                for label in all_labels:
                    label_lower = label.lower()
                    if 'desenvolvimento' in label_lower or 'development' in label_lower:
                        filtered_labels.append('Desenvolvimento')
                    elif 'devops' in label_lower:  # This will catch both DevOps and DEVOPS
                        filtered_labels.append('DevOps')
                    elif 'qualidade' in label_lower or 'quality' in label_lower:
                        filtered_labels.append('Qualidade')
                    elif 'dados' in label_lower or 'data' in label_lower:
                        filtered_labels.append('Dados')
                    elif 'arquitetura' in label_lower or 'architecture' in label_lower:
                        filtered_labels.append('Arquitetura')
                
                # Remove duplicates and keep only our configured areas
                labels = list(set(filtered_labels))
                
                # Get assignee info
                assignee = issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned"
                
                # Get dates
                created = datetime.strptime(issue.fields.created[:19], '%Y-%m-%dT%H:%M:%S')
                updated = datetime.strptime(issue.fields.updated[:19], '%Y-%m-%dT%H:%M:%S')
                
                # Get due date if available
                due_date = None
                if hasattr(issue.fields, 'duedate') and issue.fields.duedate:
                    try:
                        # Try standard format first (YYYY-MM-DD)
                        due_date = datetime.strptime(issue.fields.duedate, '%Y-%m-%d')
                    except:
                        try:
                            # Try the format you showed: Wed, 31 Dec 2025 00:00:00 +0000
                            due_date = datetime.strptime(issue.fields.duedate[:25], '%a, %d %b %Y %H:%M:%S')
                        except:
                            due_date = None
                
                # Get start date from custom field if available
                start_date = None
                if hasattr(issue.fields, 'customfield_11317') and issue.fields.customfield_11317:
                    try:
                        # Try YYYY-MM-DD format first
                        start_date = datetime.strptime(issue.fields.customfield_11317, '%Y-%m-%d')
                    except:
                        try:
                            # Try the full format: Mon, 26 May 2025 00:00:00 +0000
                            start_date = datetime.strptime(issue.fields.customfield_11317[:25], '%a, %d %b %Y %H:%M:%S')
                        except Exception as e:
                            start_date = None
                
                # Determine quarter based on start date if available, otherwise created date
                if start_date:
                    quarter = _self._get_quarter(start_date)
                else:
                    quarter = _self._get_quarter(created)
                
                # Only include issues that have at least one of our configured areas
                if labels:  # Skip issues with no matching area labels
                    issue_data = {
                        'key': issue.key,
                        'summary': issue.fields.summary,
                        'status': issue.fields.status.name,
                        'priority': issue.fields.priority.name if issue.fields.priority else 'Medium',
                        'assignee': assignee,
                        'reporter': issue.fields.reporter.displayName if issue.fields.reporter else 'Unknown',
                        'issue_type': issue.fields.issuetype.name,
                        'labels': labels,
                        'areas': ', '.join(labels),
                        'created': created,
                        'updated': updated,
                        'due_date': due_date,
                        'start_date': start_date,
                        'quarter': quarter,
                        'is_bug': issue.fields.issuetype.name.lower() in ['bug', 'defect', 'error'],
                        'story_points': getattr(issue.fields, 'customfield_10016', None),  # Common story points field
                        'description': issue.fields.description[:200] + '...' if issue.fields.description else ''
                    }
                    
                    issues_data.append(issue_data)
            
            return pd.DataFrame(issues_data)
            
        except Exception as e:
            st.error(f"Error fetching issues: {str(e)}")
            return pd.DataFrame()
    
    def _get_quarter(self, date):
        """Determine quarter from date"""
        month = date.month
        year = date.year
        
        if month <= 3:
            return f"Q1 {year}"
        elif month <= 6:
            return f"Q2 {year}"
        elif month <= 9:
            return f"Q3 {year}"
        else:
            return f"Q4 {year}"
    
    @st.cache_data(ttl=300)
    def get_project_statistics(_self):
        """Get project statistics and metrics"""
        try:
            df = _self.get_board_issues()
            if df.empty:
                return {}
            
            stats = {
                'total_issues': len(df),
                'bugs_count': len(df[df['is_bug'] == True]),
                'open_issues': len(df[df['status'] != 'Done']),
                'closed_issues': len(df[df['status'] == 'Done']),
                'by_priority': df['priority'].value_counts().to_dict(),
                'by_status': df['status'].value_counts().to_dict(),
                'by_assignee': df['assignee'].value_counts().head(10).to_dict(),
                'by_area': df['areas'].value_counts().to_dict(),
                'by_quarter': df['quarter'].value_counts().to_dict()
            }
            
            return stats
            
        except Exception as e:
            st.error(f"Error getting statistics: {str(e)}")
            return {}
    
    def get_gantt_data(self, selected_areas=None):
        """Get data formatted for Gantt chart"""
        try:
            df = self.get_board_issues()
            if df.empty:
                return pd.DataFrame()
            
            # Filter by selected areas if provided - Fixed for multi-area issues
            if selected_areas:
                def check_area_match(areas_string):
                    if areas_string == 'No Area':
                        return 'No Area' in selected_areas
                    else:
                        # Split the areas and check if any selected area is in the issue's areas
                        issue_areas = [area.strip() for area in areas_string.split(',')]
                        return any(selected_area in issue_areas for selected_area in selected_areas)
                
                area_mask = df['areas'].apply(check_area_match)
                df = df[area_mask]
            
            # Prepare Gantt data
            gantt_data = []
            for _, row in df.iterrows():
                # Use custom start date if available, otherwise use created date
                if row['start_date']:
                    start_date = row['start_date']
                else:
                    start_date = row['created']
                
                # Use due date or estimate end date
                if row['due_date']:
                    end_date = row['due_date']
                else:
                    # Estimate 2 weeks for tasks without due date
                    end_date = start_date + timedelta(days=14)
                
                # Truncate summary for display
                summary_short = row['summary'][:50] + '...' if len(row['summary']) > 50 else row['summary']
                
                gantt_data.append({
                    'Task': f"{row['key']} - {summary_short}",
                    'Start': start_date,
                    'Finish': end_date,
                    'Resource': row['areas'] if row['areas'] != 'No Area' else 'General',
                    'Status': row['status'],
                    'Priority': row['priority'],
                    'Assignee': row['assignee'],
                    'Summary': row['summary'],
                    'Key': row['key']
                })
            
            return pd.DataFrame(gantt_data)
            
        except Exception as e:
            st.error(f"Error preparing Gantt data: {str(e)}")
            return pd.DataFrame()
