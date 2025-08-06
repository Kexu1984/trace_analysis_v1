#!/usr/bin/env python3
"""
Simple test script to verify the trace parser and visualizer functionality.
"""

import os
import sys
from trace_parser import TraceParser, TraceVisualizer

def test_trace_parsing():
    """Test basic trace parsing functionality"""
    
    # Get the demo trace file
    trace_file = os.path.join(os.path.dirname(__file__), 'unified_trace_demo.json')
    
    if not os.path.exists(trace_file):
        print(f"ERROR: Demo trace file not found: {trace_file}")
        return False
    
    try:
        # Test parser
        print("Testing TraceParser...")
        parser = TraceParser(trace_file)
        trace_data = parser.load_trace_data()
        
        # Verify trace info
        assert 'trace_info' in trace_data
        assert 'events' in trace_data
        assert trace_data['trace_info']['total_events'] == 13
        print(f"✓ Loaded {trace_data['trace_info']['total_events']} events")
        
        # Test events parsing
        events_df = parser.parse_events()
        assert len(events_df) == 13
        print(f"✓ Parsed {len(events_df)} events into DataFrame")
        
        # Verify event types
        event_types = events_df['event_type'].unique()
        expected_types = ['DEVICE_EVENT', 'BUS_TRANSACTION']
        for event_type in expected_types:
            assert event_type in event_types
        print(f"✓ Found expected event types: {list(event_types)}")
        
        # Test visualizer
        print("Testing TraceVisualizer...")
        visualizer = TraceVisualizer(parser)
        
        # Test data preparation
        visualizer.prepare_data()
        assert visualizer.events_df is not None
        assert 'y_position' in visualizer.events_df.columns
        assert 'color' in visualizer.events_df.columns
        assert 'hover_text' in visualizer.events_df.columns
        print("✓ Data preparation successful")
        
        # Test figure creation
        fig = visualizer.create_timeline_figure()
        assert fig is not None
        assert len(fig.data) > 0  # Should have traces
        print("✓ Timeline figure creation successful")
        
        # Test summary stats
        stats = visualizer.create_summary_stats()
        assert stats['total_events'] == 13
        assert 'event_types' in stats
        assert 'modules' in stats
        assert 'time_span' in stats
        print("✓ Summary statistics generation successful")
        
        print("\n🎉 All tests passed! The visualization tool is working correctly.")
        return True
        
    except Exception as e:
        print(f"ERROR: Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_trace_parsing()
    sys.exit(0 if success else 1)