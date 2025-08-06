# MCU Trace Analysis Visualization Tool

A web-based visualization tool for analyzing MCU driver trace logs. This tool provides an interactive timeline visualization with zoom, pan, and hover capabilities to help diagnose potential issues in MCU driver code.

## Features

- **Interactive Timeline Visualization**: Time-based horizontal timeline showing all trace events
- **Color-Coded Events**: Different colors for different event types and operations
- **Zoom and Pan**: Mouse wheel zoom and drag-to-pan functionality  
- **Hover Details**: Detailed tooltips showing complete event information
- **Module Organization**: Events organized by module/component
- **Summary Statistics**: Overview of event counts, time spans, and module breakdown

## Supported Event Types

The tool supports visualization of three main event types:

### Bus Transactions (`BUS_TRANSACTION`)
- **READ** operations (Blue)
- **WRITE** operations (Red)

### Device Events (`DEVICE_EVENT`) 
- **READ** (Green)
- **WRITE** (Orange)
- **RESET** (Dark Orange)
- **ENABLE** (Turquoise)
- **DISABLE** (Gray)
- **IRQ_TRIGGER** / **IRQ_TRIGGER_FAILED**
- **INIT_START** / **INIT_COMPLETE**
- **RESET_START** / **RESET_COMPLETE**
- **SHUTDOWN_START** / **SHUTDOWN_COMPLETE**

### IRQ Events (`IRQ_EVENT`)
- Interrupt events (Purple)

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
Run with the default demo trace file:
```bash
python app.py
```

### Custom Trace File
Run with a specific trace file:
```bash
python app.py path/to/your/trace_file.json
```

### Web Interface
After starting the application, open your web browser and navigate to:
```
http://127.0.0.1:8050
```

## Trace File Format

The tool expects JSON files with the following structure:

```json
{
  "trace_info": {
    "total_events": 13,
    "saved_at": "2025-08-04T11:25:30.770201",
    "trace_manager": "GlobalTraceManager"
  },
  "events": [
    {
      "timestamp": 1754306730.7695093,
      "formatted_time": "2025-08-04 11:25:30.769",
      "module_name": "MainRAM",
      "event_type": "DEVICE_EVENT",
      "event_data": {
        "device_name": "MainRAM",
        "operation": "WRITE",
        "address": "0x20000000",
        "value": "0xDEADBEEF",
        "width": 4
      }
    }
  ]
}
```

## Interactive Features

- **Zoom**: Use mouse wheel or zoom controls to zoom in/out on the timeline
- **Pan**: Click and drag to move around the timeline
- **Reset**: Double-click to reset zoom level
- **Hover**: Hover over any data point to see detailed event information
- **Legend**: Toggle event types in the legend to show/hide specific event categories

## Sample Data

The repository includes `unified_trace_demo.json` as a sample trace file for testing and demonstration purposes.

## Dependencies

- `dash`: Web application framework
- `plotly`: Interactive plotting library  
- `pandas`: Data manipulation and analysis
