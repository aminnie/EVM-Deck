#!/usr/bin/env bash
# Start DevDeck application
# This script activates the virtual environment and runs the application

set -e

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo "Virtual environment not found. Please run setup.sh first."
    echo "Or create a virtual environment manually:"
    echo "  python3 -m venv venv"
    echo "  ./venv/bin/pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment and run the application
source venv/bin/activate
python -m devdeck.main

