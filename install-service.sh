#!/bin/bash

# Weather Underground to APRS Service Installation Script
# This script installs the wunderground-to-aprs service on a Linux system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVICE_NAME="wunderground-to-aprs"
SERVICE_USER="aprs"
SERVICE_GROUP="aprs"
INSTALL_DIR="/opt/wunderground-to-aprs"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# Functions
print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE} Weather Underground to APRS Service Installer ${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo
}

print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

check_systemd() {
    if ! command -v systemctl &> /dev/null; then
        print_error "systemd is not available on this system"
        exit 1
    fi
}

create_user() {
    print_step "Creating service user and group..."
    
    if ! getent group "$SERVICE_GROUP" > /dev/null 2>&1; then
        groupadd --system "$SERVICE_GROUP"
        print_info "Created group: $SERVICE_GROUP"
    else
        print_info "Group already exists: $SERVICE_GROUP"
    fi
    
    if ! getent passwd "$SERVICE_USER" > /dev/null 2>&1; then
        useradd --system --gid "$SERVICE_GROUP" --shell /bin/false \
                --home-dir "$INSTALL_DIR" --create-home \
                --comment "Weather Underground to APRS Service" "$SERVICE_USER"
        print_info "Created user: $SERVICE_USER"
    else
        print_info "User already exists: $SERVICE_USER"
    fi
}

install_dependencies() {
    print_step "Installing system dependencies..."
    
    # Detect package manager and install Python3 and pip
    if command -v apt-get &> /dev/null; then
        apt-get update
        apt-get install -y python3 python3-pip python3-venv
    elif command -v yum &> /dev/null; then
        yum install -y python3 python3-pip python3-venv
    elif command -v dnf &> /dev/null; then
        dnf install -y python3 python3-pip python3-venv
    elif command -v pacman &> /dev/null; then
        pacman -S --noconfirm python python-pip python-virtualenv
    else
        print_warning "Could not detect package manager. Please ensure Python 3, pip, and venv are installed."
    fi
}

setup_application() {
    print_step "Setting up application directory..."
    
    # Create install directory
    mkdir -p "$INSTALL_DIR"
    
    # Copy application files
    if [[ -f "wunderground_to_aprs_sender.py" ]]; then
        cp -r . "$INSTALL_DIR/"
        print_info "Copied application files to $INSTALL_DIR"
    else
        print_error "Application files not found in current directory"
        print_info "Please run this script from the wunderground-to-aprs project directory"
        exit 1
    fi
    
    # Create Python virtual environment
    print_info "Creating Python virtual environment..."
    sudo -u "$SERVICE_USER" python3 -m venv "$INSTALL_DIR/venv"
    
    # Install Python dependencies
    print_info "Installing Python dependencies..."
    sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/pip" install --upgrade pip
    sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"
    
    # Set proper ownership
    chown -R "$SERVICE_USER:$SERVICE_GROUP" "$INSTALL_DIR"
    chmod 755 "$INSTALL_DIR"
    chmod +x "$INSTALL_DIR/wunderground_to_aprs_sender.py"
}

install_service() {
    print_step "Installing systemd service..."
    
    # Copy service file
    if [[ -f "wunderground-to-aprs.service" ]]; then
        cp "wunderground-to-aprs.service" "$SERVICE_FILE"
        chmod 644 "$SERVICE_FILE"
        print_info "Installed service file: $SERVICE_FILE"
    else
        print_error "Service file not found: wunderground-to-aprs.service"
        exit 1
    fi
    
    # Reload systemd
    systemctl daemon-reload
    print_info "Reloaded systemd daemon"
}

configure_service() {
    print_step "Configuring service..."
    
    print_info "Before starting the service, you need to configure it."
    print_info "Run the following command as the service user to set up configuration:"
    echo
    echo -e "${YELLOW}sudo -u $SERVICE_USER $INSTALL_DIR/venv/bin/python $INSTALL_DIR/wunderground_to_aprs_sender.py --save-config${NC}"
    echo
    print_info "This will prompt you for:"
    print_info "- Weather Underground station ID(s)"
    print_info "- APRS callsign(s)"
    print_info "- APRS passcode"
    print_info "- Weather Underground API key (optional)"
    print_info "- Transmission interval"
    echo
}

setup_service() {
    print_step "Setting up service for auto-start..."
    
    # Enable service
    systemctl enable "$SERVICE_NAME"
    print_info "Service enabled for auto-start"
    
    print_info "Service commands:"
    print_info "- Start:   sudo systemctl start $SERVICE_NAME"
    print_info "- Stop:    sudo systemctl stop $SERVICE_NAME"
    print_info "- Status:  sudo systemctl status $SERVICE_NAME"
    print_info "- Logs:    sudo journalctl -u $SERVICE_NAME -f"
    print_info "- Restart: sudo systemctl restart $SERVICE_NAME"
}

main() {
    print_header
    
    check_root
    check_systemd
    
    print_info "This script will install the Weather Underground to APRS service"
    print_info "Installation directory: $INSTALL_DIR"
    print_info "Service user: $SERVICE_USER"
    print_info "Service name: $SERVICE_NAME"
    echo
    
    read -p "Continue with installation? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Installation cancelled"
        exit 0
    fi
    
    create_user
    install_dependencies
    setup_application
    install_service
    configure_service
    setup_service
    
    echo
    print_header
    print_info "Installation completed successfully!"
    echo
    print_warning "IMPORTANT: Before starting the service, configure it by running:"
    echo -e "${YELLOW}sudo -u $SERVICE_USER $INSTALL_DIR/venv/bin/python $INSTALL_DIR/wunderground_to_aprs_sender.py --save-config${NC}"
    echo
    print_info "After configuration, start the service with:"
    echo -e "${GREEN}sudo systemctl start $SERVICE_NAME${NC}"
    echo
    print_info "Check service status with:"
    echo -e "${GREEN}sudo systemctl status $SERVICE_NAME${NC}"
    echo
}

# Handle script interruption
trap 'print_error "Installation interrupted"; exit 1' INT TERM

# Run main function
main "$@"
