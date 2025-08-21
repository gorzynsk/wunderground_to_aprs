# Weather Underground to APRS Sender

🌤️ **A complete all-in-one solution for downloading weather data from Weather Underground and transmitting it to the APRS-IS network.**

## 📖 Overview

This script combines weather data collection from Weather Underground with APRS (Automatic Packet Reporting System) transmission capabilities, allowing amateur radio operators to send weather station data to the global APRS network with a single command.

## ✨ Features

- **🎯 One Command Solution**: Download weather data and transmit to APRS-IS in one step
- **💾 Configuration Storage**: Save your station ID, callsign, passcode, and API key for easy reuse
- **⏰ Scheduled Transmissions**: Automatic weather station mode with configurable intervals (default: 15 minutes)
- **📍 Real Coordinates**: Uses actual latitude/longitude from Weather Underground API
- **🌐 Global APRS Network**: Transmits to APRS-IS servers worldwide with automatic failover
- **🔒 Secure Authentication**: Uses official APRS-IS passcodes for secure transmission
- **🛡️ Error Handling**: Robust handling of missing data and null values
- **🎨 Simple Interface**: User-friendly command-line interface with helpful error messages

## 🚀 Quick Start

### First Time Setup (Recommended)
```bash
# Save your configuration interactively
python wunderground_to_aprs_sender.py --save-config

# Or save configuration with command line arguments
python wunderground_to_aprs_sender.py --save-config STATION_ID CALLSIGN PASSCODE --api-key YOUR_API_KEY
```

### Daily Usage (After Setup)
```bash
# Just run the script with no arguments (single transmission)
python wunderground_to_aprs_sender.py

# Run as automatic weather station (every 15 minutes)
python wunderground_to_aprs_sender.py --schedule

# Run with custom interval (every 30 minutes)
python wunderground_to_aprs_sender.py --schedule --interval 30
```

### Traditional Usage (No Configuration File)
```bash
python wunderground_to_aprs_sender.py STATION_ID CALLSIGN PASSCODE
```

### Examples
```bash
# Save configuration from Czech station IXXXXX1
python wunderground_to_aprs_sender.py --save-config IXXXXX1 YOUR_CALLSIGN YOUR_PASSCODE --api-key YOUR_API_KEY

# Single transmission using no arguments (uses saved configuration automatically!)
python wunderground_to_aprs_sender.py

# Automatic weather station mode (every 15 minutes)
python wunderground_to_aprs_sender.py --schedule

# Custom interval automatic mode (every 20 minutes)
python wunderground_to_aprs_sender.py --schedule --interval 20

# Traditional one-time usage
python wunderground_to_aprs_sender.py KLAX N6ABC 23456 --server noam.aprs2.net

# Show your current saved configuration
python wunderground_to_aprs_sender.py --show-config
```

## 📋 Requirements

- **Python 3.7+**
- **Valid amateur radio license and callsign**
- **Internet connection**
- **APRS-IS passcode** (for transmitting)
- **Weather Underground API key** (optional, but recommended for real data)

## 🔧 Installation

1. **Clone or download** the script
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up your configuration** (recommended):
   ```bash
   python wunderground_to_aprs_sender.py --save-config
   ```
4. **Run the script**:
   ```bash
   python wunderground_to_aprs_sender.py
   ```

## 🎯 Why Use Configuration Files?

**Before (traditional method):**
```bash
python wunderground_to_aprs_sender.py IXXXXX1 YOUR_CALLSIGN YOUR_PASSCODE --api-key 8298c13da23c45ea98c13da23cc5ea53 --server euro.aprs2.net
```

**After (with configuration):**
```bash
# Single transmission
python wunderground_to_aprs_sender.py

# Automatic weather station
python wunderground_to_aprs_sender.py --schedule
```

**Benefits:**
- ✅ **Security**: No passwords visible in command history
- ✅ **Convenience**: One simple command every time
- ✅ **Automation**: Perfect for cron jobs and scheduled tasks
- ✅ **Sharing**: Easy to run the same setup on multiple computers
- ✅ **Default**: No arguments needed - just run the script!
- ✅ **Scheduling**: Automatic weather station mode with --schedule

## 📡 Command Line Options

### Configuration Management
- `--save-config`: Save current settings to configuration file
- `--use-config`: Use saved configuration (this is the default when no arguments provided)
- `--show-config`: Show current saved configuration
- `--delete-config`: Delete saved configuration file

### Scheduling Options
- `--schedule`: Run continuously, sending weather data at regular intervals
- `--interval MINUTES`: Interval between transmissions in minutes (default: 15)

### Required Arguments (when not using config)
- `station_id`: Weather station ID (e.g., IXXXXX1, KLAX, KDFW)
- `callsign`: Your amateur radio callsign
- `passcode`: APRS-IS passcode for transmitting

### Optional Arguments
- `--station STATION`: Weather station ID (alternative to positional argument)
- `--server SERVER`: Specific APRS-IS server hostname
- `--api-key API_KEY`: Weather Underground API key

## ⏰ Automatic Weather Station Mode

Turn your computer into an automatic APRS weather station that sends data at regular intervals:

### Basic Scheduling
```bash
# Run every 15 minutes (default)
python wunderground_to_aprs_sender.py --schedule

# Run every 30 minutes
python wunderground_to_aprs_sender.py --schedule --interval 30

# Run every hour
python wunderground_to_aprs_sender.py --schedule --interval 60
```

### Recommended Intervals
- **15 minutes**: Standard for active weather monitoring
- **30 minutes**: Good balance for regular updates
- **60 minutes**: Minimal impact, good for stable conditions
- **5 minutes**: Minimum recommended (shorter intervals may violate APRS-IS guidelines)

### Running as a Service

#### Linux Service (Systemd)
**For automatic startup after reboot and robust service management:**

1. **Quick Setup**:
   ```bash
   # Run the installer
   sudo ./install-service.sh
   
   # Configure the service
   sudo -u aprs /opt/wunderground-to-aprs/venv/bin/python /opt/wunderground-to-aprs/wunderground_to_aprs_sender.py --save-config
   
   # Start the service
   sudo systemctl start wunderground-to-aprs
   ```

2. **Service Management**:
   ```bash
   # Check status
   sudo systemctl status wunderground-to-aprs
   
   # View logs
   sudo journalctl -u wunderground-to-aprs -f
   
   # Restart service
   sudo systemctl restart wunderground-to-aprs
   ```

**Features of the Linux service:**
- ✅ **Auto-start on boot** - Starts automatically after system reboot
- ✅ **Auto-restart on failure** - Restarts if the process crashes
- ✅ **Secure execution** - Runs as dedicated non-root user
- ✅ **System integration** - Full systemd integration with logging
- ✅ **Easy management** - Standard systemctl commands

See [SERVICE_SETUP.md](SERVICE_SETUP.md) for detailed installation instructions.

#### Mac/Linux (Alternative - Cron)
Use cron for simpler scheduling without service features:
```bash
# Edit crontab
crontab -e

# Add line for every 15 minutes
*/15 * * * * cd /path/to/script && python3 wunderground_to_aprs_sender.py
```

## 🏗️ Project Structure

The project is organized into modular components for better maintainability:

```
wunderground-to-aprs/
├── wunderground_to_aprs_sender.py    # Main script (entry point)
├── requirements.txt             # Python dependencies
├── README.md                   # This documentation
└── src/                        # Source code modules
    ├── __init__.py             # Package initialization
    ├── config_manager.py       # Configuration file management
    ├── config_handler.py       # High-level configuration workflows
    ├── argument_parser.py      # Command line argument parsing
    ├── wunderground_downloader.py   # Weather Underground API client
    ├── aprs_frame_generator.py # APRS protocol frame formatting
    ├── aprs_client.py          # APRS-IS network client
    ├── scheduler.py            # Automatic scheduling system
    └── core.py                 # Main workflow orchestration
```

### Modular Design Benefits
- **🔧 Maintainable**: Each component has a single responsibility
- **🧪 Testable**: Individual modules can be tested separately
- **🔄 Reusable**: Components can be imported by other projects
- **📚 Readable**: Clean separation of concerns

## 💾 Configuration File

The script can save your credentials to avoid typing them every time:

### Location
- **Windows**: `C:\Users\USERNAME\.weather_to_aprs_config.json`
- **Linux/Mac**: `~/.weather_to_aprs_config.json`

### Stored Information
- Weather station ID
- Amateur radio callsign
- APRS-IS passcode (encrypted storage)
- Weather Underground API key
- Preferred APRS-IS server
- **Scheduling settings** (enable/disable automatic mode, transmission interval)

### Usage Examples
```bash
# Interactive setup (prompts for missing information)
python wunderground_to_aprs_sender.py --save-config

# Command line setup
python wunderground_to_aprs_sender.py --save-config IXXXXX1 YOUR_CALLSIGN YOUR_PASSCODE --api-key YOUR_KEY

# Save configuration with automatic scheduling enabled (every 30 minutes)
python wunderground_to_aprs_sender.py --save-config IXXXXX1 YOUR_CALLSIGN YOUR_PASSCODE --schedule --interval 30

# View saved configuration
python wunderground_to_aprs_sender.py --show-config

# Run with saved configuration (default behavior)
python wunderground_to_aprs_sender.py

# Automatic weather station mode (uses scheduling settings from config if saved)
python wunderground_to_aprs_sender.py --schedule

# Custom interval automatic mode (overrides saved config)
python wunderground_to_aprs_sender.py --schedule --interval 30

# Override saved settings temporarily
python wunderground_to_aprs_sender.py --station KLAX --server euro.aprs2.net

# Scheduled mode with overrides
python wunderground_to_aprs_sender.py --schedule --station KLAX --interval 20

# Delete configuration
python wunderground_to_aprs_sender.py --delete-config
```

## ⏰ Scheduling Configuration

When you save your configuration, you can also choose to enable automatic scheduling:

```bash
# During interactive setup, you'll be prompted:
python wunderground_to_aprs_sender.py --save-config
# Enable automatic scheduling? (y/N): y
# Enter transmission interval in minutes (default: 15): 30

# Or save directly with scheduling enabled:
python wunderground_to_aprs_sender.py --save-config --station IXXXXX1 --schedule --interval 20
```

### Behavior with Saved Scheduling Settings
- **Default mode**: If scheduling is enabled in config, running with no arguments will use saved settings
- **Override**: Command line `--schedule` and `--interval` options override saved settings  
- **Persistent**: Scheduling preferences are remembered between sessions

### Show Current Scheduling Configuration
```bash
python wunderground_to_aprs_sender.py --show-config
# Will display:
# Schedule Mode: Enabled/Disabled
# Interval: X minutes
```

## 🌍 Weather Station IDs

### Examples of Valid Station IDs
- **IXXXXX1** - Czech Republic personal weather station
- **KLAX** - Los Angeles International Airport
- **KDFW** - Dallas/Fort Worth International Airport
- **KORD** - Chicago O'Hare International Airport

## 🌐 APRS-IS Servers

The script automatically selects from these servers with failover:
- `rotate.aprs2.net` - Primary server pool
- `noam.aprs2.net` - North America
- `euro.aprs2.net` - Europe  
- `asia.aprs2.net` - Asia
- `aunz.aprs2.net` - Australia/New Zealand
- `soam.aprs2.net` - South America

## 🔑 Weather Underground API Key

### Getting an API Key
1. Visit [Weather Underground API](https://www.wunderground.com/weather/api)
2. Sign up for a free account
3. Create an API key
4. Use with `--api-key` parameter or set `WUNDERGROUND_API_KEY` environment variable

### Without API Key
The script works without an API key using sample data, but coordinates will be 0,0. For real coordinates and weather data, an API key is required.

## 🎯 APRS-IS Passcode

### For Transmitting
You need an official APRS-IS passcode tied to your amateur radio license. Calculate it using online tools or ham radio software. This passcode is required for transmitting to the APRS-IS network.

## 📊 What Gets Transmitted

The script sends a complete APRS weather frame including:

- **Position**: Real coordinates from Weather Underground (lat/lon)
- **Weather Data**: Temperature, humidity, pressure, wind speed/direction
- **Timestamp**: Current UTC time
- **Identification**: Your callsign and "WX" weather identifier

### Example APRS Frame
```
YOUR_CALLSIGN>APRS,TCPIP*:@141049z52xx.99N/018xx.45E_316/004g007t066r000p000P10176h60b10176 WX
```

**Frame Breakdown:**
- `YOUR_CALLSIGN` - Your callsign
- `52xx.xxN/018xx.xxE` - Position (52.xxx°N, 18.xxx°E)
- `316/004g007` - Wind: 316° at 4mph, gusts 7mph
- `t066` - Temperature: 66°F
- `P10176h60` - Pressure: 1017.6mb, Humidity: 60%
- `WX` - Weather station identifier

## 🌍 Viewing Your Data

After transmission, your weather data appears on:
- **[aprs.fi](https://aprs.fi)** - Search for your callsign
- **[aprsdirect.com](https://aprsdirect.com)** - APRS tracking
- **Local APRS applications** and digipeaters

## 🛠️ Troubleshooting

### Connection Issues
- Check internet connection
- Try different APRS-IS server with `--server`
- Verify callsign format (e.g., YOUR_CALLSIGN, N6ABC-1)

### Authentication Issues  
- Verify your APRS-IS passcode is correct
- Check callsign spelling and format

### Weather Data Issues
- Get Weather Underground API key for real data
- Verify station ID exists (check wunderground.com)
- Some stations may have incomplete data (null values are handled automatically)

### Common Error Messages
- `"Error: Passcode required"` - Provide your official APRS-IS passcode
- `"Invalid callsign format"` - Use proper amateur radio callsign format
- `"Failed to download weather data"` - Check station ID and internet connection

## 📝 Technical Details

### Data Flow
1. **Download**: Fetches weather data from Weather Underground API
2. **Convert**: Extracts coordinates and weather parameters  
3. **Generate**: Creates APRS-formatted weather frame
4. **Transmit**: Sends frame to APRS-IS network via TCP socket

### Coordinate Handling
- Real coordinates from Weather Underground API when available
- Automatic conversion from decimal degrees to APRS format
- Graceful handling of null/missing coordinate data

### APRS Frame Format
Standard APRS weather format with position, timestamp, and weather data according to APRS specification.

## 📄 License

This project is for amateur radio use only. Users must have a valid amateur radio license before transmitting to APRS-IS networks.

## 🤝 Contributing

This is a community project for amateur radio operators. Feel free to:
- Report issues and bugs
- Suggest improvements
- Submit pull requests
- Share usage examples

## 📞 Support

For support:
1. Check this README for common solutions
2. Verify your amateur radio license and APRS-IS passcode
3. Check [APRS.org](http://www.aprs.org) for APRS protocol information

---

**73!** (Amateur radio greeting meaning "best wishes")

*Created for the amateur radio community*
