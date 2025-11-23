# Ketron EVM Stream Deck Controller - User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Hardware Requirements](#hardware-requirements)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Using the Stream Deck](#using-the-stream-deck)
7. [Volume Control System](#volume-control-system)
8. [Key Mappings](#key-mappings)
9. [Navigation](#navigation)
10. [Troubleshooting](#troubleshooting)
11. [Advanced Features](#advanced-features)

---

## Introduction

The Ketron EVM Stream Deck Controller is a custom Stream Deck application designed to control your Ketron EVM (or Event) keyboard/organ via MIDI. It transforms your Elgato Stream Deck into a powerful MIDI control surface, allowing you to trigger Ketron functions, control volume levels, and navigate through different control pages.

### Key Features

- **MIDI Control**: Send pedal commands, tab commands, and Control Change (CC) messages to your Ketron device
- **Volume Management**: Comprehensive volume control system with tracking for multiple audio sources
- **Two-Page Navigation**: Navigate between main page and secondary page controls
- **Visual Feedback**: Color-coded buttons with text labels for easy identification
- **Real-time Updates**: Instant MIDI communication with your Ketron device

---

## Getting Started

### What You Need

- Elgato Stream Deck (any model)
- Ketron EVM or Event keyboard/organ
- Computer running Windows, Linux, macOS, or Raspberry Pi
- USB connection for Stream Deck
- MIDI connection to Ketron (USB MIDI or MIDI interface)

### First Time Setup

1. **Connect Your Hardware**
   - Connect your Stream Deck to your computer via USB
   - Connect your Ketron device via MIDI (USB MIDI or MIDI interface)

2. **Install Dependencies**
   - Follow the installation instructions in the main README.md
   - Ensure MIDI libraries are installed (mido, python-rtmidi)

3. **Verify MIDI Connection**
   - Run `python list_midi_ports.py` to see available MIDI ports
   - Run `python test_ketron_sysex.py` to test MIDI communication

4. **Run the Application**
   - Execute `python -m devdeck.main` or use the provided run scripts
   - The Stream Deck should display your configured buttons

---

## Hardware Requirements

### Stream Deck

- Any Elgato Stream Deck model (15-key, 32-key, etc.)
- USB connection to computer
- Official Stream Deck application must be closed (only one app can control the device at a time)

### Ketron Device

- Ketron EVM or Event keyboard/organ
- MIDI input capability
- USB MIDI connection or MIDI interface

### Computer

- Windows 10/11, Linux, macOS, or Raspberry Pi OS
- Python 3.8 or higher
- USB port for Stream Deck
- MIDI interface (if not using USB MIDI)

---

## Installation

### Prerequisites

1. **Python Environment**
   ```bash
   python --version  # Should be 3.8 or higher
   ```

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Windows-Specific: LibUSB HIDAPI**
   - Download `hidapi.dll` from the LibUSB HIDAPI project
   - Copy to your Python Scripts directory or add to PATH
   - See README.md for detailed instructions

### Installation Steps

1. **Clone or Download the Repository**
   ```bash
   git clone <repository-url>
   cd devdeck-main
   ```

2. **Set Up Virtual Environment (Recommended)**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify Installation**
   ```bash
   python -m devdeck.main --help
   ```

---

## Configuration

### Settings File

The application uses `config/settings.yml` to configure your Stream Deck layout. This file defines:
- Which controls appear on each key
- Deck controllers and their settings
- Navigation between pages

### Key Mappings File

The `config/key_mappings.json` file defines:
- Which Ketron function each Stream Deck key triggers
- Button colors and text labels
- MIDI message types (pedal, tab, or CC)

### Basic Configuration Structure

```yaml
decks:
- name: devdeck.decks.single_page_deck_controller.SinglePageDeckController
  serial_number: YOUR_STREAM_DECK_SERIAL
  settings:
    controls:
    - key: 0
      name: devdeck.controls.ketron_key_mapping_control.KetronKeyMappingControl
      settings: {}
```

---

## Using the Stream Deck

### Main Page (Keys 0-14)

The main page contains your primary Ketron controls. Each key is mapped to a specific Ketron function based on `key_mappings.json`.

**Common Functions:**
- **Key 0**: Ketron EVM identification
- **Keys 1-3**: Intro/End variations
- **Key 4**: To End
- **Keys 5-8**: Arrangement sections (A, B, C, D)
- **Key 9**: Variation
- **Key 10**: Navigation toggle (switches to second page)
- **Keys 11-14**: Additional functions (Half Bar, Fill, Break, etc.)

### Pressing a Key

When you press a key:
1. The application looks up the key number in `key_mappings.json`
2. Determines the MIDI message type (pedal, tab, or CC)
3. Sends the appropriate MIDI command to your Ketron device
4. The button may display visual feedback

### Button Colors

Buttons are color-coded for easy identification:
- **Blue**: Arrangement sections and variations
- **Green**: Intro/End and Fill functions
- **Red**: To End function
- **Orange**: Break functions
- **Grey**: Navigation and utility buttons

---

## Volume Control System

The application includes a sophisticated volume management system that tracks and controls multiple audio sources on your Ketron device.

### Tracked Volume Sources

The system tracks the following volume levels (each 0-127):
- **Lower** (Lower manual)
- **Voice1** (First voice)
- **Voice2** (Second voice)
- **Drawbars** (Drawbar volume)
- **Style** (Style/accompaniment volume)
- **Drum** (Drum volume)
- **Chord** (Chord volume)
- **Realchord** (Real chord volume)
- **Master** (Master volume)

### How Volume Control Works

1. **Select a Volume Source**
   - Press any volume button (e.g., "LOWERS", "VOICE1", "DRAWBARS")
   - This sets it as the "last pressed volume"
   - The current volume value is sent to the Ketron device

2. **Adjust Volume**
   - Press "Volume Up" to increment the last selected volume
   - Press "Volume Down" to decrement the last selected volume
   - Each press changes the volume by 1 (range: 0-127)

3. **Mute/Unmute**
   - Press "Mute" to toggle mute on the last selected volume
   - If muted (0), pressing Mute again restores to 64
   - If not muted, pressing Mute sets it to 0

4. **Master Volume**
   - Press "Master Volume" to select it and send current value
   - Volume Up/Down also control master volume when it's selected
   - Master volume uses MIDI CC 0x07 (Expression) on channel 16

### Volume Control Buttons

**Second Page (Keys 15-29):**
- Volume source buttons: LOWERS, VOICE1, VOICE2, DRAWBARS, STYLE, DRUM, CHORD, REALCHORD, MASTER VOLUME
- Control buttons: Volume Up, Volume Down, Mute

**How to Use:**
1. Navigate to the second page (press key 10 on main page)
2. Press a volume source button (e.g., "VOICE1")
3. Use "Volume Up" or "Volume Down" to adjust
4. Use "Mute" to toggle mute state

### MIDI Channel

All volume-related MIDI CC commands are sent on **MIDI channel 16** (0-indexed: 15) by default. This is the global channel for volume control.

---

## Key Mappings

### Understanding key_mappings.json

Each entry in `key_mappings.json` defines:
- `key_no`: Stream Deck key number (0-14 for main page, 15-29 for second page)
- `key_name`: Name of the Ketron function
- `source_list_name`: MIDI message type ("pedal_midis", "tab_midis", or "cc_midis")
- `text_color`: Text color for the button
- `background_color`: Background color for the button

### Message Types

1. **pedal_midis**: Pedal commands sent as SysEx messages
   - Examples: Start/Stop, Arrangements, Intro/End
   - Format: SysEx with ON/OFF states

2. **tab_midis**: Tab commands sent as SysEx messages
   - Examples: Variation, Menu navigation
   - Format: SysEx with ON/OFF states

3. **cc_midis**: Control Change messages
   - Examples: Volume controls (LOWERS, VOICE1, etc.)
   - Format: MIDI CC messages with values 0-127

### Editing Key Mappings

To customize your key mappings:

1. Open `config/key_mappings.json`
2. Find the key number you want to change
3. Modify the `key_name` to match a function in the Ketron MIDI dictionaries
4. Ensure `source_list_name` matches the function type
5. Save the file
6. Restart the application

**Available Functions:**
- Check `devdeck/ketron.py` for available pedal, tab, and CC functions
- Pedal functions: See `pedal_midis` dictionary
- Tab functions: See `tab_midis` dictionary
- CC functions: See `cc_midis` dictionary

---

## Navigation

### Two-Page System

The application supports two pages of controls:

1. **Main Page** (Keys 0-14)
   - Primary Ketron functions
   - Navigation toggle on key 10

2. **Second Page** (Keys 15-29)
   - Volume controls
   - Additional functions
   - Navigation toggle on key 10 (returns to main page)

### Switching Pages

- **To Second Page**: Press key 10 on the main page
- **To Main Page**: Press key 10 on the second page

The navigation button is typically grey and located in the same position on both pages for consistency.

### Page Offset

The second page uses an offset of 15, meaning:
- Physical key 0 on second page = mapping key_no 15
- Physical key 1 on second page = mapping key_no 16
- And so on...

---

## Troubleshooting

### Stream Deck Not Responding

**Problem**: Keys don't light up or respond to presses.

**Solutions**:
1. Ensure the official Stream Deck application is closed
2. Check USB connection
3. Verify the Stream Deck serial number in `settings.yml` matches your device
4. Restart the application

### MIDI Messages Not Sending

**Problem**: Pressing keys doesn't trigger Ketron functions.

**Solutions**:
1. Run `python list_midi_ports.py` to verify MIDI ports
2. Run `python test_ketron_sysex.py` to test MIDI communication
3. Check that your Ketron device is powered on and connected
4. Verify the MIDI port name in logs matches your device
5. Check Windows Device Manager for MIDI device recognition

### Volume Controls Not Working

**Problem**: Volume Up/Down or Mute buttons don't work.

**Solutions**:
1. Ensure you've selected a volume source first (press a volume button)
2. Check that you're on the second page (key 10 to navigate)
3. Verify the key mappings in `key_mappings.json` are correct
4. Check application logs for error messages

### Key Not Displaying Correctly

**Problem**: A key shows "INVALID KEY" or doesn't display text.

**Solutions**:
1. Check `key_mappings.json` for the key number
2. Verify the `key_name` exists in the appropriate MIDI dictionary
3. Ensure `source_list_name` matches the function type
4. Check for typos in the key name (case-insensitive matching is used)

### Windows MIDI Port Issues

**Problem**: MIDI port not found or not advertising correctly.

**Solutions**:
1. On Windows, virtual MIDI ports may not work by default
2. Install `loopMIDI` for virtual MIDI port support
3. Use hardware MIDI ports when possible
4. Check Device Manager for MIDI device recognition

### Application Crashes or Errors

**Problem**: Application crashes or shows errors.

**Solutions**:
1. Check Python version (3.8+ required)
2. Verify all dependencies are installed: `pip install -r requirements.txt`
3. Check application logs for specific error messages
4. Ensure `key_mappings.json` is valid JSON
5. Verify `settings.yml` is valid YAML

---

## Advanced Features

### Custom Key Mappings

You can create custom key mappings by:

1. **Adding New Functions**
   - Edit `devdeck/ketron.py` to add new MIDI functions
   - Add entries to `pedal_midis`, `tab_midis`, or `cc_midis` dictionaries

2. **Custom Button Colors**
   - Modify `background_color` and `text_color` in `key_mappings.json`
   - Available colors: red, green, blue, yellow, orange, purple, white, black, grey, ketron_blue

3. **Multiple MIDI Ports**
   - The application can work with multiple MIDI devices
   - Specify port names in control settings if needed

### Volume Manager API

The `KetronVolumeManager` provides programmatic access to volume control:

```python
from devdeck.ketron_volume_manager import KetronVolumeManager

volume_manager = KetronVolumeManager()

# Get current volume
current_voice1 = volume_manager.voice1

# Increment a volume
volume_manager.increment_voice1(amount=5)

# Set a volume directly
volume_manager.set_volume("voice1", 80)

# Get all volumes
all_volumes = volume_manager.get_all_volumes()
```

### MIDI Channel Configuration

The default MIDI channel for volume control is 16. To change it:

```python
volume_manager.set_midi_out_channel(1)  # Set to channel 1
```

### Testing MIDI Communication

Use the provided test scripts:

1. **List MIDI Ports**
   ```bash
   python list_midi_ports.py
   ```

2. **Test Basic MIDI**
   ```bash
   python test_midi.py
   ```

3. **Test Ketron SysEx**
   ```bash
   python test_ketron_sysex.py "Your MIDI Port Name"
   ```

4. **Check Application MIDI Identity**
   ```bash
   python check_app_midi_identity.py
   ```

---

## Additional Resources

### Documentation Files

- **README.md**: Main project documentation
- **MIDI_IMPLEMENTATION.md**: Detailed MIDI implementation guide
- **PROJECT_STRUCTURE.md**: Code organization and structure

### Scripts and Utilities

- **list_midi_ports.py**: List available MIDI ports
- **test_midi.py**: Test basic MIDI connectivity
- **test_ketron_sysex.py**: Test Ketron SysEx messages
- **check_app_midi_identity.py**: Check application MIDI port identity

### Support

For issues, questions, or contributions:
- Check the main README.md for known issues
- Review application logs for error messages
- Verify MIDI connection with test scripts
- Check that all dependencies are installed

---

## Quick Reference

### Main Page Key Functions
- **Key 0**: Ketron EVM
- **Keys 1-3**: Intro/End 1, 2, 3
- **Key 4**: To End
- **Keys 5-8**: Arrangements A, B, C, D
- **Key 9**: Variation
- **Key 10**: Navigate to Second Page
- **Keys 11-14**: Half Bar, Fill, Break, etc.

### Second Page Key Functions
- **Keys 0-8**: Volume sources (LOWERS, VOICE1, VOICE2, DRAWBARS, STYLE, DRUM, CHORD, REALCHORD, MASTER VOLUME)
- **Key 9**: Navigation toggle (return to main page)
- **Key 10**: Navigation toggle (return to main page)
- **Keys 11-14**: Additional volume controls

### Volume Control Workflow
1. Navigate to second page (Key 10 on main page)
2. Press a volume source button
3. Use Volume Up/Down to adjust
4. Use Mute to toggle mute state

### MIDI Channels
- **Volume Controls**: Channel 16 (default)
- **Other Controls**: As defined in key mappings

---

*Last Updated: 2025*
