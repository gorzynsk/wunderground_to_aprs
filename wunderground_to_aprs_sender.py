#!/usr/bin/env python3
"""
Weather to APRS Sender

A complete all-in-one solution for downloading weather data from Weather Underground
and transmitting it to the APRS-IS network.

Features:
- Downloads weather data from Weather Underground for any station ID
- Generates proper APRS weather frames with real coordinates
- Sends frames to APRS-IS servers with authentication
- Simple command-line interface
- Configuration file support for saving credentials
- Scheduled automatic transmissions (default: every 15 minutes)
- Self-contained (no external module dependencies except requests)

Usage:
    # Default: just run the script (uses saved configuration)
    python wunderground_to_aprs_sender.py
    
    # Scheduled mode: send weather data every 15 minutes
    python wunderground_to_aprs_sender.py --schedule
    
    # Custom interval: send every 30 minutes
    python wunderground_to_aprs_sender.py --schedule --interval 30
    
    # First time setup - save your configuration
    python wunderground_to_aprs_sender.py --save-config YOUR_STATION_ID YOUR_CALLSIGN YOUR_PASSCODE --api-key YOUR_KEY
    
    # Traditional command line usage (single station)
    python wunderground_to_aprs_sender.py STATION_ID CALLSIGN PASSCODE
    
    # Multiple stations with paired callsigns
    python wunderground_to_aprs_sender.py STATION1,STATION2 CALL1,CALL2 PASSCODE
    
Examples:
    # Run with no arguments (easiest - uses saved config)
    python wunderground_to_aprs_sender.py
    
    # Run continuously every 15 minutes (automatic weather station)
    python wunderground_to_aprs_sender.py --schedule
    
    # Run continuously with custom 30-minute interval
    python wunderground_to_aprs_sender.py --schedule --interval 30
    
    # Save configuration interactively (includes scheduling options)
    python wunderground_to_aprs_sender.py --save-config
    
    # Save configuration with scheduling enabled
    python wunderground_to_aprs_sender.py --save-config YOUR_STATION_ID YOUR_CALLSIGN YOUR_PASSCODE --schedule --interval 20
    
    # Show current configuration
    python wunderground_to_aprs_sender.py --show-config
    
    # Traditional usage (no config file) - single station
    python wunderground_to_aprs_sender.py YOUR_STATION_ID YOUR_CALLSIGN YOUR_PASSCODE
    python wunderground_to_aprs_sender.py KLAX N6ABC 23456 --server euro.aprs2.net
    
    # Multiple stations with paired callsigns
    python wunderground_to_aprs_sender.py KLAX,KJFK N6ABC,K2DEF 23456
    
Requirements:
- Python 3.7+
- requests library (pip install requests)
- Valid amateur radio license and callsign
- APRS-IS passcode for transmitting
- Internet connection for Weather Underground and APRS-IS
"""

import sys
import os

# Import our modular components
from src import (
    ConfigManager, ScheduledWeatherSender, send_weather_to_aprs,
    ArgumentParser, ConfigHandler
)


def main():
    """Main function - orchestrates the entire application."""
    
    # Initialize components
    arg_parser = ArgumentParser()
    config_manager = ConfigManager()
    config_handler = ConfigHandler(config_manager)
    
    # Parse command line arguments
    args = arg_parser.parse_args()
    
    # If no arguments provided, show helpful message
    if args.use_config and len(sys.argv) == 1:
        print("🔧 No arguments provided - using saved configuration")
        print("   (Use --help to see all options)")
        print()
    
    # Handle configuration management commands
    if args.show_config:
        config_handler.handle_show_config()
        return
    
    if args.delete_config:
        config_handler.handle_delete_config()
        return
    
    if args.save_config:
        config_handler.handle_save_config(args)
        return
    
    # Determine configuration source and load settings
    if args.use_config:
        config_data = config_handler.handle_use_config(args)
    else:
        config_data = config_handler.handle_traditional_mode(args)
    
    if not config_data:
        arg_parser.print_help()
        sys.exit(1)
    
    # Extract configuration
    stations = config_data['stations']
    api_key = config_data['api_key']
    server = config_data['server']
    
    # Get API key from environment if not provided
    if not api_key:
        api_key = os.getenv('WUNDERGROUND_API_KEY')
    
    if not api_key:
        print("⚠️  No Weather Underground API key provided")
        print("   Using sample data. For real weather data:")
        print("   1. Get API key from Weather Underground")
        print("   2. Use --api-key parameter or set WUNDERGROUND_API_KEY environment variable")
        print("   3. Save API key in config with --save-config")
        print()
    
    # Validate callsign formats
    for station in stations:
        if not arg_parser.validate_callsign(station['callsign']):
            print(f"❌ Error: Invalid callsign format: {station['callsign']}")
            print("   Example valid callsigns: YOUR_CALL, N6ABC, VK2DEF-1")
            sys.exit(1)
    
    # Handle scheduling mode
    if args.schedule:
        # Validate interval
        is_valid, warning = arg_parser.validate_interval(args.interval)
        if not is_valid:
            print(f"❌ Error: {warning}")
            sys.exit(1)
        
        if warning:
            print(f"⚠️  Warning: {warning}")
            response = input("Continue anyway? (y/N): ").strip().lower()
            if response != 'y':
                print("Operation cancelled")
                sys.exit(0)
        
        # Start scheduled mode
        try:
            scheduler = ScheduledWeatherSender(
                stations=stations,
                server=server,
                api_key=api_key,
                interval_minutes=args.interval,
                send_function=send_weather_to_aprs
            )
            scheduler.start()
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Scheduler error: {e}")
            sys.exit(1)
    else:
        # Execute single transmission
        try:
            success = send_weather_to_aprs(
                stations=stations,
                server=server,
                api_key=api_key
            )
            
            if success:
                print("\n🎉 Mission accomplished!")
                sys.exit(0)
            else:
                print("\n💥 Mission failed!")
                sys.exit(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
