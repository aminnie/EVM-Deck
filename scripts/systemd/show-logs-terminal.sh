#!/bin/bash
# Script to open a terminal window showing devdeck service logs
# This can be run manually to view logs in a terminal window

# Get project directory from environment variable or default to ~/devdeck
PROJECT_DIR="${PROJECT_DIR:-$HOME/devdeck}"

# Resolve to absolute path
PROJECT_DIR=$(cd "$PROJECT_DIR" 2>/dev/null && pwd || echo "$HOME/devdeck")

# Check if desktop environment is running
if [ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ]; then
    # No display available, log error and exit
    logger -t devdeck-logs "Cannot open terminal: No display available (not running in desktop environment)"
    exit 1
fi

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    logger -t devdeck-logs "ERROR: Project directory not found: $PROJECT_DIR"
    # Try to show error in a notification if available
    if command -v notify-send &> /dev/null; then
        notify-send "DevDeck Logs" "ERROR: Project directory not found: $PROJECT_DIR" 2>/dev/null || true
    fi
    exit 1
fi

# Check if manage-service.sh exists
if [ ! -f "$PROJECT_DIR/scripts/manage/manage-service.sh" ]; then
    logger -t devdeck-logs "ERROR: manage-service.sh not found in $PROJECT_DIR/scripts/manage/"
    if command -v notify-send &> /dev/null; then
        notify-send "DevDeck Logs" "ERROR: manage-service.sh not found" 2>/dev/null || true
    fi
    exit 1
fi

# Build the command to run
CMD="cd '$PROJECT_DIR' && bash scripts/manage/manage-service.sh logs; exec bash"

# Log function (try logger, fallback to syslog or file)
log_message() {
    local msg="$1"
    if command -v logger &> /dev/null; then
        logger -t devdeck-logs "$msg" 2>/dev/null || true
    fi
    # Also try to write to a log file for debugging
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $msg" >> "$PROJECT_DIR/logs/terminal-logs.log" 2>/dev/null || true
}

# Detect the terminal emulator and open it
TERMINAL_OPENED=0

if command -v lxterminal &> /dev/null; then
    # Raspberry Pi OS default terminal
    lxterminal -e "bash -c '$CMD'" 2>/dev/null &
    TERMINAL_OPENED=1
    log_message "Attempted to open lxterminal"
elif command -v xterm &> /dev/null; then
    xterm -e "bash -c '$CMD'" 2>/dev/null &
    TERMINAL_OPENED=1
    log_message "Attempted to open xterm"
elif command -v gnome-terminal &> /dev/null; then
    gnome-terminal -- bash -c "$CMD" 2>/dev/null &
    TERMINAL_OPENED=1
    log_message "Attempted to open gnome-terminal"
elif command -v xfce4-terminal &> /dev/null; then
    xfce4-terminal -e "bash -c '$CMD'" 2>/dev/null &
    TERMINAL_OPENED=1
    log_message "Attempted to open xfce4-terminal"
else
    # Fallback: try to find any terminal
    TERMINAL=$(which x-terminal-emulator 2>/dev/null || which xterm 2>/dev/null || echo "")
    if [ -n "$TERMINAL" ] && [ -x "$TERMINAL" ]; then
        $TERMINAL -e "bash -c '$CMD'" 2>/dev/null &
        TERMINAL_OPENED=1
        log_message "Attempted to open $TERMINAL"
    else
        log_message "ERROR: No terminal emulator found"
        if command -v notify-send &> /dev/null; then
            notify-send "DevDeck Logs" "ERROR: No terminal emulator found" 2>/dev/null || true
        fi
        exit 1
    fi
fi

# Log success
if [ $TERMINAL_OPENED -eq 1 ]; then
    log_message "Terminal launch command executed (PROJECT_DIR=$PROJECT_DIR)"
else
    log_message "ERROR: Failed to open any terminal emulator"
    if command -v notify-send &> /dev/null; then
        notify-send "DevDeck Logs" "ERROR: Failed to open terminal window" 2>/dev/null || true
    fi
    exit 1
fi

