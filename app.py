"""
Trace Analysis Web Application

Web-based visualization tool for MCU trace logs using Dash and Plotly.
Provides interactive timeline visualization with zoom, pan, and hover details.

Usage:
    python app.py [trace_file.json]
    
    If no trace file is provided, uses unified_trace_demo.json by default.
"""

import sys
import os
from pathlib import Path
import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
from trace_parser import TraceParser, TraceVisualizer


# Configuration
DEFAULT_TRACE_FILE = "unified_trace_demo.json"
APP_TITLE = "MCU Trace Log Visualization"


def get_trace_file_path():
    """Get the trace file path from command line arguments or use default"""
    if len(sys.argv) > 1:
        trace_file = sys.argv[1]
    else:
        trace_file = DEFAULT_TRACE_FILE
    
    # Make sure the path is absolute
    if not os.path.isabs(trace_file):
        trace_file = os.path.join(os.path.dirname(__file__), trace_file)
    
    if not os.path.exists(trace_file):
        raise FileNotFoundError(f"Trace file not found: {trace_file}")
    
    return trace_file


def create_app_layout(trace_file_path: str):
    """Create the main application layout"""
    
    # Initialize parser and visualizer
    parser = TraceParser(trace_file_path)
    visualizer = TraceVisualizer(parser)
    
    # Get summary stats
    stats = visualizer.create_summary_stats()
    
    # Create the initial timeline figure
    timeline_fig = visualizer.create_timeline_figure()
    
    # App layout
    layout = html.Div([
        # Header
        html.Div([
            html.H1(APP_TITLE, style={'textAlign': 'center', 'marginBottom': '20px'}),
            html.H3(f"Trace File: {os.path.basename(trace_file_path)}", 
                    style={'textAlign': 'center', 'color': 'gray', 'marginBottom': '30px'})
        ]),
        
        # Summary Statistics
        html.Div([
            html.H3("Trace Summary", style={'marginBottom': '15px'}),
            html.Div([
                html.Div([
                    html.H4("Total Events", style={'margin': '0', 'color': '#3498db'}),
                    html.P(f"{stats['total_events']}", style={'fontSize': '24px', 'margin': '5px 0'})
                ], className='stat-box', style={
                    'display': 'inline-block', 'margin': '10px', 'padding': '15px',
                    'border': '1px solid #ddd', 'borderRadius': '5px', 'textAlign': 'center',
                    'minWidth': '120px'
                }),
                
                html.Div([
                    html.H4("Time Span", style={'margin': '0', 'color': '#e74c3c'}),
                    html.P(f"{stats['time_span']['duration']:.6f}s", style={'fontSize': '18px', 'margin': '5px 0'})
                ], className='stat-box', style={
                    'display': 'inline-block', 'margin': '10px', 'padding': '15px',
                    'border': '1px solid #ddd', 'borderRadius': '5px', 'textAlign': 'center',
                    'minWidth': '120px'
                }),
                
                html.Div([
                    html.H4("Event Types", style={'margin': '0', 'color': '#2ecc71'}),
                    html.Ul([
                        html.Li(f"{event_type}: {count}") 
                        for event_type, count in stats['event_types'].items()
                    ], style={'textAlign': 'left', 'margin': '5px 0', 'fontSize': '14px'})
                ], className='stat-box', style={
                    'display': 'inline-block', 'margin': '10px', 'padding': '15px',
                    'border': '1px solid #ddd', 'borderRadius': '5px', 'textAlign': 'center',
                    'minWidth': '200px', 'verticalAlign': 'top'
                }),
                
                html.Div([
                    html.H4("Modules", style={'margin': '0', 'color': '#f39c12'}),
                    html.Ul([
                        html.Li(f"{module}: {count}") 
                        for module, count in stats['modules'].items()
                    ], style={'textAlign': 'left', 'margin': '5px 0', 'fontSize': '14px'})
                ], className='stat-box', style={
                    'display': 'inline-block', 'margin': '10px', 'padding': '15px',
                    'border': '1px solid #ddd', 'borderRadius': '5px', 'textAlign': 'center',
                    'minWidth': '200px', 'verticalAlign': 'top'
                })
            ], style={'textAlign': 'center', 'marginBottom': '30px'})
        ]),
        
        # Instructions
        html.Div([
            html.H3("Instructions", style={'marginBottom': '15px'}),
            html.Ul([
                html.Li("Each point on the timeline represents a trace event"),
                html.Li("Events are color-coded by type and operation (see legend)"),
                html.Li("Hover over any point to see detailed event information"),
                html.Li("Use mouse wheel or zoom controls to zoom in/out on the timeline"),
                html.Li("Click and drag to pan around the timeline"),
                html.Li("Double-click to reset zoom")
            ], style={'fontSize': '14px', 'marginBottom': '20px'})
        ]),
        
        # Main Timeline Visualization
        html.Div([
            dcc.Graph(
                id='timeline-graph',
                figure=timeline_fig,
                config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
                    'toImageButtonOptions': {
                        'format': 'png',
                        'filename': 'trace_timeline',
                        'height': 600,
                        'width': 1200,
                        'scale': 1
                    }
                }
            )
        ]),
        
        # Event Type Legend/Details
        html.Div([
            html.H3("Event Type Color Legend", style={'marginTop': '30px', 'marginBottom': '15px'}),
            html.Div([
                # Bus Transaction Colors
                html.Div([
                    html.H4("Bus Transactions", style={'color': '#9b59b6', 'marginBottom': '10px'}),
                    html.Div([
                        html.Span("●", style={'color': '#3498db', 'fontSize': '20px', 'marginRight': '5px'}),
                        html.Span("READ operations", style={'marginRight': '20px'}),
                        html.Span("●", style={'color': '#e74c3c', 'fontSize': '20px', 'marginRight': '5px'}),
                        html.Span("WRITE operations")
                    ])
                ], style={'display': 'inline-block', 'margin': '10px', 'verticalAlign': 'top'}),
                
                # Device Event Colors
                html.Div([
                    html.H4("Device Events", style={'color': '#34495e', 'marginBottom': '10px'}),
                    html.Div([
                        html.Div([
                            html.Span("●", style={'color': '#2ecc71', 'fontSize': '20px', 'marginRight': '5px'}),
                            html.Span("READ", style={'marginRight': '15px'}),
                            html.Span("●", style={'color': '#f39c12', 'fontSize': '20px', 'marginRight': '5px'}),
                            html.Span("WRITE")
                        ]),
                        html.Div([
                            html.Span("●", style={'color': '#e67e22', 'fontSize': '20px', 'marginRight': '5px'}),
                            html.Span("RESET", style={'marginRight': '15px'}),
                            html.Span("●", style={'color': '#1abc9c', 'fontSize': '20px', 'marginRight': '5px'}),
                            html.Span("ENABLE")
                        ], style={'marginTop': '5px'}),
                        html.Div([
                            html.Span("●", style={'color': '#95a5a6', 'fontSize': '20px', 'marginRight': '5px'}),
                            html.Span("DISABLE", style={'marginRight': '15px'}),
                            html.Span("●", style={'color': '#f1c40f', 'fontSize': '20px', 'marginRight': '5px'}),
                            html.Span("DEMO_EVENT")
                        ], style={'marginTop': '5px'})
                    ])
                ], style={'display': 'inline-block', 'margin': '10px', 'verticalAlign': 'top'}),
                
                # IRQ Event Colors
                html.Div([
                    html.H4("IRQ Events", style={'color': '#8e44ad', 'marginBottom': '10px'}),
                    html.Div([
                        html.Span("●", style={'color': '#8e44ad', 'fontSize': '20px', 'marginRight': '5px'}),
                        html.Span("Interrupt events")
                    ])
                ], style={'display': 'inline-block', 'margin': '10px', 'verticalAlign': 'top'})
            ])
        ])
    ], style={'margin': '20px', 'fontFamily': 'Arial, sans-serif'})
    
    return layout


def main():
    """Main application entry point"""
    try:
        # Get trace file path
        trace_file_path = get_trace_file_path()
        print(f"Loading trace file: {trace_file_path}")
        
        # Initialize Dash app
        app = dash.Dash(__name__)
        app.title = APP_TITLE
        
        # Set up the layout
        app.layout = create_app_layout(trace_file_path)
        
        print("Starting web server...")
        print("Open your browser and go to: http://127.0.0.1:8050")
        
        # Run the app
        app.run_server(debug=True, host='127.0.0.1', port=8050)
        
    except Exception as e:
        print(f"Error: {e}")
        print(f"Usage: python {os.path.basename(__file__)} [trace_file.json]")
        sys.exit(1)


if __name__ == '__main__':
    main()