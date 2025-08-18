"""
Scheduled Weather Sender

Handles automatic scheduled transmission of weather data to APRS-IS
with configurable intervals and graceful shutdown handling.
"""

import time
import signal
import threading
from datetime import datetime


class ScheduledWeatherSender:
    """Handle scheduled sending of weather data to APRS-IS."""
    
    def __init__(self, stations, server=None, api_key=None, interval_minutes=15, send_function=None):
        """Initialize scheduled weather sender.
        
        Args:
            stations: List of station dicts with 'station_id', 'callsign', 'passcode' keys
            server: APRS-IS server (None for auto-select)
            api_key: Weather Underground API key
            interval_minutes: Transmission interval in minutes
            send_function: Function to call for sending weather data
        """
        # Handle backward compatibility - single station format
        if isinstance(stations, dict):
            stations = [stations]
        elif not isinstance(stations, list):
            # Legacy format: single station parameters
            stations = [{
                'station_id': stations,
                'callsign': server,  # In old format, these were different parameters
                'passcode': api_key
            }]
        
        self.stations = stations
        self.server = server
        self.api_key = api_key
        self.interval_seconds = interval_minutes * 60
        self.running = False
        self.thread = None
        self.next_send_time = None
        self.send_function = send_function  # Function to call for sending weather data
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print(f"\n🛑 Received shutdown signal ({signum})")
        self.stop()
    
    def start(self):
        """Start the scheduled weather sending."""
        if self.running:
            print("⚠️  Scheduler is already running")
            return
        
        self.running = True
        print(f"🕐 Starting scheduled weather transmission every {self.interval_seconds // 60} minutes")
        print(f"📡 Stations ({len(self.stations)}):")
        for i, station in enumerate(self.stations, 1):
            print(f"   {i}. {station['station_id']} -> {station['callsign']}")
        print(f"🌐 Server: {self.server or 'auto-select'}")
        print("   Press Ctrl+C to stop")
        print("=" * 50)
        
        # Start the scheduler thread
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the scheduled weather sending."""
        if not self.running:
            return
        
        print("\n🛑 Stopping scheduled weather transmission...")
        self.running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        
        print("✅ Scheduler stopped successfully")
    
    def _run_scheduler(self):
        """Run the scheduler loop."""
        first_transmission = True
        
        while self.running:
            if first_transmission:
                # Send immediately on startup
                print("📡 Sending initial transmission...")
                self._send_weather_data(is_scheduled=False)
                first_transmission = False
                
                if not self.running:  # Exit if stopped during first transmission
                    break
                
                print("-" * 50)
            
            # Calculate next send time
            current_time = datetime.now()
            self.next_send_time = current_time.replace(second=0, microsecond=0)
            
            # Round to next interval
            minutes_past_hour = self.next_send_time.minute
            interval_minutes = self.interval_seconds // 60
            next_interval = ((minutes_past_hour // interval_minutes) + 1) * interval_minutes
            
            if next_interval >= 60:
                # Move to next hour, handling midnight rollover
                next_hour = (self.next_send_time.hour + 1) % 24
                if next_hour == 0:  # Midnight rollover
                    from datetime import timedelta
                    self.next_send_time = self.next_send_time.replace(hour=0, minute=0) + timedelta(days=1)
                else:
                    self.next_send_time = self.next_send_time.replace(hour=next_hour, minute=0)
            else:
                self.next_send_time = self.next_send_time.replace(minute=next_interval)
            
            # Wait until next send time
            wait_seconds = (self.next_send_time - current_time).total_seconds()
            
            print(f"⏰ Next transmission at: {self.next_send_time.strftime('%H:%M:%S')} (in {wait_seconds/60:.1f} minutes)")
            
            # Wait with periodic checks for shutdown
            start_wait = time.time()
            while self.running and (time.time() - start_wait) < wait_seconds:
                time.sleep(1)
            
            # Send weather data if still running
            if self.running:
                self._send_weather_data(is_scheduled=True)
    
    def _send_weather_data(self, is_scheduled=True):
        """Send weather data once."""
        try:
            if is_scheduled:
                print(f"\n📡 Scheduled transmission at {datetime.now().strftime('%H:%M:%S')}")
                print("-" * 30)
            
            # Call the provided send function with all stations
            if self.send_function:
                success = self.send_function(
                    stations=self.stations,
                    server=self.server,
                    api_key=self.api_key
                )
            else:
                print("❌ No send function provided to scheduler")
                success = False
            
            if success:
                if is_scheduled:
                    print("✅ Scheduled transmission completed successfully")
                else:
                    print("✅ Initial transmission completed successfully")
            else:
                if is_scheduled:
                    print("❌ Scheduled transmission failed")
                else:
                    print("❌ Initial transmission failed")
                
        except Exception as e:
            print(f"❌ Error in transmission: {e}")
        
        finally:
            if is_scheduled:
                print("-" * 50)
