# DevDeck - Stream Deck Controller User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Hardware Requirements](#hardware-requirements)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Available Controls](#available-controls)
7. [Using the Stream Deck](#using-the-stream-deck)
8. [MIDI Support](#midi-support)
9. [Ketron Integration](#ketron-integration)
10. [Volume Control System](#volume-control-system)
11. [Navigation](#navigation)
12. [Troubleshooting](#troubleshooting)
13. [Advanced Features](#advanced-features)

---

## Introduction

DevDeck is a Python-based control system for Elgato Stream Deck devices that enables developers and musicians to create custom button layouts and controls. The project includes specialized MIDI support and Ketron EVM/Event device integration, making it ideal for musicians and audio professionals who need to control MIDI devices from their Stream Deck.

### Key Features

- **Multi-Device Support**: Manage multiple Stream Deck devices simultaneously with independent configurations
- **MIDI Integration**: Send MIDI Control Change (CC) and System Exclusive (SysEx) messages to any MIDI device
- **Ketron EVM Control**: Specialized integration for Ketron EVM/Event devices with pre-configured SysEx messages
- **Volume Management**: Comprehensive volume control system with tracking for multiple audio sources (Ketron devices)
- **Visual Feedback**: Keys flash with white background for successful MIDI sends, red for failures
- **Multi-Page Navigation**: Navigate between different deck pages using navigation controls
- **Extensible Architecture**: Plugin-based control system for custom functionality
- **Cross-Platform**: Works on Windows, Linux, macOS, and Raspberry Pi

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
   - Run `python tests/list_midi_ports.py` to see available MIDI ports
   - Run `python tests/devdeck/ketron/test_ketron_sysex.py` to test MIDI communication

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
- Python 3.12 or higher
- USB port for Stream Deck
- MIDI interface (if not using USB MIDI)

**Platform-Specific Requirements:**
- **Linux**: PulseAudio for audio controls (MicMuteControl, VolumeLevelControl, VolumeMuteControl)
- **Windows**: LibUSB HIDAPI backend (hidapi.dll) required

---

## Installation

### Prerequisites

1. **Python Environment**
   ```bash
   python --version  # Should be 3.12 or higher
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
    icon: ~/path/to/icon.png  # Optional: icon for the deck
    controls:
    - key: 0
      name: devdeck.controls.clock_control.ClockControl
      settings: {}
    - key: 1
      name: devdeck.ketron.controls.ketron_key_mapping_control.KetronKeyMappingControl
      settings:
        port: "CH345:CH345 MIDI 1"  # Optional: specific MIDI port
        midi_channel: 16  # Optional: MIDI channel (1-16)
```

### Multi-Device Configuration

You can configure multiple Stream Deck devices in the same `settings.yml`:

```yaml
decks:
- name: devdeck.decks.single_page_deck_controller.SinglePageDeckController
  serial_number: FIRST_STREAM_DECK_SERIAL
  settings:
    controls: [...]
- name: devdeck.decks.single_page_deck_controller.SinglePageDeckController
  serial_number: SECOND_STREAM_DECK_SERIAL
  settings:
    controls: [...]
```

---

## Available Controls

DevDeck provides a comprehensive set of built-in controls for various use cases:

### General Controls

#### ClockControl
- **Class**: `devdeck.controls.clock_control.ClockControl`
- **Description**: Displays current date and time on deck keys
- **Features**: Auto-updates every second
- **Settings**: None required
- **Example**:
  ```yaml
  - key: 0
    name: devdeck.controls.clock_control.ClockControl
    settings: {}
  ```

#### CommandControl
- **Class**: `devdeck.controls.command_control.CommandControl`
- **Description**: Executes system commands on key press
- **Features**: 
  - Supports custom icons and command arguments
  - Optional security allowlist for commands
- **Settings**:
  - `command` (required): Command to execute (string or list)
  - `icon` (required): Path to icon file
  - `allowed_commands` (optional): List of allowed command names for security
- **Example**:
  ```yaml
  - key: 1
    name: devdeck.controls.command_control.CommandControl
    settings:
      command: "notepad.exe"
      icon: "~/icons/notepad.png"
      allowed_commands: ["notepad.exe", "calc.exe"]
  ```

#### TextControl
- **Class**: `devdeck.controls.text_control.TextControl`
- **Description**: Displays custom text on keys with configurable colors and fonts
- **Features**: 
  - Supports runtime text updates via `update_text()` method
  - Automatic text wrapping (6 characters per line)
  - Custom background and text colors
- **Settings**:
  - `text` (required): Text to display (supports `\n` for newlines)
  - `font_size` (optional): Font size (default: 100)
  - `color` (optional): Text color (default: white)
  - `background_color` (optional): Background color (default: lightblue)
- **Example**:
  ```yaml
  - key: 2
    name: devdeck.controls.text_control.TextControl
    settings:
      text: "Hello\nWorld"
      font_size: 120
      color: "white"
      background_color: "blue"
  ```

#### NavigationToggleControl
- **Class**: `devdeck.controls.navigation_toggle_control.NavigationToggleControl`
- **Description**: Navigates between deck pages
- **Features**: Returns to previous deck or navigates to a target deck
- **Settings**:
  - `icon` (optional): Icon path
  - `background_color` (optional): Background color
  - `text_color` (optional): Text color
  - `target_deck_class` (optional): Target deck controller class
  - `target_deck_settings` (optional): Settings for target deck
- **Example**:
  ```yaml
  - key: 10
    name: devdeck.controls.navigation_toggle_control.NavigationToggleControl
    settings:
      background_color: grey
      text_color: black
      target_deck_class: devdeck.decks.second_page_deck_controller.SecondPageDeckController
      target_deck_settings:
        controls: [...]
  ```

#### TimerControl
- **Class**: `devdeck.controls.timer_control.TimerControl`
- **Description**: Stopwatch functionality with start/stop/reset operations
- **Features**: 
  - Displays elapsed time in HH:MM:SS format
  - First press starts, second press stops, third press resets
- **Settings**: None required
- **Example**:
  ```yaml
  - key: 3
    name: devdeck.controls.timer_control.TimerControl
    settings: {}
  ```

#### NameListControl
- **Class**: `devdeck.controls.name_list_control.NameListControl`
- **Description**: Cycles through a list of names/initials
- **Features**: Useful for stand-ups and team rotations
- **Settings**:
  - `names` (required): List of names (e.g., ["John Doe", "Jane Smith"])
- **Example**:
  ```yaml
  - key: 4
    name: devdeck.controls.name_list_control.NameListControl
    settings:
      names:
        - "John Doe"
        - "Jane Smith"
        - "Bob Johnson"
  ```

### Linux Audio Controls (PulseAudio Required)

These controls work on Linux systems with PulseAudio:

#### MicMuteControl
- **Class**: `devdeck.controls.mic_mute_control.MicMuteControl`
- **Description**: Toggles microphone mute state
- **Features**: Visual feedback for mute status (microphone icon changes)
- **Settings**:
  - `microphone` (required): Microphone device description
- **Example**:
  ```yaml
  - key: 5
    name: devdeck.controls.mic_mute_control.MicMuteControl
    settings:
      microphone: "Built-in Audio Analog Stereo"
  ```

#### VolumeLevelControl
- **Class**: `devdeck.controls.volume_level_control.VolumeLevelControl`
- **Description**: Sets audio output volume to specific level
- **Features**: 
  - Displays current volume percentage
  - Highlights when volume matches target
- **Settings**:
  - `output` (required): Audio output device description
  - `volume` (required): Target volume (0-100)
- **Example**:
  ```yaml
  - key: 6
    name: devdeck.controls.volume_level_control.VolumeLevelControl
    settings:
      output: "Built-in Audio Analog Stereo"
      volume: 75
  ```

#### VolumeMuteControl
- **Class**: `devdeck.controls.volume_mute_control.VolumeMuteControl`
- **Description**: Toggles audio output mute
- **Features**: Visual state indication (volume icon changes)
- **Settings**:
  - `output` (required): Audio output device description
- **Example**:
  ```yaml
  - key: 7
    name: devdeck.controls.volume_mute_control.VolumeMuteControl
    settings:
      output: "Built-in Audio Analog Stereo"
  ```

### MIDI Controls

#### MidiControl
- **Class**: `devdeck.midi.controls.midi_control.MidiControl`
- **Description**: Sends MIDI CC or SysEx messages
- **Features**: 
  - Configurable port, channel, and message data
  - **Visual Feedback**: Keys flash for 100ms after sending:
    - White background for successful sends
    - Red background with error message for failed sends
- **Settings**:
  - `type` (required): "cc" or "sysex"
  - `port` (optional): MIDI port name
  - For CC: `control` (0-127), `value` (0-127), `channel` (0-15, default: 0)
  - For SysEx: `data` (list of bytes) or `raw_data` (includes 0xF0 and 0xF7)
  - `icon` (optional): Path to icon file
- **Example (CC)**:
  ```yaml
  - key: 8
    name: devdeck.midi.controls.midi_control.MidiControl
    settings:
      type: cc
      control: 102
      value: 64
      channel: 0
      port: "MIDI Device"
  ```
- **Example (SysEx)**:
  ```yaml
  - key: 9
    name: devdeck.midi.controls.midi_control.MidiControl
    settings:
      type: sysex
      data: [0x00, 0x20, 0x29, 0x01, 0x00]
      port: "MIDI Device"
  ```

### Ketron Controls

#### KetronKeyMappingControl
- **Class**: `devdeck.ketron.controls.ketron_key_mapping_control.KetronKeyMappingControl`
- **Description**: Maps Stream Deck keys to Ketron functions
- **Features**: 
  - Reads mappings from `config/key_mappings.json`
  - Sends Ketron-specific SysEx messages (pedal, tab, and CC commands)
  - **Visual Feedback**: Keys flash for 100ms after sending MIDI messages:
    - White background for successful sends
    - Red background with error message for failed sends
- **Settings**:
  - `key_mappings_file` (optional): Path to key_mappings.json (default: config/key_mappings.json)
  - `port` (optional): MIDI port name
  - `cc_value` (optional): CC value for cc_midis (default: 64)
  - `cc_channel` (optional): MIDI channel for CC messages (default: 0)
  - `midi_channel` (optional): MIDI channel for volume CC messages (1-16, default: 16)
- **Example**:
  ```yaml
  - key: 0
    name: devdeck.ketron.controls.ketron_key_mapping_control.KetronKeyMappingControl
    settings:
      port: "CH345:CH345 MIDI 1"
      midi_channel: 16
  ```

---

## Using the Stream Deck

### Basic Operation

When you press a key on your Stream Deck:
1. The application identifies which control is assigned to that key
2. Executes the control's `pressed()` method
3. For MIDI controls, sends the MIDI message and provides visual feedback
4. For other controls, performs the configured action

### Visual Feedback for MIDI Controls

All MIDI controls (MidiControl and KetronKeyMappingControl) provide immediate visual feedback:

- **Successful Sends**: The key flashes with a **white background** for 100ms, confirming the message was sent successfully
- **Failed Sends**: The key flashes with a **red background** for 100ms, displaying an error message (e.g., "SEND\nFAILED")
- **Automatic Restoration**: After the flash, the key automatically returns to its original appearance

This feedback helps you verify that MIDI messages are being sent correctly to your devices.

### Main Page (Keys 0-14)

The main page typically contains your primary controls. For Ketron setups, each key is mapped to a specific Ketron function based on `key_mappings.json`.

**Example Ketron Functions:**
- **Key 0**: Ketron EVM identification
- **Keys 1-3**: Intro/End variations
- **Key 4**: To End
- **Keys 5-8**: Arrangement sections (A, B, C, D)
- **Key 9**: Variation
- **Key 10**: Navigation toggle (switches to second page)
- **Keys 11-14**: Additional functions (Half Bar, Fill, Break, etc.)

### Button Colors

Buttons can be color-coded for easy identification. Common color schemes:
- **Blue**: Arrangement sections and variations
- **Green**: Intro/End and Fill functions
- **Red**: To End function
- **Orange**: Break functions
- **Grey**: Navigation and utility buttons

Colors are configured in `key_mappings.json` for Ketron controls, or in control settings for other controls.

---

## MIDI Support

### Overview

DevDeck includes comprehensive MIDI support through the `MidiManager` singleton and `MidiControl` class. The implementation uses `mido` with `python-rtmidi` backend for cross-platform compatibility.

### MIDI Manager Features

The `MidiManager` provides:
- Thread-safe MIDI port management
- Automatic port connection/disconnection
- Support for multiple MIDI ports simultaneously
- CC and SysEx message sending

### MIDI Port Selection

MIDI ports can be specified in control settings:
- If a port is specified, the control uses that port
- If no port is specified, the first available MIDI port is used
- Port names must match exactly (case-sensitive)

### Listing Available MIDI Ports

To see available MIDI ports on your system:
```bash
python tests/list_midi_ports.py
```

### Testing MIDI Communication

Use the provided test scripts:

1. **List MIDI Ports**
   ```bash
   python tests/list_midi_ports.py
   ```

2. **Test Basic MIDI**
   ```bash
   python tests/devdeck/midi/test_midi.py
   ```

3. **Test MIDI Output**
   ```bash
   python scripts/test/test_midi_output.py
   ```

---

## Ketron Integration

### Overview

DevDeck includes specialized support for Ketron EVM and Event devices, with pre-configured SysEx message formatting and a comprehensive volume management system.

### Ketron MIDI Message Types

Ketron devices use three types of MIDI messages:

1. **Pedal Commands** (`pedal_midis`): Sent as SysEx messages
   - Examples: Start/Stop, Arrangements, Intro/End
   - Format: SysEx with ON/OFF states

2. **Tab Commands** (`tab_midis`): Sent as SysEx messages
   - Examples: Variation, Menu navigation
   - Format: SysEx with ON/OFF states

3. **Control Change** (`cc_midis`): Standard MIDI CC messages
   - Examples: Volume controls (LOWERS, VOICE1, etc.)
   - Format: MIDI CC messages with values 0-127

### Key Mappings File

The `config/key_mappings.json` file defines:
- Which Ketron function each Stream Deck key triggers
- Button colors and text labels
- MIDI message types (pedal, tab, or CC)

Each entry in `key_mappings.json` defines:
- `key_no`: Stream Deck key number (0-14 for main page, 15-29 for second page)
- `key_name`: Name of the Ketron function
- `source_list_name`: MIDI message type ("pedal_midis", "tab_midis", or "cc_midis")
- `text_color`: Text color for the button
- `background_color`: Background color for the button

### Editing Key Mappings

To customize your key mappings:

1. Open `config/key_mappings.json`
2. Find the key number you want to change
3. Modify the `key_name` to match a function in the Ketron MIDI dictionaries
4. Ensure `source_list_name` matches the function type
5. Save the file
6. Restart the application (or the control will reload on next key press)

**Available Functions:**
- Check `devdeck/ketron.py` for available pedal, tab, and CC functions
- Pedal functions: See `pedal_midis` dictionary
- Tab functions: See `tab_midis` dictionary
- CC functions: See `cc_midis` dictionary

### Testing Ketron MIDI Communication

To test Ketron SysEx messages:
```bash
python tests/devdeck/ketron/test_ketron_sysex.py "Your MIDI Port Name"
```

To check application MIDI identity:
```bash
python scripts/check/check_app_midi_identity.py
```

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
1. Run `python tests/list_midi_ports.py` to verify MIDI ports
2. Run `python tests/devdeck/ketron/test_ketron_sysex.py` to test MIDI communication
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
1. Check Python version (3.12+ required)
2. Verify all dependencies are installed: `pip install -r requirements.txt`
3. Check application logs for specific error messages
4. Ensure `key_mappings.json` is valid JSON
5. Verify `settings.yml` is valid YAML

### Linux Audio Controls Not Working

**Problem**: MicMuteControl, VolumeLevelControl, or VolumeMuteControl don't work.

**Solutions**:
1. Ensure PulseAudio is installed and running
2. Verify the device description matches exactly (case-sensitive)
3. List available devices using PulseAudio tools:
   ```bash
   pactl list sources  # For microphones
   pactl list sinks    # For audio outputs
   ```
4. Use the exact description from the output in your settings

### Control Not Responding

**Problem**: A control doesn't respond when pressed.

**Solutions**:
1. Check that the control class name is correct in `settings.yml`
2. Verify all required settings are provided
3. Check application logs for error messages
4. Ensure the control is properly registered in the deck controller

---

## Advanced Features

### Multi-Device Support

DevDeck supports multiple Stream Deck devices simultaneously. Each device is configured independently using its serial number:

```yaml
decks:
- name: devdeck.decks.single_page_deck_controller.SinglePageDeckController
  serial_number: FIRST_DEVICE_SERIAL
  settings:
    controls: [...]
- name: devdeck.decks.single_page_deck_controller.SinglePageDeckController
  serial_number: SECOND_DEVICE_SERIAL
  settings:
    controls: [...]
```

### Custom Key Mappings

You can create custom key mappings by:

1. **Adding New Functions**
   - Edit `devdeck/ketron.py` to add new MIDI functions
   - Add entries to `pedal_midis`, `tab_midis`, or `cc_midis` dictionaries

2. **Custom Button Colors**
   - Modify `background_color` and `text_color` in `key_mappings.json`
   - Available colors: red, green, blue, yellow, orange, purple, white, black, grey, ketron_blue
   - Custom colors can be defined in COLOR_MAP

3. **Multiple MIDI Ports**
   - The application can work with multiple MIDI devices
   - Specify port names in control settings if needed

### Runtime Text Updates

TextControl supports runtime text updates through the deck controller:

```python
from devdeck.decks.single_page_deck_controller import SinglePageDeckController

# Get the deck controller instance
deck_controller = ...  # Your deck controller instance

# Update text on key 2
deck_controller.update_text(2, "New\nText")
```

### Creating Custom Controls

You can create custom controls by:

1. Create a new class inheriting from `DeckControl` or `BaseDeckControl`
2. Implement `initialize()`, `pressed()`, and optionally `released()` methods
3. Define `settings_schema()` for validation
4. Register your control in `settings.yml` using the full class path

Example:
```python
from devdeck_core.controls.deck_control import DeckControl

class MyCustomControl(DeckControl):
    def initialize(self):
        # Set up the control
        pass
    
    def pressed(self):
        # Handle key press
        pass
    
    def settings_schema(self):
        return {
            'my_setting': {
                'type': 'string',
                'required': True
            }
        }
```

### Deck Controller Methods

Deck controllers provide useful methods:

- `get_control(key_no, control_type=None)`: Get a control by key number, optionally filtering by type
- `update_text(key_no, new_text)`: Update text on a TextControl at runtime

Example:
```python
# Get a specific control
text_control = deck_controller.get_control(2, TextControl)

# Update text
deck_controller.update_text(2, "Updated")
```

### Volume Manager API

The `KetronVolumeManager` provides programmatic access to volume control:

```python
from devdeck.ketron import KetronVolumeManager

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
from devdeck.ketron import KetronVolumeManager

volume_manager = KetronVolumeManager()
volume_manager.set_midi_out_channel(1)  # Set to channel 1
```

Or configure it in settings:
```yaml
- key: 0
  name: devdeck.ketron.controls.ketron_key_mapping_control.KetronKeyMappingControl
  settings:
    midi_channel: 1  # Use channel 1 instead of default 16
```

---

## Additional Resources

### Documentation Files

- **README.md**: Main project documentation
- **MIDI_IMPLEMENTATION.md**: Detailed MIDI implementation guide
- **PROJECT_STRUCTURE.md**: Code organization and structure

### Scripts and Utilities

- **tests/list_midi_ports.py**: List available MIDI ports
- **tests/devdeck/midi/test_midi.py**: Test basic MIDI connectivity
- **tests/devdeck/ketron/test_ketron_sysex.py**: Test Ketron SysEx messages
- **scripts/check/check_app_midi_identity.py**: Check application MIDI port identity
- **scripts/test/test_midi_output.py**: Test MIDI output functionality
- **scripts/generate/generate_key_mappings.py**: Generate key mappings file

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

---

*Last Updated: December 2025*
