"""
Weather to APRS Core Functions

Core functionality for downloading weather data and sending to APRS-IS.
"""

from .wunderground_downloader import WundergroundDownloader
from .aprs_frame_generator import APRSFrameGenerator
from .aprs_client import APRSISClient


def send_weather_to_aprs(stations, server=None, api_key=None):
    """
    Complete workflow: Download weather data from multiple stations and send to APRS-IS.
    
    Args:
        stations (list): List of station dicts with 'station_id', 'callsign', 'passcode' keys
        server (str): APRS-IS server (None for auto-select)
        api_key (str): Weather Underground API key (None for sample data)
        
    Returns:
        bool: True if all transmissions successful
    """
    # Handle backward compatibility - single station format
    if isinstance(stations, dict):
        stations = [stations]
    
    print("🌤️  Weather to APRS Sender")
    print("=" * 50)
    print(f"Stations ({len(stations)}):")
    for i, station in enumerate(stations, 1):
        print(f"  {i}. {station['station_id']} -> {station['callsign']}")
    print(f"APRS-IS Server: {server or 'auto-select'}")
    print()
    
    # Initialize components
    downloader = WundergroundDownloader(api_key)
    overall_success = True
    
    # Process each station
    for i, station in enumerate(stations, 1):
        print(f"\n📡 Processing station {i}/{len(stations)}: {station['station_id']} -> {station['callsign']}")
        print("-" * 50)
        
        success = _process_single_station(
            station['station_id'], 
            station['callsign'], 
            station['passcode'],
            downloader, 
            server, 
            api_key
        )
        
        if not success:
            overall_success = False
            print(f"❌ Failed to process station {station['station_id']}")
        else:
            print(f"✅ Successfully processed station {station['station_id']}")
    
    print("\n" + "=" * 50)
    
    if overall_success:
        print("🎉 All stations processed successfully!")
        print("📡 Weather data transmitted to APRS-IS network")
        print("🌐 View at: https://aprs.fi")
    else:
        print("⚠️  Some stations failed to process")
        print("📡 Partial data transmitted to APRS-IS network")
    
    return overall_success


def _process_single_station(station_id, callsign, passcode, downloader, server, api_key):
    """
    Process a single weather station.
    
    Args:
        station_id (str): Weather station ID
        callsign (str): Amateur radio callsign
        passcode (int): APRS-IS passcode
        downloader: WundergroundDownloader instance
        server (str): APRS-IS server
        api_key (str): API key for weather data
        
    Returns:
        bool: True if successful
    """
    client = None
    
    try:
        # Step 1: Download weather data
        print(f"📡 Step 1: Downloading weather data for {station_id}...")
        weather_data = downloader.get_current_conditions(station_id)
        
        if not weather_data:
            print(f"❌ Failed to download weather data for {station_id}")
            return False
            
        print(f"✅ Weather data downloaded for {station_id}")
        
        # Show coordinate info
        if 'observations' in weather_data and weather_data['observations']:
            obs = weather_data['observations'][0]
            lat = obs.get('lat', 0.0)
            lon = obs.get('lon', 0.0)
            if weather_data.get('status') == 'mock_data':
                print(f"📍 Coordinates: {lat:.4f}, {lon:.4f} (sample data)")
            else:
                print(f"📍 Coordinates: {lat:.6f}, {lon:.6f} (from Weather Underground)")
        
        # Step 2: Generate APRS frame
        print(f"📻 Step 2: Generating APRS frame for {callsign}...")
        aprs_frame = APRSFrameGenerator.create_aprs_frame(weather_data, callsign)
        
        if aprs_frame.startswith("Error"):
            print(f"❌ {aprs_frame}")
            return False
            
        print(f"✅ APRS frame generated for {callsign}")
        print(f"📻 Frame: {aprs_frame}")
        
        # Step 3: Send to APRS-IS
        print(f"🌐 Step 3: Transmitting {callsign} data to APRS-IS...")
        client = APRSISClient(callsign, passcode, server)
        
        if not client.connect():
            print(f"❌ Failed to connect to APRS-IS for {callsign}")
            return False
        
        success = client.send_frame(aprs_frame)
        
        if success:
            print(f"✅ {callsign} data transmitted successfully")
            return True
        else:
            print(f"❌ Failed to transmit {callsign} data")
            return False
            
    except Exception as e:
        print(f"❌ Error processing station {station_id} -> {callsign}: {e}")
        return False
    
    finally:
        if client:
            client.disconnect()


# Backward compatibility wrapper
def send_weather_to_aprs_single(station_id, callsign, passcode, server=None, api_key=None):
    """Backward compatibility wrapper for single station."""
    station = {
        'station_id': station_id,
        'callsign': callsign,
        'passcode': passcode
    }
    return send_weather_to_aprs([station], server, api_key)
