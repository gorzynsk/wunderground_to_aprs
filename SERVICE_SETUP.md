# Running as a Linux Service

This document explains how to set up the Weather Underground to APRS script as a Linux systemd service that starts automatically after reboot.

## Quick Start

1. **Copy files to your Linux server**
2. **Run the installation script**:
   ```bash
   sudo ./install-service.sh
   ```
3. **Configure the service**:
   ```bash
   sudo -u aprs /opt/wunderground-to-aprs/venv/bin/python /opt/wunderground-to-aprs/wunderground_to_aprs_sender.py --save-config
   ```
4. **Start the service**:
   ```bash
   sudo systemctl start wunderground-to-aprs
   ```

## Detailed Installation Guide

### Prerequisites

- Linux system with systemd (Ubuntu 16.04+, CentOS 7+, Debian 8+, etc.)
- Root access (sudo privileges)
- Internet connection
- Valid amateur radio license and APRS passcode

### Installation Steps

1. **Transfer files to Linux server**:
   ```bash
   # Copy the entire project directory to your Linux server
   scp -r wunderground_to_aprs/ user@your-server:/home/user/
   ```

2. **Navigate to the project directory**:
   ```bash
   cd wunderground_to_aprs/
   ```

3. **Make installation script executable**:
   ```bash
   chmod +x install-service.sh
   ```

4. **Run the installation script**:
   ```bash
   sudo ./install-service.sh
   ```

   The installer will:
   - Create a dedicated `aprs` user and group
   - Install Python dependencies
   - Copy files to `/opt/wunderground-to-aprs/`
   - Create a Python virtual environment
   - Install the systemd service
   - Configure auto-start on boot

### Configuration

After installation, configure the service before starting it:

```bash
sudo -u aprs /opt/wunderground-to-aprs/venv/bin/python /opt/wunderground-to-aprs/wunderground_to_aprs_sender.py --save-config
```

You'll be prompted for:
- **Station ID(s)**: Weather Underground station IDs (e.g., `KCASANFR123`)
- **Callsign(s)**: Your amateur radio callsign (e.g., `N6ABC`)
- **APRS Passcode**: Your APRS-IS passcode
- **API Key**: Weather Underground API key (optional)
- **Transmission Interval**: How often to send data (default: 15 minutes)
- **Scheduling**: Whether to enable automatic scheduled transmissions

### Service Management

#### Start the service:
```bash
sudo systemctl start wunderground-to-aprs
```

#### Enable auto-start on boot (done automatically by installer):
```bash
sudo systemctl enable wunderground-to-aprs
```

#### Check service status:
```bash
sudo systemctl status wunderground-to-aprs
```

#### View service logs:
```bash
# View recent logs
sudo journalctl -u wunderground-to-aprs

# Follow logs in real-time
sudo journalctl -u wunderground-to-aprs -f

# View logs from today
sudo journalctl -u wunderground-to-aprs --since today
```

#### Stop the service:
```bash
sudo systemctl stop wunderground-to-aprs
```

#### Restart the service:
```bash
sudo systemctl restart wunderground-to-aprs
```

#### Disable auto-start:
```bash
sudo systemctl disable wunderground-to-aprs
```

### Service Configuration Details

The service is configured with the following characteristics:

- **User**: Runs as dedicated `aprs` user (not root)
- **Working Directory**: `/opt/wunderground-to-aprs/`
- **Auto-restart**: Automatically restarts if it crashes
- **Start Delay**: 30-second delay between restart attempts
- **Security**: Enhanced security with restricted filesystem access
- **Logging**: All output goes to systemd journal
- **Network**: Waits for network connectivity before starting

### Configuration File Location

The service stores its configuration in:
```
/opt/wunderground-to-aprs/.config.json
```

You can manually edit this file or use the `--save-config` option to reconfigure.

### Updating the Service

To update the application:

1. **Stop the service**:
   ```bash
   sudo systemctl stop wunderground-to-aprs
   ```

2. **Backup current configuration** (optional):
   ```bash
   sudo cp /opt/wunderground-to-aprs/.config.json ~/config-backup.json
   ```

3. **Update application files**:
   ```bash
   sudo cp -r src/ /opt/wunderground-to-aprs/
   sudo cp wunderground_to_aprs_sender.py /opt/wunderground-to-aprs/
   sudo cp requirements.txt /opt/wunderground-to-aprs/
   ```

4. **Update Python dependencies**:
   ```bash
   sudo -u aprs /opt/wunderground-to-aprs/venv/bin/pip install -r /opt/wunderground-to-aprs/requirements.txt --upgrade
   ```

5. **Set proper ownership**:
   ```bash
   sudo chown -R aprs:aprs /opt/wunderground-to-aprs/
   ```

6. **Start the service**:
   ```bash
   sudo systemctl start wunderground-to-aprs
   ```

### Troubleshooting

#### Service won't start:
```bash
# Check detailed status
sudo systemctl status wunderground-to-aprs -l

# Check logs for errors
sudo journalctl -u wunderground-to-aprs --no-pager
```

#### Configuration issues:
```bash
# Test configuration manually
sudo -u aprs /opt/wunderground-to-aprs/venv/bin/python /opt/wunderground-to-aprs/wunderground_to_aprs_sender.py --show-config

# Reconfigure if needed
sudo -u aprs /opt/wunderground-to-aprs/venv/bin/python /opt/wunderground-to-aprs/wunderground_to_aprs_sender.py --save-config
```

#### Python environment issues:
```bash
# Recreate virtual environment
sudo rm -rf /opt/wunderground-to-aprs/venv/
sudo -u aprs python3 -m venv /opt/wunderground-to-aprs/venv
sudo -u aprs /opt/wunderground-to-aprs/venv/bin/pip install -r /opt/wunderground-to-aprs/requirements.txt
```

#### Network connectivity issues:
The service automatically waits for network connectivity. If you have issues:
```bash
# Check network status
systemctl status network-online.target

# Restart networking (Ubuntu/Debian)
sudo systemctl restart networking

# Restart NetworkManager (CentOS/RHEL)
sudo systemctl restart NetworkManager
```

### Uninstallation

To completely remove the service:

1. **Make uninstaller executable**:
   ```bash
   chmod +x uninstall-service.sh
   ```

2. **Run the uninstaller**:
   ```bash
   sudo ./uninstall-service.sh
   ```

This will:
- Stop and disable the service
- Remove all service files
- Delete the application directory
- Remove the `aprs` user and group

### Security Considerations

The service is configured with several security features:

- **Non-root execution**: Runs as dedicated `aprs` user
- **Filesystem restrictions**: Limited filesystem access
- **No new privileges**: Cannot escalate privileges
- **Private temp**: Uses private temporary directories
- **Protected system**: System directories are read-only

### Performance and Resource Usage

The service is designed to be lightweight:

- **Memory usage**: Typically 20-50 MB
- **CPU usage**: Minimal (only active during transmissions)
- **Network usage**: Very low (small APRS packets every 15+ minutes)
- **Storage**: Configuration and logs only

### Monitoring and Alerts

To monitor the service health:

```bash
# Create a simple monitoring script
cat > /usr/local/bin/check-aprs-service.sh << 'EOF'
#!/bin/bash
if ! systemctl is-active --quiet wunderground-to-aprs; then
    echo "APRS service is not running!"
    # Add notification logic here (email, SMS, etc.)
fi
EOF

chmod +x /usr/local/bin/check-aprs-service.sh

# Add to cron for regular checks
echo "*/5 * * * * /usr/local/bin/check-aprs-service.sh" | sudo crontab -
```

### Log Rotation

Systemd automatically manages log rotation, but you can configure it:

```bash
# Create custom log rotation config
sudo tee /etc/systemd/journald.conf.d/wunderground-to-aprs.conf << 'EOF'
[Journal]
SystemMaxUse=100M
MaxRetentionSec=30day
EOF

# Restart journald
sudo systemctl restart systemd-journald
```
