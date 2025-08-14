"""
Weather to APRS Core Functions

Core functionality for downloading weather data and sending to APRS-IS.
"""

from .wunderground_downloader import WundergroundDownloader
from .aprs_frame_generator import APRSFrameGenerator
from .aprs_client import APRSISClient


def send_weather_to_aprs(station_id, callsign, passcode, server=None, api_key=None):
    """
    Complete workflow: Download weather data and send to APRS-IS.
    
    Args:
        station_id (str): Weather station ID (e.g., 'YOUR_STATION_ID')
        callsign (str): Amateur radio callsign
        passcode (int): APRS-IS passcode
        server (str): APRS-IS server (None for auto-select)
        api_key (str): Weather Underground API key (None for sample data)
        
    Returns:
        bool: True if successful
    """
    print("🌤️  Weather to APRS Sender")
    print("=" * 50)
    print(f"Station ID: {station_id}")
    print(f"Callsign: {callsign}")
    print(f"APRS-IS Server: {server or 'auto-select'}")
    print()
    
    # Step 1: Download weather data
    print("📡 Step 1: Downloading weather data...")
    try:
        downloader = WundergroundDownloader(api_key)
        weather_data = downloader.get_current_conditions(station_id)
        
        if not weather_data:
            print("❌ Failed to download weather data")
            return False
            
        print("✅ Weather data downloaded successfully")
        
        # Show coordinate info
        if 'observations' in weather_data and weather_data['observations']:
            obs = weather_data['observations'][0]
            lat = obs.get('lat', 0.0)
            lon = obs.get('lon', 0.0)
            if weather_data.get('status') == 'mock_data':
                print(f"📍 Coordinates: {lat:.4f}, {lon:.4f} (sample data)")
            else:
                print(f"📍 Coordinates: {lat:.6f}, {lon:.6f} (from Weather Underground)")
        
    except Exception as e:
        print(f"❌ Error downloading weather data: {e}")
        return False
    
    # Step 2: Generate APRS frame
    print("\n📻 Step 2: Generating APRS frame...")
    try:
        aprs_frame = APRSFrameGenerator.create_aprs_frame(weather_data, callsign)
        
        if aprs_frame.startswith("Error"):
            print(f"❌ {aprs_frame}")
            return False
            
        print("✅ APRS frame generated successfully")
        print(f"📻 Frame: {aprs_frame}")
        
    except Exception as e:
        print(f"❌ Error generating APRS frame: {e}")
        return False
    
    # Step 3: Send to APRS-IS
    print("\n🌐 Step 3: Sending to APRS-IS network...")
    try:
        # Initialize APRS-IS client
        client = APRSISClient(callsign, passcode, server)
        
        # Connect to APRS-IS
        if not client.connect():
            print("❌ Failed to connect to APRS-IS")
            return False
        
        # Send frame
        success = client.send_frame(aprs_frame)
        
        # Disconnect
        client.disconnect()
        
        if success:
            print("✅ Weather data successfully transmitted to APRS-IS!")
            print("📡 Your weather station data is now live on the APRS network")
            print("🌐 View at: https://aprs.fi")
            return True
        else:
            print("❌ Failed to send frame to APRS-IS")
            return False
            
    except Exception as e:
        print(f"❌ Error sending to APRS-IS: {e}")
        return False
