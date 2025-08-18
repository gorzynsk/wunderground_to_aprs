"""
Configuration Manager for Weather to APRS Sender

Manages configuration file for storing user preferences including
station settings, credentials, and scheduling options.
"""

import os
import json


class ConfigManager:
    """Manage configuration file for storing user preferences."""
    
    def __init__(self, config_file=None):
        """Initialize configuration manager."""
        if config_file:
            self.config_file = config_file
        else:
            # Use user's home directory for config file
            home_dir = os.path.expanduser("~")
            self.config_file = os.path.join(home_dir, ".weather_to_aprs_config.json")
    
    def load_config(self):
        """Load configuration from file."""
        if not os.path.exists(self.config_file):
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            return config
        except Exception as e:
            print(f"⚠️  Warning: Could not load config file: {e}")
            return {}
    
    def save_config(self, config):
        """Save configuration to file."""
        try:
            # Create directory if it doesn't exist
            config_dir = os.path.dirname(self.config_file)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"✅ Configuration saved to: {self.config_file}")
            return True
        except Exception as e:
            print(f"❌ Error saving config file: {e}")
            return False
    
    def update_config(self, stations=None, api_key=None, server=None, schedule=None, interval=None, station_id=None, callsign=None, passcode=None):
        """Update configuration with new values.
        
        Args:
            stations: List of dicts with 'station_id', 'callsign', 'passcode' keys
            api_key: Weather Underground API key
            server: APRS-IS server
            schedule: Enable/disable scheduling
            interval: Transmission interval in minutes
            station_id: Single station ID (backward compatibility)
            callsign: Single callsign (backward compatibility)
            passcode: Single passcode (backward compatibility)
        """
        config = self.load_config()
        
        # Handle new multi-station format
        if stations is not None:
            config['stations'] = stations
            # Remove old single station format for clarity
            config.pop('station_id', None)
            config.pop('callsign', None) 
            config.pop('passcode', None)
        
        # Handle backward compatibility - single station format
        elif all(param is not None for param in [station_id, callsign, passcode]):
            config['stations'] = [{
                'station_id': station_id,
                'callsign': callsign,
                'passcode': passcode
            }]
            # Remove old format
            config.pop('station_id', None)
            config.pop('callsign', None)
            config.pop('passcode', None)
        
        # Handle partial backward compatibility updates
        elif any(param is not None for param in [station_id, callsign, passcode]):
            # If we have existing old format, update it
            if 'station_id' in config or 'callsign' in config or 'passcode' in config:
                if station_id is not None:
                    config['station_id'] = station_id
                if callsign is not None:
                    config['callsign'] = callsign
                if passcode is not None:
                    config['passcode'] = passcode
            # If we have new format, update first station
            elif 'stations' in config and config['stations']:
                if station_id is not None:
                    config['stations'][0]['station_id'] = station_id
                if callsign is not None:
                    config['stations'][0]['callsign'] = callsign
                if passcode is not None:
                    config['stations'][0]['passcode'] = passcode
        
        # Update other settings
        if api_key is not None:
            config['api_key'] = api_key
        if server is not None:
            config['server'] = server
        if schedule is not None:
            config['schedule'] = schedule
        if interval is not None:
            config['interval'] = interval
        
        return self.save_config(config)
    
    def get_config_value(self, key, default=None):
        """Get a specific configuration value."""
        config = self.load_config()
        return config.get(key, default)
    
    def show_config(self):
        """Display current configuration."""
        config = self.load_config()
        
        if not config:
            print("📝 No configuration file found")
            print(f"   Config file location: {self.config_file}")
            return
        
        print("📝 Current Configuration:")
        print(f"   Config file: {self.config_file}")
        
        # Show stations (support both old and new format)
        stations = config.get('stations', [])
        
        # Backward compatibility: convert old format
        if not stations and config.get('station_id'):
            stations = [{
                'station_id': config.get('station_id'),
                'callsign': config.get('callsign'),
                'passcode': config.get('passcode')
            }]
        
        if stations:
            if len(stations) == 1:
                station = stations[0]
                print(f"   Station ID: {station.get('station_id', 'Not set')}")
                print(f"   Callsign: {station.get('callsign', 'Not set')}")
                print(f"   Passcode: {'***' if station.get('passcode') else 'Not set'}")
            else:
                print(f"   Stations ({len(stations)}):")
                for i, station in enumerate(stations, 1):
                    print(f"     {i}. {station.get('station_id', 'Not set')} -> {station.get('callsign', 'Not set')} (passcode: {'***' if station.get('passcode') else 'Not set'})")
        else:
            print("   Stations: Not configured")
        
        print(f"   API Key: {'***' if config.get('api_key') else 'Not set'}")
        print(f"   Server: {config.get('server', 'Auto-select')}")
        print(f"   Schedule Mode: {'Enabled' if config.get('schedule') else 'Disabled'}")
        print(f"   Interval: {config.get('interval', 15)} minutes")
    
    def delete_config(self):
        """Delete configuration file."""
        try:
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
                print(f"✅ Configuration file deleted: {self.config_file}")
                return True
            else:
                print("📝 No configuration file to delete")
                return True
        except Exception as e:
            print(f"❌ Error deleting config file: {e}")
            return False
