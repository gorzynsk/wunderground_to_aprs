"""
Command Line Argument Parser for Weather to APRS Sender

Handles all command line argument parsing and validation
for the Weather to APRS Sender application.
"""

import sys
import argparse
import re


class ArgumentParser:
    """Handle command line argument parsing for Weather to APRS Sender."""
    
    def __init__(self):
        """Initialize the argument parser."""
        self.parser = self._create_parser()
    
    def _create_parser(self):
        """Create and configure the argument parser."""
        parser = argparse.ArgumentParser(
            description='Download weather data and send to APRS-IS network',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Default: run with no arguments (uses saved configuration)
  python wunderground_to_aprs_sender.py
  
  # Run continuously every 15 minutes (default)
  python wunderground_to_aprs_sender.py --schedule
  
  # Run continuously with custom interval
  python wunderground_to_aprs_sender.py --schedule --interval 30
  
  # Traditional single transmission
  python wunderground_to_aprs_sender.py YOUR_STATION_ID YOUR_CALLSIGN YOUR_PASSCODE
  python wunderground_to_aprs_sender.py KLAX N6ABC 23456 --server euro.aprs2.net
  
  # Multiple stations (each station_id paired with its callsign)
  python wunderground_to_aprs_sender.py KLAX,KJFK N6ABC,K2DEF 23456
  
  # Save configuration for future use
  python wunderground_to_aprs_sender.py --save-config YOUR_STATION_ID YOUR_CALLSIGN YOUR_PASSCODE --api-key YOUR_KEY
  
  # Save multiple stations configuration
  python wunderground_to_aprs_sender.py --save-config KLAX,KJFK N6ABC,K2DEF 23456
  
  # Save configuration with scheduling enabled
  python wunderground_to_aprs_sender.py --save-config YOUR_STATION_ID YOUR_CALLSIGN YOUR_PASSCODE --schedule --interval 30
  
  # Scheduled mode using saved configuration
  python wunderground_to_aprs_sender.py --schedule --interval 20
  
  # Show current configuration
  python wunderground_to_aprs_sender.py --show-config
            """
        )
        
        # Configuration management arguments
        config_group = parser.add_argument_group('Configuration Management')
        config_group.add_argument('--save-config', action='store_true', 
                                help='Save current settings to configuration file')
        config_group.add_argument('--use-config', action='store_true',
                                help='Use saved configuration (this is the default when no arguments provided)')
        config_group.add_argument('--show-config', action='store_true',
                                help='Show current saved configuration')
        config_group.add_argument('--delete-config', action='store_true',
                                help='Delete saved configuration file')
        
        # Station and authentication arguments (optional when using config)
        parser.add_argument('station_id', nargs='?', help='Weather station ID(s) (e.g., YOUR_STATION_ID or STATION1,STATION2)')
        parser.add_argument('callsign', nargs='?', help='Your amateur radio callsign(s) (e.g., YOUR_CALL or CALL1,CALL2)')
        parser.add_argument('passcode', nargs='?', type=int, help='APRS-IS passcode for transmitting')
        
        # Named optional arguments
        parser.add_argument('--station', help='Weather station ID(s) (alternative to positional argument, supports comma-separated list)')
        parser.add_argument('--server', help='APRS-IS server hostname (auto-select if not specified)')
        parser.add_argument('--api-key', help='Weather Underground API key (uses sample data if not provided)')
        
        # Scheduling arguments
        schedule_group = parser.add_argument_group('Scheduling Options')
        schedule_group.add_argument('--schedule', action='store_true',
                                   help='Run continuously, sending weather data at regular intervals')
        schedule_group.add_argument('--interval', type=int, default=15, metavar='MINUTES',
                                   help='Interval between transmissions in minutes (default: 15)')
        
        return parser
    
    def parse_args(self, argv=None):
        """Parse command line arguments and return parsed args."""
        args = self.parser.parse_args(argv)
        
        # If no arguments provided at all, default to --use-config
        if len(sys.argv) == 1:
            args.use_config = True
        
        return args
    
    def validate_callsign(self, callsign):
        """Validate amateur radio callsign format."""
        if not callsign:
            return False
        pattern = r'^[A-Z0-9]{3,6}(-[0-9]{1,2})?$'
        return bool(re.match(pattern, callsign.upper()))
    
    def validate_interval(self, interval):
        """Validate transmission interval."""
        if interval < 1:
            return False, "Interval must be at least 1 minute"
        
        if interval < 5:
            return True, "Very short intervals may violate APRS-IS guidelines. Recommended minimum: 5 minutes"
        
        return True, None
    
    def print_help(self):
        """Print help message."""
        self.parser.print_help()
    
    def print_usage(self):
        """Print usage message."""
        self.parser.print_usage()
