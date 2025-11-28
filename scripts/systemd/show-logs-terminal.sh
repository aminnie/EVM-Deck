#!/bin/bash
# Script to open a terminal window showing devdeck service logs
# This is typically called from a desktop autostart entry

# Detect the terminal emulator
if command -v lxterminal &> /dev/null; then
    # Raspberry Pi OS default terminal
    lxterminal -e "bash -c 'cd ~/devdeck && bash scripts/manage/manage-service.sh logs; exec bash'" &
elif command -v xterm &> /dev/null; then
    xterm -e "bash -c 'cd ~/devdeck && bash scripts/manage/manage-service.sh logs; exec bash'" &
elif command -v gnome-terminal &> /dev/null; then
    gnome-terminal -- bash -c "cd ~/devdeck && bash scripts/manage/manage-service.sh logs; exec bash" &
elif command -v xfce4-terminal &> /dev/null; then
    xfce4-terminal -e "bash -c 'cd ~/devdeck && bash scripts/manage/manage-service.sh logs; exec bash'" &
else
    # Fallback: try to find any terminal
    TERMINAL=$(which x-terminal-emulator 2>/dev/null || which xterm 2>/dev/null || echo "xterm")
    $TERMINAL -e "bash -c 'cd ~/devdeck && bash scripts/manage/manage-service.sh logs; exec bash'" &
fi

