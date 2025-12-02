#!/bin/bash
# Install systemd service for devdeck
# This script helps set up the service with the correct paths

set -e

# Get current user and home directory
CURRENT_USER=$(whoami)
HOME_DIR=$(eval echo ~$CURRENT_USER)
PROJECT_DIR="$HOME_DIR/devdeck"

echo "=========================================="
echo "DevDeck Systemd Service Installer"
echo "=========================================="
echo ""
echo "Detected settings:"
echo "  Username: $CURRENT_USER"
echo "  Home directory: $HOME_DIR"
echo "  Project directory: $PROJECT_DIR"
echo ""

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo "ERROR: Project directory not found: $PROJECT_DIR"
    echo "Please run this script from your project directory or update PROJECT_DIR in the script."
    exit 1
fi

# Check if venv exists
if [ ! -f "$PROJECT_DIR/venv/bin/python" ]; then
    echo "ERROR: Virtual environment not found: $PROJECT_DIR/venv"
    echo "Please create the virtual environment first:"
    echo "  cd $PROJECT_DIR"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Create service file with correct paths
SERVICE_FILE="/tmp/devdeck.service"
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Ketron EVM Stream Deck Controller
After=network.target sound.target
Wants=network-online.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$PROJECT_DIR/venv/bin/python -m devdeck.main
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security settings
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

echo "Service file created:"
echo "----------------------------------------"
cat "$SERVICE_FILE"
echo "----------------------------------------"
echo ""

# Ask for confirmation
read -p "Install this service? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    rm "$SERVICE_FILE"
    exit 0
fi

# Copy service file to systemd directory
echo "Installing service..."
sudo cp "$SERVICE_FILE" /etc/systemd/system/devdeck.service
rm "$SERVICE_FILE"

# Reload systemd
echo "Reloading systemd..."
sudo systemctl daemon-reload

# Enable service
echo "Enabling service (auto-start on boot)..."
sudo systemctl enable devdeck.service

echo ""
echo "=========================================="
echo "Service installed successfully!"
echo "=========================================="
echo ""
echo "Useful commands:"
echo "  Start service:    sudo systemctl start devdeck.service"
echo "  Stop service:     sudo systemctl stop devdeck.service"
echo "  Restart service:  sudo systemctl restart devdeck.service"
echo "  Check status:     sudo systemctl status devdeck.service"
echo "  View logs:        sudo journalctl -u devdeck.service -f"
echo ""
read -p "Start the service now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo systemctl start devdeck.service
    echo ""
    echo "Service started. Checking status..."
    sudo systemctl status devdeck.service --no-pager -l
fi

