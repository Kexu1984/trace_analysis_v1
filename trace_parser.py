"""
Trace Analysis Visualization Tool

This module provides web-based visualization for MCU trace logs.
Supports interactive timeline visualization with zoom, pan, and hover details.
"""

import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from typing import Dict, List, Any, Tuple


class EventType:
    """Event type constants matching the trace log format"""
    BUS_TRANSACTION = 'BUS_TRANSACTION'
    IRQ_EVENT = 'IRQ_EVENT'
    DEVICE_EVENT = 'DEVICE_EVENT'


class BusOperation:
    """Bus operation constants"""
    READ = 'READ'
    WRITE = 'WRITE'


class DeviceOperation:
    """Device operation constants"""
    READ = 'READ'
    WRITE = 'WRITE'
    READ_FAILED = 'READ_FAILED'
    WRITE_FAILED = 'WRITE_FAILED'
    RESET = 'RESET'
    ENABLE = 'ENABLE'
    DISABLE = 'DISABLE'
    IRQ_TRIGGER = 'IRQ_TRIGGER'
    IRQ_TRIGGER_FAILED = 'IRQ_TRIGGER_FAILED'
    INIT_START = 'INIT_START'
    INIT_COMPLETE = 'INIT_COMPLETE'
    RESET_START = 'RESET_START'
    RESET_COMPLETE = 'RESET_COMPLETE'
    SHUTDOWN_START = 'SHUTDOWN_START'
    SHUTDOWN_COMPLETE = 'SHUTDOWN_COMPLETE'


class TraceParser:
    """Parser for trace log JSON files"""
    
    def __init__(self, trace_file_path: str):
        self.trace_file_path = trace_file_path
        self.trace_data = None
        self.events_df = None
        
    def load_trace_data(self) -> Dict[str, Any]:
        """Load trace data from JSON file"""
        try:
            with open(self.trace_file_path, 'r') as f:
                self.trace_data = json.load(f)
            return self.trace_data
        except FileNotFoundError:
            raise FileNotFoundError(f"Trace file not found: {self.trace_file_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in file: {self.trace_file_path}")
    
    def parse_events(self) -> pd.DataFrame:
        """Parse events into a pandas DataFrame for easier processing"""
        if not self.trace_data:
            self.load_trace_data()
            
        events = []
        for event in self.trace_data['events']:
            parsed_event = {
                'timestamp': event['timestamp'],
                'formatted_time': event['formatted_time'],
                'module_name': event['module_name'],
                'event_type': event['event_type'],
            }
            
            # Flatten event_data for easier access
            if 'event_data' in event:
                for key, value in event['event_data'].items():
                    parsed_event[f'data_{key}'] = value
            
            events.append(parsed_event)
        
        self.events_df = pd.DataFrame(events)
        return self.events_df
    
    def get_event_color(self, event_type: str, operation: str = None) -> str:
        """Get color for event based on type and operation"""
        color_map = {
            EventType.BUS_TRANSACTION: {
                BusOperation.READ: '#3498db',     # Blue
                BusOperation.WRITE: '#e74c3c',    # Red
                'default': '#9b59b6'              # Purple
            },
            EventType.DEVICE_EVENT: {
                DeviceOperation.READ: '#2ecc71',          # Green
                DeviceOperation.WRITE: '#f39c12',         # Orange
                DeviceOperation.RESET: '#e67e22',         # Dark Orange
                DeviceOperation.ENABLE: '#1abc9c',        # Turquoise
                DeviceOperation.DISABLE: '#95a5a6',       # Gray
                'DEMO_EVENT': '#f1c40f',                   # Yellow for demo events
                'default': '#34495e'                       # Dark Gray
            },
            EventType.IRQ_EVENT: {
                'default': '#8e44ad'              # Dark Purple
            }
        }
        
        event_colors = color_map.get(event_type, {})
        if operation and operation in event_colors:
            return event_colors[operation]
        return event_colors.get('default', '#7f7f7f')
    
    def create_hover_text(self, row: pd.Series) -> str:
        """Create detailed hover text for an event"""
        hover_parts = [
            f"<b>Time:</b> {row['formatted_time']}",
            f"<b>Module:</b> {row['module_name']}",
            f"<b>Event Type:</b> {row['event_type']}"
        ]
        
        # Add event-specific data
        data_fields = [col for col in row.index if col.startswith('data_')]
        for field in data_fields:
            if pd.notna(row[field]) and row[field] is not None:
                field_name = field.replace('data_', '').replace('_', ' ').title()
                hover_parts.append(f"<b>{field_name}:</b> {row[field]}")
        
        return "<br>".join(hover_parts)


class TraceVisualizer:
    """Creates interactive timeline visualization for trace events"""
    
    def __init__(self, parser: TraceParser):
        self.parser = parser
        self.events_df = None
        
    def prepare_data(self):
        """Prepare data for visualization"""
        self.events_df = self.parser.parse_events()
        
        # Add y-position for timeline (group by module_name for lanes)
        unique_modules = self.events_df['module_name'].unique()
        module_positions = {module: i for i, module in enumerate(unique_modules)}
        self.events_df['y_position'] = self.events_df['module_name'].map(module_positions)
        
        # Add colors
        colors = []
        for _, row in self.events_df.iterrows():
            operation = row.get('data_operation', None)
            color = self.parser.get_event_color(row['event_type'], operation)
            colors.append(color)
        self.events_df['color'] = colors
        
        # Add hover text
        self.events_df['hover_text'] = self.events_df.apply(self.parser.create_hover_text, axis=1)
    
    def create_timeline_figure(self) -> go.Figure:
        """Create the main timeline visualization"""
        if self.events_df is None:
            self.prepare_data()
        
        fig = go.Figure()
        
        # Group events by type for legend
        event_types = self.events_df['event_type'].unique()
        
        for event_type in event_types:
            type_events = self.events_df[self.events_df['event_type'] == event_type]
            
            fig.add_trace(go.Scatter(
                x=type_events['timestamp'],
                y=type_events['y_position'],
                mode='markers',
                marker=dict(
                    color=type_events['color'],
                    size=10,
                    line=dict(width=1, color='white')
                ),
                text=type_events['hover_text'],
                hovertemplate='%{text}<extra></extra>',
                name=event_type,
                showlegend=True
            ))
        
        # Customize layout
        fig.update_layout(
            title=dict(
                text="MCU Trace Log Timeline Visualization",
                x=0.5,
                font=dict(size=20)
            ),
            xaxis=dict(
                title="Timeline",
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray',
                zeroline=False
            ),
            yaxis=dict(
                title="Module",
                tickmode='array',
                tickvals=list(range(len(self.events_df['module_name'].unique()))),
                ticktext=list(self.events_df['module_name'].unique()),
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray',
                zeroline=False
            ),
            hovermode='closest',
            plot_bgcolor='white',
            width=1200,
            height=600,
            margin=dict(l=100, r=50, t=80, b=80)
        )
        
        return fig
    
    def create_summary_stats(self) -> Dict[str, Any]:
        """Create summary statistics for the trace data"""
        if self.events_df is None:
            self.prepare_data()
        
        stats = {
            'total_events': len(self.events_df),
            'event_types': self.events_df['event_type'].value_counts().to_dict(),
            'modules': self.events_df['module_name'].value_counts().to_dict(),
            'time_span': {
                'start': self.events_df['formatted_time'].iloc[0],
                'end': self.events_df['formatted_time'].iloc[-1],
                'duration': self.events_df['timestamp'].iloc[-1] - self.events_df['timestamp'].iloc[0]
            }
        }
        
        return stats