"""
APRS-IS Client

Handles connection and transmission to APRS-IS servers
with authentication and server failover capabilities.
"""

import socket
import re


class APRSISClient:
    """APRS-IS client for sending weather data to the APRS network."""
    
    # Common APRS-IS servers
    APRS_SERVERS = [
        ("rotate.aprs2.net", 14580),      # Primary server pool
        ("noam.aprs2.net", 14580),        # North America
        ("euro.aprs2.net", 14580),        # Europe
        ("asia.aprs2.net", 14580),        # Asia
        ("aunz.aprs2.net", 14580),        # Australia/New Zealand
        ("soam.aprs2.net", 14580),        # South America
    ]
    
    def __init__(self, callsign, passcode, server=None, port=14580):
        """Initialize APRS-IS client."""
        self.callsign = callsign.upper()
        self.passcode = passcode
        self.server = server
        self.port = port
        self.socket = None
        self.connected = False
        self.login_successful = False
        
        # Validate callsign format
        if not self._validate_callsign(callsign):
            raise ValueError(f"Invalid callsign format: {callsign}")
    
    def _validate_callsign(self, callsign):
        """Validate amateur radio callsign format."""
        pattern = r'^[A-Z0-9]{3,6}(-[0-9]{1,2})?$'
        return bool(re.match(pattern, callsign.upper()))
    
    def connect(self, timeout=30):
        """Connect to APRS-IS server."""
        if self.server:
            servers_to_try = [(self.server, self.port)]
        else:
            servers_to_try = self.APRS_SERVERS
        
        for server_host, server_port in servers_to_try:
            try:
                print(f"🔌 Connecting to {server_host}:{server_port}...")
                
                # Create socket
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(timeout)
                
                # Connect
                self.socket.connect((server_host, server_port))
                self.connected = True
                
                print(f"✅ Connected to {server_host}:{server_port}")
                
                # Login
                if self._login():
                    self.server = server_host
                    self.port = server_port
                    return True
                else:
                    self.disconnect()
                    
            except Exception as e:
                print(f"❌ Failed to connect to {server_host}:{server_port}: {e}")
                if self.socket:
                    try:
                        self.socket.close()
                    except:
                        pass
                    self.socket = None
                self.connected = False
                continue
        
        print("❌ Failed to connect to any APRS-IS server")
        return False
    
    def _login(self):
        """Login to APRS-IS server."""
        try:
            # First, read the server banner
            banner = self.socket.recv(1024).decode('ascii')
            print(f"📡 Server banner: {banner.strip()}")
            
            # Send login string (proper APRS-IS format)
            login_string = f"user {self.callsign} pass {self.passcode} vers PythonAPRS 1.0\r\n"
            self.socket.send(login_string.encode('ascii'))
            
            # Read login response
            response = self.socket.recv(1024).decode('ascii')
            print(f"📡 Login response: {response.strip()}")
            
            if "verified" in response.lower():
                print(f"✅ Login successful - transmit enabled")
                self.login_successful = True
                return True
            elif "unverified" in response.lower():
                print(f"⚠️  Login successful - read-only mode")
                print(f"   Use your official APRS-IS passcode for transmit capability")
                self.login_successful = False
                return True
            else:
                print(f"❌ Login failed: {response.strip()}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def send_frame(self, aprs_frame):
        """Send APRS frame to the network."""
        if not self.connected or not self.socket:
            print("❌ Not connected to APRS-IS server")
            return False
        
        try:
            # Ensure frame ends with CRLF
            if not aprs_frame.endswith('\r\n'):
                aprs_frame += '\r\n'
            
            # Send frame
            self.socket.send(aprs_frame.encode('ascii'))
            
            if self.login_successful:
                print(f"📡 Frame transmitted: {aprs_frame.strip()}")
            else:
                print(f"🔒 Frame would be transmitted (read-only mode): {aprs_frame.strip()}")
                print(f"   Get your official APRS-IS passcode to enable transmission")
            
            return True
            
        except Exception as e:
            print(f"❌ Error sending frame: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from APRS-IS server."""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        self.connected = False
        self.login_successful = False
        print("🔌 Disconnected from APRS-IS server")
