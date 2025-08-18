"""
Configuration Handler for Weather to APRS Sender

Handles configuration-related operations including saving, loading,
and interactive configuration setup.
"""

import sys
import os
import re


class ConfigHandler:
    """Handle configuration operations for Weather to APRS Sender."""
    
    def __init__(self, config_manager):
        """Initialize with a ConfigManager instance."""
        self.config_manager = config_manager
    
    def handle_show_config(self):
        """Handle showing current configuration."""
        self.config_manager.show_config()
    
    def handle_delete_config(self):
        """Handle deleting configuration."""
        return self.config_manager.delete_config()
    
    def handle_save_config(self, args):
        """Handle saving configuration interactively or from arguments."""
        # Check if we have command line arguments for single station
        station_id = args.station_id or args.station
        callsign = args.callsign
        passcode = args.passcode
        api_key = args.api_key
        server = args.server
        schedule = args.schedule
        interval = args.interval if args.interval != 15 else None  # Only save if not default
        
        stations = []
        
        if station_id and callsign and passcode:
            # Handle command line arguments - support multiple stations
            if ',' in station_id and ',' in callsign:
                station_ids = [s.strip() for s in station_id.split(',') if s.strip()]
                callsigns = [c.strip().upper() for c in callsign.split(',') if c.strip()]
                
                if len(station_ids) != len(callsigns):
                    print("❌ Error: Number of station IDs must match number of callsigns")
                    print("   Example: STATION1,STATION2 CALL1,CALL2 PASSCODE")
                    return False
                
                # For multiple stations, use the same passcode for all
                for sid, call in zip(station_ids, callsigns):
                    stations.append({
                        'station_id': sid.upper(),
                        'callsign': call,
                        'passcode': passcode
                    })
            else:
                # Single station from command line
                stations.append({
                    'station_id': station_id.upper(),
                    'callsign': callsign.upper(),
                    'passcode': passcode
                })
        else:
            # Interactive configuration
            print("📝 Setting up configuration...")
            print("\nYou can configure:")
            print("  1. Single station: Enter one station ID and callsign")
            print("  2. Multiple stations: Enter comma-separated lists")
            print("     Example: STATION1,STATION2 and CALL1,CALL2")
            
            while True:
                station_input = input("\nEnter weather station ID(s): ").strip().upper()
                if not station_input:
                    print("❌ Station ID is required")
                    continue
                
                callsign_input = input("Enter callsign(s): ").strip().upper()
                if not callsign_input:
                    print("❌ Callsign is required")
                    continue
                
                # Parse station IDs and callsigns
                station_ids = [s.strip() for s in station_input.split(',') if s.strip()]
                callsigns = [c.strip() for c in callsign_input.split(',') if c.strip()]
                
                if len(station_ids) != len(callsigns):
                    print(f"❌ Error: Number of station IDs ({len(station_ids)}) must match number of callsigns ({len(callsigns)})")
                    continue
                
                # Validate callsigns
                invalid_callsigns = []
                for call in callsigns:
                    if not re.match(r'^[A-Z0-9]{3,6}(-[0-9]{1,2})?$', call):
                        invalid_callsigns.append(call)
                
                if invalid_callsigns:
                    print(f"❌ Error: Invalid callsign format(s): {', '.join(invalid_callsigns)}")
                    continue
                
                # Get passcode (same for all stations for simplicity)
                if len(station_ids) == 1:
                    passcode_prompt = f"Enter APRS-IS passcode for {callsigns[0]}: "
                else:
                    passcode_prompt = f"Enter APRS-IS passcode (will be used for all {len(callsigns)} callsigns): "
                
                try:
                    passcode = int(input(passcode_prompt).strip())
                except ValueError:
                    print("❌ Error: Invalid passcode format")
                    continue
                
                # Create station configurations
                for sid, call in zip(station_ids, callsigns):
                    stations.append({
                        'station_id': sid,
                        'callsign': call,
                        'passcode': passcode
                    })
                
                # Show summary
                print(f"\n✅ Configured {len(stations)} station(s):")
                for i, station in enumerate(stations, 1):
                    print(f"   {i}. {station['station_id']} -> {station['callsign']}")
                
                break
            
            # Get other settings
            if not api_key:
                api_key = input("\nEnter Weather Underground API key (optional, press Enter to skip): ").strip()
                if not api_key:
                    api_key = None
            
            # Ask about scheduling preferences
            schedule_choice = input("Enable automatic scheduling? (y/N): ").strip().lower()
            if schedule_choice == 'y':
                schedule = True
                try:
                    interval_input = input("Enter transmission interval in minutes (default: 15): ").strip()
                    interval = int(interval_input) if interval_input else 15
                except ValueError:
                    print("⚠️  Invalid interval, using default 15 minutes")
                    interval = 15
            else:
                schedule = False
                interval = None
        
        # Validate all callsigns
        for station in stations:
            if not re.match(r'^[A-Z0-9]{3,6}(-[0-9]{1,2})?$', station['callsign']):
                print(f"❌ Error: Invalid callsign format: {station['callsign']}")
                return False
        
        # Save configuration
        if self.config_manager.update_config(stations=stations, api_key=api_key, server=server, schedule=schedule, interval=interval):
            print("🎉 Configuration saved successfully!")
            print(f"   Configured {len(stations)} station(s)")
            if schedule:
                print(f"   Automatic scheduling enabled (every {interval or 15} minutes)")
            print("   You can now run: python wunderground_to_aprs_sender.py")
            return True
        
        return False
    
    def handle_use_config(self, args):
        """Handle loading and using saved configuration."""
        config = self.config_manager.load_config()
        
        if not config:
            print("❌ No configuration file found!")
            print("   Create one with: python wunderground_to_aprs_sender.py --save-config")
            return None
        
        # Load stations from config (support both old and new format)
        stations = config.get('stations', [])
        
        # Backward compatibility: convert old format
        if not stations and config.get('station_id'):
            stations = [{
                'station_id': config.get('station_id'),
                'callsign': config.get('callsign'),
                'passcode': config.get('passcode')
            }]
        
        api_key = config.get('api_key')
        server = config.get('server')
        
        # Load scheduling options from config if not overridden by command line
        if not args.schedule and config.get('schedule'):
            args.schedule = True
            print("🕐 Scheduling enabled from configuration")
        
        if args.interval == 15 and config.get('interval'):  # Use config interval if default not overridden
            args.interval = config.get('interval')
        
        # Override with command line arguments if provided
        if args.station_id or args.station:
            station_input = args.station_id or args.station
            callsign_input = args.callsign
            passcode_input = args.passcode
            
            if ',' in station_input:
                # Multiple stations from command line
                station_ids = [s.strip().upper() for s in station_input.split(',') if s.strip()]
                if callsign_input and ',' in callsign_input:
                    callsigns = [c.strip().upper() for c in callsign_input.split(',') if c.strip()]
                    if len(station_ids) == len(callsigns):
                        stations = []
                        for sid, call in zip(station_ids, callsigns):
                            stations.append({
                                'station_id': sid,
                                'callsign': call,
                                'passcode': passcode_input or (stations[0]['passcode'] if stations else None)
                            })
                    else:
                        print("❌ Error: Number of station IDs must match number of callsigns")
                        return None
                else:
                    print("❌ Error: Multiple station IDs require multiple callsigns")
                    return None
            else:
                # Single station override
                stations = [{
                    'station_id': station_input.upper(),
                    'callsign': callsign_input.upper() if callsign_input else stations[0]['callsign'] if stations else None,
                    'passcode': passcode_input if passcode_input else stations[0]['passcode'] if stations else None
                }]
        
        if args.api_key:
            api_key = args.api_key
        if args.server:
            server = args.server
        
        # Validate that we have all required data
        if not stations:
            print("❌ No stations configured!")
            print("   Please run --save-config to configure stations.")
            return None
        
        for station in stations:
            if not all([station.get('station_id'), station.get('callsign'), station.get('passcode')]):
                print("❌ Incomplete station configuration!")
                print("   Missing values in configuration file. Please run --save-config again.")
                return None
        
        return {
            'stations': stations,
            'api_key': api_key,
            'server': server
        }
    
    def handle_traditional_mode(self, args):
        """Handle traditional command line mode with fallback to config."""
        # Check if we have all required arguments
        station_id = args.station_id or args.station
        callsign = args.callsign
        passcode = args.passcode
        
        # Load defaults from config if available
        config = self.config_manager.load_config()
        stations = []
        
        if config:
            # Try to load from new format first
            config_stations = config.get('stations', [])
            
            # Backward compatibility: convert old format
            if not config_stations and config.get('station_id'):
                config_stations = [{
                    'station_id': config.get('station_id'),
                    'callsign': config.get('callsign'),
                    'passcode': config.get('passcode')
                }]
            
            # Use config defaults if command line args not provided
            if not station_id and config_stations:
                stations = config_stations
            if not args.api_key:
                args.api_key = config.get('api_key')
            if not args.server:
                args.server = config.get('server')
            
            # Load scheduling defaults from config if not specified on command line
            if not args.schedule and config.get('schedule'):
                args.schedule = True
                print("🕐 Scheduling enabled from configuration")
            
            if args.interval == 15 and config.get('interval'):
                args.interval = config.get('interval')
        
        # Handle command line arguments
        if station_id and callsign and passcode:
            if ',' in station_id and ',' in callsign:
                # Multiple stations from command line
                station_ids = [s.strip().upper() for s in station_id.split(',') if s.strip()]
                callsigns = [c.strip().upper() for c in callsign.split(',') if c.strip()]
                
                if len(station_ids) != len(callsigns):
                    print("❌ Error: Number of station IDs must match number of callsigns")
                    return None
                
                stations = []
                for sid, call in zip(station_ids, callsigns):
                    stations.append({
                        'station_id': sid,
                        'callsign': call,
                        'passcode': passcode
                    })
            else:
                # Single station from command line
                stations = [{
                    'station_id': station_id.upper(),
                    'callsign': callsign.upper(),
                    'passcode': passcode
                }]
        
        if not stations:
            print("❌ Error: Missing required arguments")
            print("   Either provide: STATION_ID(S) CALLSIGN(S) PASSCODE")
            print("   For multiple stations: STATION1,STATION2 CALL1,CALL2 PASSCODE")
            print("   Or save config with: --save-config")
            print("   Or use saved config with: --use-config")
            return None
        
        return {
            'stations': stations,
            'api_key': args.api_key,
            'server': args.server
        }
