#!/bin/bash
# Install desktop autostart entry to show devdeck logs in terminal on startup
# This script creates an autostart entry that opens a terminal window with logs

set -e

CURRENT_USER=$(whoami)
HOME_DIR=$(eval echo ~$CURRENT_USER)
PROJECT_DIR="${PROJECT_DIR:-$HOME_DIR/devdeck}"
AUTOSTART_DIR="$HOME_DIR/.config/autostart"

echo "=========================================="
echo "DevDeck Logs Autostart Installer"
echo "=========================================="
echo ""
echo "This will create a desktop autostart entry that opens a terminal"
echo "window showing devdeck service logs when you log in to the desktop."
echo ""
echo "Detected settings:"
echo "  Username: $CURRENT_USER"
echo "  Home directory: $HOME_DIR"
echo "  Project directory: $PROJECT_DIR"
echo "  Autostart directory: $AUTOSTART_DIR"
echo ""

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo "ERROR: Project directory not found: $PROJECT_DIR"
    echo "Please run this script from your project directory or set PROJECT_DIR environment variable."
    exit 1
fi

# Check if show-logs-terminal.sh exists
if [ ! -f "$PROJECT_DIR/scripts/systemd/show-logs-terminal.sh" ]; then
    echo "ERROR: show-logs-terminal.sh not found: $PROJECT_DIR/scripts/systemd/show-logs-terminal.sh"
    exit 1
fi

# Make the script executable
chmod +x "$PROJECT_DIR/scripts/systemd/show-logs-terminal.sh"

# Create autostart directory if it doesn't exist
mkdir -p "$AUTOSTART_DIR"

# Create desktop entry
DESKTOP_FILE="$AUTOSTART_DIR/devdeck-logs.desktop"
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=DevDeck Service Logs
Comment=Open terminal showing DevDeck service logs
Exec=bash -c 'sleep 5 && export PROJECT_DIR="$PROJECT_DIR" && cd "$PROJECT_DIR" && bash scripts/systemd/show-logs-terminal.sh'
Icon=utilities-terminal
Terminal=false
Categories=System;Utility;
StartupNotify=true
X-GNOME-Autostart-enabled=true
EOF

echo "Desktop entry created:"
echo "----------------------------------------"
cat "$DESKTOP_FILE"
echo "----------------------------------------"
echo ""

# Ask for confirmation
read -p "Install this autostart entry? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    rm "$DESKTOP_FILE"
    exit 0
fi

echo ""
echo "=========================================="
echo "Autostart entry installed successfully!"
echo "=========================================="
echo ""
echo "The terminal window with logs will open automatically when you log in."
echo ""
echo "To disable autostart:"
echo "  rm $DESKTOP_FILE"
echo ""
echo "To enable again:"
echo "  bash $PROJECT_DIR/scripts/systemd/install-logs-autostart.sh"
echo ""
echo "Note: The terminal will open 5 seconds after login to ensure"
echo "      the service has time to start."

