#!/bin/bash

# Weather Underground to APRS Service Uninstaller
# This script removes the wunderground-to-aprs service from a Linux system

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
    echo -e "${BLUE}===================================================${NC}"
    echo -e "${BLUE} Weather Underground to APRS Service Uninstaller  ${NC}"
    echo -e "${BLUE}===================================================${NC}"
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

stop_service() {
    print_step "Stopping and disabling service..."
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        systemctl stop "$SERVICE_NAME"
        print_info "Stopped service: $SERVICE_NAME"
    fi
    
    if systemctl is-enabled --quiet "$SERVICE_NAME" 2>/dev/null; then
        systemctl disable "$SERVICE_NAME"
        print_info "Disabled service: $SERVICE_NAME"
    fi
}

remove_service_file() {
    print_step "Removing service file..."
    
    if [[ -f "$SERVICE_FILE" ]]; then
        rm -f "$SERVICE_FILE"
        print_info "Removed service file: $SERVICE_FILE"
        
        systemctl daemon-reload
        print_info "Reloaded systemd daemon"
    else
        print_info "Service file not found: $SERVICE_FILE"
    fi
}

remove_application() {
    print_step "Removing application directory..."
    
    if [[ -d "$INSTALL_DIR" ]]; then
        rm -rf "$INSTALL_DIR"
        print_info "Removed directory: $INSTALL_DIR"
    else
        print_info "Directory not found: $INSTALL_DIR"
    fi
}

remove_user() {
    print_step "Removing service user and group..."
    
    if getent passwd "$SERVICE_USER" > /dev/null 2>&1; then
        userdel "$SERVICE_USER"
        print_info "Removed user: $SERVICE_USER"
    else
        print_info "User not found: $SERVICE_USER"
    fi
    
    if getent group "$SERVICE_GROUP" > /dev/null 2>&1; then
        groupdel "$SERVICE_GROUP"
        print_info "Removed group: $SERVICE_GROUP"
    else
        print_info "Group not found: $SERVICE_GROUP"
    fi
}

main() {
    print_header
    
    check_root
    
    print_warning "This will completely remove the Weather Underground to APRS service"
    print_warning "and all its data from your system."
    echo
    print_info "The following will be removed:"
    print_info "- Service: $SERVICE_NAME"
    print_info "- User: $SERVICE_USER"
    print_info "- Group: $SERVICE_GROUP"
    print_info "- Directory: $INSTALL_DIR"
    print_info "- Service file: $SERVICE_FILE"
    echo
    
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Uninstallation cancelled"
        exit 0
    fi
    
    stop_service
    remove_service_file
    remove_application
    remove_user
    
    echo
    print_header
    print_info "Uninstallation completed successfully!"
    print_info "The Weather Underground to APRS service has been completely removed."
    echo
}

# Handle script interruption
trap 'print_error "Uninstallation interrupted"; exit 1' INT TERM

# Run main function
main "$@"
