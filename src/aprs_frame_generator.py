"""
APRS Frame Generator

Generates proper APRS weather frames from Weather Underground data
following the APRS protocol specifications.
"""

from datetime import datetime, timezone


class APRSFrameGenerator:
    """Generate APRS weather frames from weather data."""
    
    @staticmethod
    def convert_coordinates(lat, lon):
        """Convert decimal degrees to APRS format."""
        # Latitude
        lat_abs = abs(lat)
        lat_deg = int(lat_abs)
        lat_min = (lat_abs - lat_deg) * 60
        lat_hem = 'N' if lat >= 0 else 'S'
        lat_str = f"{lat_deg:02d}{lat_min:05.2f}{lat_hem}"
        
        # Longitude  
        lon_abs = abs(lon)
        lon_deg = int(lon_abs)
        lon_min = (lon_abs - lon_deg) * 60
        lon_hem = 'E' if lon >= 0 else 'W'
        lon_str = f"{lon_deg:03d}{lon_min:05.2f}{lon_hem}"
        
        return f"{lat_str}/{lon_str}"
    
    @staticmethod
    def create_aprs_frame(weather_data, callsign="N0CALL"):
        """Create APRS frame from weather data."""
        
        # Extract data from Weather Underground API format
        if 'observations' in weather_data and weather_data['observations']:
            obs = weather_data['observations'][0]
            station_id = obs.get('stationID', 'UNKNOWN')
            lat = obs.get('lat', 0.0) or 0.0
            lon = obs.get('lon', 0.0) or 0.0
            humidity = obs.get('humidity') or 0
            wind_dir = obs.get('winddir') or 0
            timestamp = obs.get('obsTimeUtc', '')
            
            if 'metric' in obs:
                metric = obs['metric']
                temp_c = metric.get('temp') or 0
                pressure_mb = metric.get('pressure') or 1013.25
                wind_speed_kmh = metric.get('windSpeed') or 0
                wind_gust_kmh = metric.get('windGust') or 0
            else:
                temp_c = pressure_mb = wind_speed_kmh = wind_gust_kmh = 0
        else:
            return "Error: No observation data found in weather data"
        
        # Convert values
        coordinates = APRSFrameGenerator.convert_coordinates(lat, lon)
        temp_f = int((temp_c * 9/5) + 32)
        wind_mph = int(wind_speed_kmh * 0.621371)
        gust_mph = int(wind_gust_kmh * 0.621371)
        pressure_tenths = int(pressure_mb * 10)
        
        # Format timestamp
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                dt = datetime.now(timezone.utc)
        else:
            dt = datetime.now(timezone.utc)
        
        timestamp_aprs = dt.strftime("%d%H%Mz")
        
        # Create APRS frame
        header = f"{callsign.upper()}>APRS,TCPIP*:"
        weather = (f"@{timestamp_aprs}{coordinates}_{wind_dir:03d}/{wind_mph:03d}"
                  f"g{gust_mph:03d}t{temp_f:03d}r000p000P{pressure_tenths:04d}"
                  f"h{humidity:02d}b{pressure_tenths:04d} WX")
        
        return header + weather
