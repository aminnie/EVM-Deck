#!/bin/bash
# Manage devdeck systemd service
# Provides easy commands to start, stop, restart, enable, disable, and check status

SERVICE_NAME="devdeck.service"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if service exists (multiple methods for robustness)
service_exists() {
    # Check if service file exists
    [ -f "/etc/systemd/system/${SERVICE_NAME}" ] || \
    systemctl list-unit-files 2>/dev/null | grep -q "^${SERVICE_NAME}" || \
    systemctl list-units --all 2>/dev/null | grep -q "${SERVICE_NAME}"
}

# Show usage
show_usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start       - Start the service"
    echo "  stop        - Stop the service"
    echo "  restart     - Restart the service"
    echo "  status      - Show service status"
    echo "  enable      - Enable service to start on boot"
    echo "  disable     - Disable service from starting on boot"
    echo "  toggle      - Toggle autostart (enable/disable)"
    echo "  logs        - Show service logs (follow mode)"
    echo "  logs-last   - Show last 50 log lines"
    echo "  logs-boot   - Show logs since last boot"
    echo "  help        - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start              # Start the service"
    echo "  $0 restart            # Restart the service"
    echo "  $0 toggle             # Toggle autostart on boot"
    echo "  $0 logs               # Follow logs in real-time"
}

# Commands that require the service to be installed
REQUIRES_SERVICE="start stop restart enable disable toggle"

# Check if service is installed (only for commands that require it)
COMMAND="${1:-help}"

# Check if this command requires the service
if echo "$REQUIRES_SERVICE" | grep -q "\b${COMMAND}\b"; then
    if ! service_exists; then
        echo -e "${RED}ERROR: Service ${SERVICE_NAME} is not installed.${NC}"
        echo ""
        echo "To install the service, run:"
        echo "  bash scripts/systemd/install-service.sh"
        echo ""
        echo "Or if you're on a system without systemd, you can still view logs using:"
        echo "  sudo journalctl -u ${SERVICE_NAME} -f"
        exit 1
    fi
elif [ "$COMMAND" != "help" ] && [ "$COMMAND" != "--help" ] && [ "$COMMAND" != "-h" ]; then
    # For read-only commands (logs, status), warn but allow
    if ! service_exists; then
        echo -e "${YELLOW}WARNING: Service ${SERVICE_NAME} may not be installed.${NC}"
        echo "Attempting to proceed anyway (logs may be empty if service never ran)..."
        echo ""
    fi
fi

# Command is already set above

case "$COMMAND" in
    start)
        echo "Starting ${SERVICE_NAME}..."
        if sudo systemctl start "$SERVICE_NAME"; then
            echo -e "${GREEN}✓ Service started${NC}"
            sudo systemctl status "$SERVICE_NAME" --no-pager -l | head -n 5
        else
            echo -e "${RED}✗ Failed to start service${NC}"
            exit 1
        fi
        ;;
    
    stop)
        echo "Stopping ${SERVICE_NAME}..."
        if sudo systemctl stop "$SERVICE_NAME"; then
            echo -e "${GREEN}✓ Service stopped${NC}"
        else
            echo -e "${RED}✗ Failed to stop service${NC}"
            exit 1
        fi
        ;;
    
    restart)
        echo "Restarting ${SERVICE_NAME}..."
        if sudo systemctl restart "$SERVICE_NAME"; then
            echo -e "${GREEN}✓ Service restarted${NC}"
            echo ""
            sudo systemctl status "$SERVICE_NAME" --no-pager -l | head -n 5
        else
            echo -e "${RED}✗ Failed to restart service${NC}"
            exit 1
        fi
        ;;
    
    status)
        echo "Service status for ${SERVICE_NAME}:"
        echo ""
        sudo systemctl status "$SERVICE_NAME" --no-pager -l
        ;;
    
    enable)
        echo "Enabling ${SERVICE_NAME} to start on boot..."
        if sudo systemctl enable "$SERVICE_NAME"; then
            echo -e "${GREEN}✓ Service enabled (will start on boot)${NC}"
        else
            echo -e "${RED}✗ Failed to enable service${NC}"
            exit 1
        fi
        ;;
    
    disable)
        echo "Disabling ${SERVICE_NAME} from starting on boot..."
        if sudo systemctl disable "$SERVICE_NAME"; then
            echo -e "${YELLOW}✓ Service disabled (will NOT start on boot)${NC}"
        else
            echo -e "${RED}✗ Failed to disable service${NC}"
            exit 1
        fi
        ;;
    
    toggle)
        if systemctl is-enabled --quiet "$SERVICE_NAME"; then
            echo "Service is currently enabled. Disabling..."
            if sudo systemctl disable "$SERVICE_NAME"; then
                echo -e "${YELLOW}✓ Service disabled (will NOT start on boot)${NC}"
            else
                echo -e "${RED}✗ Failed to disable service${NC}"
                exit 1
            fi
        else
            echo "Service is currently disabled. Enabling..."
            if sudo systemctl enable "$SERVICE_NAME"; then
                echo -e "${GREEN}✓ Service enabled (will start on boot)${NC}"
            else
                echo -e "${RED}✗ Failed to enable service${NC}"
                exit 1
            fi
        fi
        ;;
    
    logs)
        echo "Showing logs for ${SERVICE_NAME} (Press Ctrl+C to exit)..."
        echo ""
        # For follow mode, we can't easily check beforehand, so just try it
        # journalctl will show an error if the unit doesn't exist
        sudo journalctl -u "$SERVICE_NAME" -f || {
            echo ""
            echo -e "${RED}Failed to show logs for ${SERVICE_NAME}.${NC}"
            echo "The service may not be installed or may have never run."
            echo ""
            echo "To install the service, run:"
            echo "  bash scripts/systemd/install-service.sh"
            exit 1
        }
        ;;
    
    logs-last)
        echo "Last 50 log lines for ${SERVICE_NAME}:"
        echo ""
        # Try to show logs
        OUTPUT=$(sudo journalctl -u "$SERVICE_NAME" -n 50 2>&1)
        EXIT_CODE=$?
        if [ $EXIT_CODE -ne 0 ] || [ -z "$OUTPUT" ]; then
            echo -e "${RED}No logs found for ${SERVICE_NAME}.${NC}"
            echo "The service may not be installed or may have never run."
            echo ""
            echo "To install the service, run:"
            echo "  bash scripts/systemd/install-service.sh"
            exit 1
        else
            echo "$OUTPUT"
        fi
        ;;
    
    logs-boot)
        echo "Logs since last boot for ${SERVICE_NAME}:"
        echo ""
        # Try to show logs
        OUTPUT=$(sudo journalctl -u "$SERVICE_NAME" -b 2>&1)
        EXIT_CODE=$?
        if [ $EXIT_CODE -ne 0 ] || [ -z "$OUTPUT" ]; then
            echo -e "${RED}No logs found for ${SERVICE_NAME}.${NC}"
            echo "The service may not be installed or may have never run."
            echo ""
            echo "To install the service, run:"
            echo "  bash scripts/systemd/install-service.sh"
            exit 1
        else
            echo "$OUTPUT"
        fi
        ;;
    
    help|--help|-h)
        show_usage
        ;;
    
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        echo ""
        show_usage
        exit 1
        ;;
esac

