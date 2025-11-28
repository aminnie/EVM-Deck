#!/bin/bash
# Update devdeck application from git and restart service
# This script pulls the latest code and restarts the devdeck service

set -e

SERVICE_NAME="devdeck.service"
PROJECT_DIR="${PROJECT_DIR:-$(pwd)}"

# If not in project directory, try to find it
if [ ! -d "$PROJECT_DIR/.git" ]; then
    # Try common locations
    if [ -d "$HOME/devdeck/.git" ]; then
        PROJECT_DIR="$HOME/devdeck"
    elif [ -d "/home/$(whoami)/devdeck/.git" ]; then
        PROJECT_DIR="/home/$(whoami)/devdeck"
    else
        echo "ERROR: Could not find devdeck project directory."
        echo "Please run this script from the project directory or set PROJECT_DIR environment variable."
        exit 1
    fi
fi

echo "=========================================="
echo "DevDeck Update Script"
echo "=========================================="
echo ""
echo "Project directory: $PROJECT_DIR"
echo ""

# Change to project directory
cd "$PROJECT_DIR"

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "ERROR: git is not installed or not in PATH"
    exit 1
fi

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "ERROR: Not a git repository: $PROJECT_DIR"
    exit 1
fi

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"
echo ""

# Check if there are uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "WARNING: You have uncommitted changes in your working directory."
    echo "These changes may be overwritten by git pull."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Update cancelled."
        exit 0
    fi
fi

# Perform git pull
echo "Pulling latest changes from git..."
if git pull; then
    echo ""
    echo "✓ Git pull completed successfully"
else
    echo ""
    echo "ERROR: Git pull failed. Please resolve conflicts manually."
    exit 1
fi

# Check if service exists
if ! systemctl list-unit-files | grep -q "^${SERVICE_NAME}"; then
    echo ""
    echo "WARNING: Service ${SERVICE_NAME} is not installed."
    echo "Skipping service restart."
    echo ""
    echo "To install the service, run:"
    echo "  bash scripts/systemd/install-service.sh"
    exit 0
fi

# Check if service is running
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo ""
    echo "Service is currently running. Restarting..."
    if sudo systemctl restart "$SERVICE_NAME"; then
        echo "✓ Service restarted successfully"
    else
        echo "ERROR: Failed to restart service"
        exit 1
    fi
else
    echo ""
    echo "Service is not running. Starting service..."
    if sudo systemctl start "$SERVICE_NAME"; then
        echo "✓ Service started successfully"
    else
        echo "ERROR: Failed to start service"
        exit 1
    fi
fi

# Show service status
echo ""
echo "Service status:"
sudo systemctl status "$SERVICE_NAME" --no-pager -l | head -n 10

echo ""
echo "=========================================="
echo "Update completed successfully!"
echo "=========================================="
echo ""
echo "To view logs: sudo journalctl -u ${SERVICE_NAME} -f"

