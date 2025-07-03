"""
Alternative Jira API client using requests library instead of jira library
"""

import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime, timedelta
from config.settings import JIRA_SERVER, PROJECT_KEY, BOARD_ID, AREAS


class JiraClientRequests:
    def __init__(self, email, api_key):
        """Initialize Jira client with credentials"""
        self.email = email
        self.api_key = api_key
        
        # Create auth header
        auth_str = f'{email}:{api_key}'
        auth_bytes = auth_str.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        self.headers = {
            'Authorization': f'Basic {auth_b64}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, endpoint, params=None):
        """Make authenticated request to Jira API"""
        try:
            url = f'{JIRA_SERVER}/rest/api/2/{endpoint}'
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_board_issues(_self):
        """Fetch all issues from the board using requests"""
        try:
            all_issues = []
            
            # Search for issues with specific labels
            label_queries = [
                'labels = "DevOps"',
                'labels = "Arquitetura"', 
                'labels = "Desenvolvimento"',
                'labels = "Dados"',
                'labels = "Qualidade"'
            ]
            
            existing_keys = set()
            
            # Get issues from each label query
            for query in label_queries:
                try:
                    search_data = _self._make_request('search', {
                        'jql': query,
                        'maxResults': 500,
                        'fields': '*all'
                    })
                    
                    if search_data and 'issues' in search_data:
                        for issue_data in search_data['issues']:
                            if issue_data['key'] not in existing_keys:
                                all_issues.append(issue_data)
                                existing_keys.add(issue_data['key'])
                except Exception as e:
                    print(f"DEBUG: Failed to search for {query}: {e}")
                    continue
            
            # Also get issues from AICP project
            try:
                search_data = _self._make_request('search', {
                    'jql': f'project = {PROJECT_KEY}',
                    'maxResults': 1000,
                    'fields': '*all'
                })
                
                if search_data and 'issues' in search_data:
                    for issue_data in search_data['issues']:
                        if issue_data['key'] not in existing_keys:
                            all_issues.append(issue_data)
                            existing_keys.add(issue_data['key'])
            except Exception as e:
                print(f"DEBUG: Failed to search AICP project: {e}")
            
            # Process issues data
            issues_data = []
            for issue_data in all_issues:
                try:
                    fields = issue_data['fields']
                    
                    # Extract labels
                    all_labels = [str(label) for label in fields.get('labels', [])]
                    
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
                    
                    # Get assignee
                    assignee = "Unassigned"
                    if fields.get('assignee'):
                        assignee = fields['assignee'].get('displayName', 'Unknown')
                    
                    # Get dates
                    created = datetime.strptime(fields['created'][:19], '%Y-%m-%dT%H:%M:%S')
                    updated = datetime.strptime(fields['updated'][:19], '%Y-%m-%dT%H:%M:%S')
                    
                    # Get due date
                    due_date = None
                    if fields.get('duedate'):
                        try:
                            due_date = datetime.strptime(fields['duedate'], '%Y-%m-%d')
                        except:
                            due_date = None
                    
                    # Get start date from custom field
                    start_date = None
                    if fields.get('customfield_11317'):
                        try:
                            start_date = datetime.strptime(fields['customfield_11317'], '%Y-%m-%d')
                        except:
                            start_date = None
                    
                    # Determine quarter
                    quarter_date = start_date if start_date else created
                    quarter = _self._get_quarter(quarter_date)
                    
                    # Only include issues with matching area labels
                    if labels:
                        issue_info = {
                            'key': issue_data['key'],
                            'summary': fields['summary'],
                            'status': fields['status']['name'],
                            'priority': fields['priority']['name'] if fields.get('priority') else 'Medium',
                            'assignee': assignee,
                            'reporter': fields['reporter']['displayName'] if fields.get('reporter') else 'Unknown',
                            'issue_type': fields['issuetype']['name'],
                            'labels': labels,
                            'areas': ', '.join(labels),
                            'created': created,
                            'updated': updated,
                            'due_date': due_date,
                            'start_date': start_date,
                            'quarter': quarter,
                            'is_bug': fields['issuetype']['name'].lower() in ['bug', 'defect', 'error'],
                            'story_points': fields.get('customfield_10016'),
                            'description': fields.get('description', '')[:200] + '...' if fields.get('description') else ''
                        }
                        issues_data.append(issue_info)
                        
                except Exception as e:
                    print(f"Error processing issue {issue_data.get('key', 'unknown')}: {e}")
                    continue
            
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
            
            # Filter by selected areas if provided
            if selected_areas:
                def check_area_match(areas_string):
                    if areas_string == 'No Area':
                        return 'No Area' in selected_areas
                    else:
                        issue_areas = [area.strip() for area in areas_string.split(',')]
                        return any(selected_area in issue_areas for selected_area in selected_areas)
                
                area_mask = df['areas'].apply(check_area_match)
                df = df[area_mask]
            
            # Prepare Gantt data
            gantt_data = []
            for _, row in df.iterrows():
                start_date = row['start_date'] if row['start_date'] else row['created']
                end_date = row['due_date'] if row['due_date'] else start_date + timedelta(days=14)
                
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
