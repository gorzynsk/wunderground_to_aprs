# Weather Underground to APRS Sender - Source Modules

This directory contains the modular components of the Weather to APRS Sender application.

## Module Overview

### 📊 Core Modules

- **`config_manager.py`** - Configuration file management
  - Handles saving/loading user preferences (station ID, callsign, API keys, scheduling)
  - JSON-based configuration storage in user home directory
  - Low-level configuration operations

- **`config_handler.py`** - Configuration workflow management
  - High-level configuration operations and user interaction
  - Interactive configuration setup and validation
  - Handles save/load/use configuration workflows

- **`argument_parser.py`** - Command line argument parsing
  - Defines all command line arguments and options
  - Validates user input (callsigns, intervals)
  - Clean separation of argument parsing logic

- **`wunderground_downloader.py`** - Weather Underground API client
  - Downloads current weather conditions from Weather Underground
  - Fallback to mock data when API key is not available
  - Proper error handling and SSL handling

- **`aprs_frame_generator.py`** - APRS protocol frame generation
  - Converts weather data to proper APRS weather frames
  - Coordinate conversion (decimal degrees to APRS format)
  - APRS protocol compliance

- **`aprs_client.py`** - APRS-IS network client
  - Connects to APRS-IS servers with authentication
  - Server failover capability
  - Proper APRS-IS login protocol

- **`scheduler.py`** - Automatic scheduling system
  - Handles scheduled weather transmissions
  - Immediate transmission on startup + regular intervals
  - Graceful shutdown handling with signal handlers

- **`core.py`** - Main workflow orchestration
  - Combines all modules for complete weather-to-APRS workflow
  - Error handling and status reporting
  - Single function entry point for weather transmission

### 📦 Package Structure

```
src/
├── __init__.py              # Package initialization and exports
├── argument_parser.py       # Command line argument parsing
├── config_manager.py        # Low-level configuration management
├── config_handler.py        # High-level configuration workflows
├── wunderground_downloader.py    # Weather Underground API
├── aprs_frame_generator.py  # APRS frame generation
├── aprs_client.py           # APRS-IS network client
├── scheduler.py             # Scheduled transmission handling
└── core.py                  # Main workflow function
```

### 🔗 Dependencies

- **External**: `requests` (for HTTP API calls)
- **Standard Library**: `socket`, `json`, `datetime`, `threading`, `signal`, `re`, `os`

### 💡 Usage in Main Script

```python
from src import (
    ConfigManager, ScheduledWeatherSender, send_weather_to_aprs,
    ArgumentParser, ConfigHandler
)

# Argument parsing
arg_parser = ArgumentParser()
args = arg_parser.parse_args()

# Configuration management
config_manager = ConfigManager()
config_handler = ConfigHandler(config_manager)

# Configuration operations
config_handler.handle_save_config(args)
config_data = config_handler.handle_use_config(args)

# Single transmission
success = send_weather_to_aprs(station_id, callsign, passcode, server, api_key)

# Scheduled transmission
scheduler = ScheduledWeatherSender(
    station_id, callsign, passcode, server, api_key, 
    interval_minutes=15, send_function=send_weather_to_aprs
)
scheduler.start()
```

### 🧪 Testing

Each module can be imported and tested independently:

```python
from src.wunderground_downloader import WundergroundDownloader
from src.aprs_frame_generator import APRSFrameGenerator
from src.config_manager import ConfigManager

# Test weather download
downloader = WundergroundDownloader(api_key="your_key")
data = downloader.get_current_conditions("YOUR_STATION_ID")

# Test APRS frame generation
frame = APRSFrameGenerator.create_aprs_frame(data, "SQ2WB")

# Test configuration
config = ConfigManager()
config.show_config()
```

### 🎯 Benefits of Modular Design

1. **Maintainability**: Each component has a single responsibility
2. **Testability**: Individual modules can be tested in isolation
3. **Reusability**: Components can be used in other projects
4. **Readability**: Clear separation of concerns
5. **Extensibility**: Easy to add new features or modify existing ones
