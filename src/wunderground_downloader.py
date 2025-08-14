"""
Weather Underground Data Downloader

Downloads current weather conditions from Weather Underground API
with fallback to mock data for testing without API key.
"""

import requests
from datetime import datetime


class WundergroundDownloader:
    """Weather Underground data downloader."""
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://api.weather.com/v1"
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'WundergroundDownloader/1.0'})
        self.session.verify = False  # Handle SSL issues in development
    
    def get_current_conditions(self, station_id):
        """Get current weather conditions for a station."""
        try:
            if self.api_key:
                # Try Weather Underground PWS endpoint with API key
                url = f"https://api.weather.com/v2/pws/observations/current"
                params = {
                    'stationId': station_id,
                    'format': 'json',
                    'units': 'm',  # metric units
                    'apiKey': self.api_key
                }
                
                response = self.session.get(url, params=params)
                response.raise_for_status()
                return response.json()
            else:
                # Return mock data structure
                return self._get_mock_data(station_id)
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching current conditions: {e}")
            return None
    
    def _get_mock_data(self, station_id):
        """Create mock weather data for testing without API key."""
        current_time = datetime.now().isoformat()
        
        return {
            'observations': [{
                'stationID': station_id,
                'obsTimeUtc': current_time,
                'obsTimeLocal': current_time,
                'neighborhood': f"Sample Station {station_id}",
                'softwareType': "WU Sample Data",
                'country': "Unknown",
                'lat': 0.0,
                'lon': 0.0,
                'elevation': 100.0,
                'humidity': 65,
                'winddir': 270,
                'metric': {
                    'temp': 20.5,
                    'heatIndex': 20.5,
                    'dewpt': 14.2,
                    'windChill': 20.5,
                    'windSpeed': 9.7,
                    'windGust': 12.9,
                    'pressure': 1013.25,
                    'precipRate': 0.0,
                    'precipTotal': 0.0,
                    'elev': 100.0
                },
                'imperial': {
                    'temp': 68.9,
                    'heatIndex': 68.9,
                    'dewpt': 57.6,
                    'windChill': 68.9,
                    'windSpeed': 6.0,
                    'windGust': 8.0,
                    'pressure': 29.92,
                    'precipRate': 0.0,
                    'precipTotal': 0.0,
                    'elev': 328.1
                }
            }],
            'status': 'mock_data',
            'message': 'API key required for real data with coordinates',
            'note': 'This mimics the real Weather Underground API structure. Real data includes accurate lat/lon coordinates.',
        }
