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
        # Use provided values or ask for them
        station_id = args.station_id or args.station
        callsign = args.callsign
        passcode = args.passcode
        api_key = args.api_key
        server = args.server
        schedule = args.schedule
        interval = args.interval if args.interval != 15 else None  # Only save if not default
        
        if not all([station_id, callsign, passcode]):
            print("📝 Setting up configuration...")
            
            if not station_id:
                station_id = input("Enter weather station ID (e.g., YOUR_STATION_ID): ").strip().upper()
            if not callsign:
                callsign = input("Enter your amateur radio callsign: ").strip().upper()
            if not passcode:
                try:
                    passcode = int(input("Enter your APRS-IS passcode: ").strip())
                except ValueError:
                    print("❌ Error: Invalid passcode format")
                    return False
            
            if not api_key:
                api_key = input("Enter Weather Underground API key (optional, press Enter to skip): ").strip()
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
        
        # Validate callsign
        if not re.match(r'^[A-Z0-9]{3,6}(-[0-9]{1,2})?$', callsign):
            print(f"❌ Error: Invalid callsign format: {callsign}")
            return False
        
        # Save configuration
        if self.config_manager.update_config(station_id, callsign, passcode, api_key, server, schedule, interval):
            print("🎉 Configuration saved successfully!")
            if schedule:
                print(f"   Automatic scheduling enabled (every {interval or 15} minutes)")
                print("   You can now run: python wunderground_to_aprs_sender.py")
            else:
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
        
        # Load values from config
        station_id = config.get('station_id')
        callsign = config.get('callsign')
        passcode = config.get('passcode')
        api_key = config.get('api_key')
        server = config.get('server')
        
        # Load scheduling options from config if not overridden by command line
        if not args.schedule and config.get('schedule'):
            args.schedule = True
            print("🕐 Scheduling enabled from configuration")
        
        if args.interval == 15 and config.get('interval'):  # Use config interval if default not overridden
            args.interval = config.get('interval')
        
        # Override with command line arguments if provided
        if args.station_id:
            station_id = args.station_id
        if args.station:
            station_id = args.station
        if args.callsign:
            callsign = args.callsign
        if args.passcode:
            passcode = args.passcode
        if args.api_key:
            api_key = args.api_key
        if args.server:
            server = args.server
        
        if not all([station_id, callsign, passcode]):
            print("❌ Incomplete configuration!")
            print("   Missing values in configuration file. Please run --save-config again.")
            return None
        
        return {
            'station_id': station_id,
            'callsign': callsign,
            'passcode': passcode,
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
        if config and not station_id:
            station_id = config.get('station_id')
        if config and not callsign:
            callsign = config.get('callsign')
        if config and not passcode:
            passcode = config.get('passcode')
        if config and not args.api_key:
            args.api_key = config.get('api_key')
        if config and not args.server:
            args.server = config.get('server')
        
        # Load scheduling defaults from config if not specified on command line
        if config and not args.schedule and config.get('schedule'):
            args.schedule = True
            print("🕐 Scheduling enabled from configuration")
        
        if config and args.interval == 15 and config.get('interval'):
            args.interval = config.get('interval')
        
        if not all([station_id, callsign, passcode]):
            print("❌ Error: Missing required arguments")
            print("   Either provide: STATION_ID CALLSIGN PASSCODE")
            print("   Or save config with: --save-config")
            print("   Or use saved config with: --use-config")
            return None
        
        return {
            'station_id': station_id,
            'callsign': callsign,
            'passcode': passcode,
            'api_key': args.api_key,
            'server': args.server
        }
