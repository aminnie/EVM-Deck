# DevDeck

**Stream Deck control software for software developers with MIDI and Ketron EVM integration**

[![CI](https://github.com/jamesridgway/devdeck/workflows/CI/badge.svg?branch=main)](https://github.com/jamesridgway/devdeck/actions)

DevDeck is a Python-based control system for Elgato Stream Deck devices that enables developers to create custom button layouts and controls. The project extends the original devdeck with specialized MIDI support and Ketron EVM/Event device integration, making it ideal for musicians and audio professionals who need to control MIDI devices from their Stream Deck.

## Table of Contents

- [Overview](#overview)
- [Technical Architecture](#technical-architecture)
- [Key Features](#key-features)
- [Installation](#installation)
- [Building and Installing](#building-and-installing)
- [Configuration](#configuration)
- [Built-in Controls](#built-in-controls)
- [MIDI Support](#midi-support)
- [Ketron Integration](#ketron-integration)
- [Project Structure](#project-structure)
- [Development](#development)
- [Testing](#testing)
- [Known Issues](#known-issues)
- [Checking System Logs for Errors](#checking-system-logs-for-errors)
- [Documentation](#documentation)

## Overview

DevDeck provides a flexible framework for controlling Stream Deck hardware through a YAML-based configuration system. The application supports multiple Stream Deck devices simultaneously, each with its own configuration. The architecture is modular, allowing for easy extension with custom controls and deck layouts.

### Core Capabilities

- **Multi-Device Support**: Manage multiple Stream Deck devices with independent configurations
- **MIDI Integration**: Send MIDI Control Change (CC) and System Exclusive (SysEx) messages
- **Ketron EVM Control**: Specialized integration for Ketron EVM/Event devices
- **Extensible Architecture**: Plugin-based control system for custom functionality
- **Cross-Platform**: Works on Windows, Linux, macOS, and Raspberry Pi

## Technical Architecture

### System Components

```
┌─────────────────┐
│   main.py       │  Entry point, device enumeration, settings loading
└────────┬────────┘
         │
         ├──► USB Device Checker ───► Device Validation
         │         │                        │
         │         │                        ├── Elgato Stream Deck (USB)
         │         │                        └── MIDI Output Devices (USB)
         │         │
         ├──► DeckManager ───► DeckController ───► Controls
         │         │                  │                │
         │         │                  │                ├── ClockControl
         │         │                  │                ├── CommandControl
         │         │                  │                ├── MidiControl
         │         │                  │                ├── VolumeControl
         │         │                  │                └── KetronKeyMappingControl
         │         │                  │
         │         └──► Settings Management (YAML)
         │
         └──► MIDI Manager (Singleton)
                    │
                    ├──► Auto-Connect Hardware Port
                    └──► MIDI Port Management
                         ├── CC Messages
                         └── SysEx Messages
```

### Key Architectural Patterns

1. **Deck Manager Pattern**: Centralized management of Stream Deck devices and their active deck controllers
2. **Control Inheritance**: All controls inherit from `BaseDeckControl` which extends `devdeck-core`'s `DeckControl`
3. **Singleton MIDI Manager**: Thread-safe MIDI port management with automatic connection handling
4. **Settings Validation**: YAML configuration validated using Cerberus schema validation
5. **Deck Stack**: Navigation between decks using a stack-based approach

### Technology Stack

- **Python 3.12+**: Core runtime
- **devdeck-core 1.0.7**: Base Stream Deck library
- **mido + python-rtmidi**: Cross-platform MIDI support
- **PyYAML**: Configuration file parsing
- **Cerberus**: Settings validation
- **Pillow**: Image rendering for deck keys
- **pulsectl**: Linux audio control (volume management)

## Key Features

### 1. Multi-Deck Support
- Simultaneous control of multiple Stream Deck devices
- Per-device configuration using serial numbers
- Independent deck layouts per device

### 2. MIDI Integration
- **Control Change (CC) Messages**: Standard MIDI CC support (0-127)
- **System Exclusive (SysEx) Messages**: Custom MIDI commands for specialized devices
- **Cross-Platform MIDI**: Works on Windows, Linux, macOS, and Raspberry Pi
- **Port Management**: Automatic or manual MIDI port selection
- **Automatic MIDI Connection**: Automatically detects and connects to hardware MIDI output devices at startup
- **Thread-Safe**: Safe concurrent MIDI message sending
- **Visual Feedback**: Keys flash for 100ms after sending MIDI messages:
  - **White background** for successful sends
  - **Red background** for failed sends (with error message)

### 3. Ketron EVM Integration
- Pre-configured SysEx message formatting for Ketron devices
- Key mapping system for Stream Deck keys to Ketron functions
- Volume slider control via MIDI CC
- Color-coded button states

### 4. Configuration System
- YAML-based settings with schema validation
- Automatic settings migration from legacy formats
- Key mapping import from JSON files
- Default configuration generation for new devices

### 5. Extensible Control System
- Plugin architecture for custom controls
- Base control class with common functionality
- Deck controller system for multi-page layouts
- Navigation controls for deck switching

### 6. Automatic Device Detection
- **USB Device Validation**: Automatically checks for required USB devices at startup
  - **Elgato Stream Deck**: Validates Stream Deck connection via USB (Linux/Raspberry Pi)
  - **MIDI Output Devices**: Detects MIDI USB adapters and interfaces (CH345, Roland, M-Audio, etc.)
- **Automatic MIDI Connection**: Connects to the first available hardware MIDI port on startup
- **Error Handling**: Clear error messages if required devices are missing
- **Cross-Platform**: Windows uses library detection, Linux/Raspberry Pi uses USB-level checks

### 7. Raspberry Pi Autostart
- Systemd service integration for automatic startup on boot
- Service management scripts for easy control
- Update scripts for seamless code deployment
- Development workflow support for local development and Pi testing

## Installation

### Prerequisites

**Windows:**
- Python 3.12 or higher
- LibUSB HIDAPI backend (hidapi.dll)
- Visual C++ Redistributable (if using pre-built packages)

**Linux/macOS:**
- Python 3.12 or higher
- ALSA/JACK MIDI support (for MIDI functionality)
- libusb development libraries

**Raspberry Pi:**
- Python 3.12 or higher
- ALSA MIDI support (built-in)

### Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd devdeck-main
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment:**
   - Windows: `venv\Scripts\activate`
   - Linux/macOS: `source venv/bin/activate`

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run setup script:**
   ```bash
   ./setup.sh  # Linux/macOS
   # or
   .\setup.sh  # Windows (Git Bash)
   ```

### First Run

On first run, DevDeck will:
1. **Validate USB Devices**: Check for Elgato Stream Deck and MIDI output devices
   - On Linux/Raspberry Pi: Validates via USB device detection (`lsusb`)
   - On Windows: Uses Stream Deck library and MIDI port enumeration
   - Exits with clear error messages if devices are missing
2. **Auto-Connect MIDI**: Automatically detects and connects to the first available hardware MIDI output port
   - Filters out virtual ports and "Midi Through" ports
   - Prefers ports with known MIDI device names (USB MIDI, CH345, etc.)
   - Logs connection status for troubleshooting
3. **Detect Stream Deck Devices**: Enumerate connected Stream Deck devices
4. **Generate Settings**: Create a default `config/settings.yml` file if none exists
5. **Populate Controls**: Add basic clock controls for each device

**Note**: Ensure the official Stream Deck application is closed before running DevDeck, as only one application can control a Stream Deck at a time.

**Device Detection Errors**: If you see errors about missing devices:
- **Elgato Stream Deck**: Verify USB connection and check with `lsusb | grep -i elgato` (Linux/Raspberry Pi)
- **MIDI Device**: Ensure MIDI adapter is connected and check with `lsusb | grep -i midi` (Linux/Raspberry Pi)

## Building and Installing

DevDeck uses modern Python packaging with `pyproject.toml`. You can build and install it as a package for system-wide use.

### Building the Package

**Build a source distribution:**
```bash
pip install build
python -m build
```

This creates distribution files in the `dist/` directory:
- `devdeck-X.X.X.tar.gz` - Source distribution
- `devdeck-X.X.X-py3-none-any.whl` - Wheel distribution

**Version Management:**
The package version is automatically determined from git tags using `setuptools-scm`. If no git tags exist, it falls back to version `0.1.0`.

### Installing as a Package

**Install in development mode (editable):**
```bash
pip install -e .
```

This installs the package in editable mode, so changes to the source code are immediately available without reinstalling.

**Install from source:**
```bash
pip install .
```

**Install from a built distribution:**
```bash
pip install dist/devdeck-*.whl
# or
pip install dist/devdeck-*.tar.gz
```

### Console Script

After installation, the `devdeck` console script will be available in your PATH:

```bash
devdeck
```

This is equivalent to running `python -m devdeck.main`.

### Package Metadata

The package is configured in `pyproject.toml` with:
- **Name**: `devdeck`
- **License**: MIT
- **Author**: James Ridgway
- **Homepage**: https://github.com/jamesridgway/devdeck
- **Dependencies**: All dependencies from `requirements.txt`
- **Console Script**: `devdeck = devdeck.main:main`

### Raspberry Pi Autostart

DevDeck can be configured to automatically start on boot using a systemd service. This is ideal for headless Raspberry Pi deployments.

#### Quick Setup

**Option 1: Automated Installation (Recommended)**

```bash
cd ~/devdeck
bash scripts/systemd/install-service.sh
```

This script will:
- Detect your username and project path automatically
- Create and install the systemd service file
- Enable autostart on boot
- Optionally start the service immediately

**Option 2: Manual Installation**

```bash
# Copy the service template
sudo cp scripts/systemd/devdeck.service /etc/systemd/system/devdeck.service

# Edit the service file (update username and paths)
sudo nano /etc/systemd/system/devdeck.service

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable devdeck.service
sudo systemctl start devdeck.service
```

#### Service Management

Use the provided management script for easy service control:

```bash
# Restart service
bash scripts/manage/manage-service.sh restart

# Toggle autostart on boot
bash scripts/manage/manage-service.sh toggle

# View logs in real-time
bash scripts/manage/manage-service.sh logs

# Check service status
bash scripts/manage/manage-service.sh status
```

**Useful Commands:**

You can also use systemctl commands directly:

```bash
# Start service
sudo systemctl start devdeck.service

# Stop service
sudo systemctl stop devdeck.service

# Restart service
sudo systemctl restart devdeck.service

# Check status
sudo systemctl status devdeck.service

# View logs
sudo journalctl -u devdeck.service -f
```

#### Updating Code

After making changes locally and pushing to git, update on Raspberry Pi:

```bash
cd ~/devdeck
bash scripts/update/update-devdeck.sh
```

This script will:
- Pull the latest code from git
- Warn about uncommitted changes
- Automatically restart the service

#### Viewing Logs Manually

To view service logs in a terminal window manually:

```bash
cd ~/devdeck
bash scripts/systemd/show-logs-terminal.sh
```

Or use the management script:

```bash
bash scripts/manage/manage-service.sh logs
```

For detailed Raspberry Pi deployment instructions, see [docs/RASPBERRY_PI_DEPLOYMENT.md](docs/RASPBERRY_PI_DEPLOYMENT.md).

## Configuration

### Settings File Location

The main settings file is located at:
- **Project-based**: `config/settings.yml` (for development)
- **User-based**: `~/.devdeck/settings.yml` (for installed packages)

### Settings Structure

```yaml
decks:
  - name: devdeck.decks.single_page_deck_controller.SinglePageDeckController
    serial_number: YOUR_SERIAL_NUMBER
    settings:
      controls:
        - key: 0
          name: devdeck.controls.clock_control.ClockControl
          settings: {}
        - key: 1
          name: devdeck.midi.controls.midi_control.MidiControl
          settings:
            type: cc
            control: 102
            value: 64
            channel: 0
            port: "MIDI Device"
```

### Key Mappings

Ketron key mappings can be imported from `config/key_mappings.json`:
- Maps Stream Deck key numbers to Ketron functions
- Supports SysEx commands for Ketron EVM/Event devices
- Automatically loaded on startup if present

## Built-in Controls

### General Controls

- **ClockControl** (`devdeck.controls.clock_control.ClockControl`)
  - Displays current date and time on deck keys
  - Auto-updates every second

- **CommandControl** (`devdeck.controls.command_control.CommandControl`)
  - Executes system commands on key press
  - Supports custom icons and command arguments

- **MicMuteControl** (`devdeck.controls.mic_mute_control.MicMuteControl`)
  - Toggles microphone mute state
  - Visual feedback for mute status

- **NameListControl** (`devdeck.controls.name_list_control.NameListControl`)
  - Cycles through a list of names/initials
  - Useful for stand-ups and team rotations

- **TimerControl** (`devdeck.controls.timer_control.TimerControl`)
  - Stopwatch functionality
  - Start/stop/reset operations

- **VolumeLevelControl** (`devdeck.controls.volume_level_control.VolumeLevelControl`)
  - Sets audio output volume to specific level
  - Platform-specific implementation (Windows/Linux)

- **VolumeMuteControl** (`devdeck.controls.volume_mute_control.VolumeMuteControl`)
  - Toggles audio output mute
  - Visual state indication

- **TextControl** (`devdeck.controls.text_control.TextControl`)
  - Displays custom text on keys
  - Configurable colors and fonts

- **NavigationToggleControl** (`devdeck.controls.navigation_toggle_control.NavigationToggleControl`)
  - Navigates between deck pages
  - Returns to previous deck

### MIDI Controls

- **MidiControl** (`devdeck.midi.controls.midi_control.MidiControl`)
  - Sends MIDI CC or SysEx messages
  - Configurable port, channel, and message data
  - **Visual Feedback**: Keys flash for 100ms after sending:
    - White background for successful sends
    - Red background with error message for failed sends
  - See [MIDI Support](#midi-support) for details

### Ketron Controls

- **KetronKeyMappingControl** (`devdeck.ketron.controls.ketron_key_mapping_control.KetronKeyMappingControl`)
  - Maps Stream Deck keys to Ketron functions
  - Reads mappings from `config/key_mappings.json`
  - Sends Ketron-specific SysEx messages (pedal, tab, and CC commands)
  - **Visual Feedback**: Keys flash for 100ms after sending MIDI messages:
    - White background for successful sends
    - Red background with error message for failed sends

## MIDI Support

### Overview

DevDeck includes comprehensive MIDI support through the `MidiManager` singleton and `MidiControl` class. The implementation uses `mido` with `python-rtmidi` backend for cross-platform compatibility.

### MIDI Manager

The `MidiManager` provides:
- Thread-safe MIDI port management
- Automatic port connection/disconnection
- **Automatic Hardware Port Connection**: `auto_connect_hardware_port()` method detects and connects to hardware MIDI devices at startup
- Support for multiple MIDI ports
- CC and SysEx message sending

### Visual Feedback

All MIDI controls provide immediate visual feedback when sending messages:

- **Successful Sends**: The key flashes with a **white background** for 100ms, confirming the message was sent successfully
- **Failed Sends**: The key flashes with a **red background** for 100ms, displaying an error message (e.g., "SEND\nFAILED")
- **Automatic Restoration**: After the flash, the key automatically returns to its original appearance

This feedback applies to:
- `MidiControl` for CC and SysEx messages
- `KetronKeyMappingControl` for pedal commands, tab commands, and CC messages

### Usage Examples

#### Control Change (CC) Message
```yaml
- key: 0
  name: devdeck.midi.controls.midi_control.MidiControl
  settings:
    type: cc
    control: 102  # CC number (0-127)
    value: 64     # CC value (0-127)
    channel: 0    # MIDI channel (0-15)
    port: "MIDI Device"  # Optional: specific port name
```

#### System Exclusive (SysEx) Message
```yaml
- key: 1
  name: devdeck.midi.controls.midi_control.MidiControl
  settings:
    type: sysex
    data: [0x43, 0x10, 0x4C, 0x00, 0x00, 0x7E, 0x00]  # SysEx data
    port: "MIDI Device"  # Optional
```

### MIDI Testing

See the [Testing](#testing) section for MIDI connectivity and functionality tests.

For detailed MIDI implementation information, see [docs/MIDI_IMPLEMENTATION.md](docs/MIDI_IMPLEMENTATION.md).

## Ketron Integration

### Overview

The Ketron integration provides specialized support for Ketron EVM and Event devices, including:
- Pre-formatted SysEx messages for Ketron commands
- Key mapping system for Stream Deck to Ketron function mapping
- Volume slider control via MIDI CC
- Color-coded button states matching Ketron UI

### Key Components

1. **KetronMidi** (`devdeck.ketron.ketron.py`)
   - SysEx message format constants
   - MIDI CC definitions for volume sliders
   - Color definitions for button states

2. **KetronVolumeManager** (`devdeck.ketron.ketron_volume_manager.py`)
   - Manages volume slider states
   - Sends MIDI CC messages for volume control

3. **KetronKeyMappingControl** (`devdeck.ketron.controls.ketron_key_mapping_control.py`)
   - Reads key mappings from JSON configuration
   - Sends appropriate Ketron SysEx or CC messages
   - Provides visual feedback on Stream Deck keys
   - Flashes keys with white (success) or red (failure) background for 100ms after each MIDI send

### Configuration

Ketron key mappings are defined in `config/key_mappings.json`:
```json
{
  "0": {
    "name": "Start/Stop",
    "sysex_command": "start_stop",
    "color": "green"
  },
  "1": {
    "name": "Intro",
    "sysex_command": "intro",
    "color": "blue"
  }
}
```

## Project Structure

```
devdeck-main/
├── config/                 # Configuration files
│   ├── key_mappings.json   # Ketron key mappings
│   └── settings.yml         # Main settings file
│
├── devdeck/                # Main package
│   ├── controls/           # General controls
│   ├── decks/              # Deck controllers
│   ├── ketron/             # Ketron integration
│   ├── midi/               # MIDI infrastructure
│   ├── settings/           # Settings management
│   └── main.py             # Entry point
│
├── docs/                   # Documentation
│   ├── MIDI_IMPLEMENTATION.md
│   ├── PROJECT_STRUCTURE.md
│   └── USER_GUIDE.md
│
├── scripts/                # Utility scripts
│   ├── check/              # Verification scripts
│   ├── generate/           # Code generation
│   ├── list/               # Listing utilities
│   ├── manage/             # Service management scripts
│   ├── run/                # Run scripts
│   ├── systemd/            # Systemd service files
│   └── update/             # Update scripts
│
└── tests/                  # Test suite
    └── devdeck/            # Package tests
```

For detailed structure information, see [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md).

## Development

### Setup Development Environment

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd devdeck-main
   ./setup.sh
   ```

2. **Activate virtual environment:**
   ```bash
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install development dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

**Development mode:**
```bash
python -m devdeck.main
```

**Using run scripts:**
```bash
./scripts/run/run-devdeck.sh  # Linux/macOS
.\scripts\run\run-devdeck.ps1  # Windows PowerShell
.\scripts\run\run-devdeck.bat  # Windows CMD
```

### Code Organization

- **Controls**: Inherit from `BaseDeckControl` (which extends `devdeck-core.DeckControl`)
- **Decks**: Implement `DeckController` interface from `devdeck-core`
- **Settings**: Use `DevDeckSettings` class for loading and validation
- **MIDI**: Use `MidiManager` singleton for all MIDI operations

### Adding New Controls

1. Create a new control class in `devdeck/controls/`:
   ```python
   from devdeck.controls.base_control import BaseDeckControl
   
   class MyControl(BaseDeckControl):
       def __init__(self, key_no, **kwargs):
           super().__init__(key_no, **kwargs)
           # Initialize your control
       
       def render(self):
           # Render your control
           pass
       
       def pressed(self):
           # Handle key press
           pass
   ```

2. Register in settings.yml:
   ```yaml
   - key: 0
     name: devdeck.controls.my_control.MyControl
     settings: {}
   ```

## Testing

### Running Tests

```bash
./scripts/run/run-tests.sh  # Linux/macOS
# or
python -m pytest tests/
```

### MIDI Testing

#### List MIDI Ports
```bash
python tests/list_midi_ports.py
```

#### Test MIDI Connectivity
```bash
python tests/devdeck/midi/test_midi.py
# or with specific port:
python tests/devdeck/midi/test_midi.py "MIDI Device Name"
```

#### Test Ketron SysEx
```bash
python tests/devdeck/ketron/test_ketron_sysex.py
# or with specific port:
python tests/devdeck/ketron/test_ketron_sysex.py "Ketron Port Name"
```

#### Check MIDI Identity
```bash
python scripts/check/check_app_midi_identity.py
```

### Test Coverage

The test suite includes:
- Control functionality tests
- MIDI connectivity and message formatting tests
- Ketron SysEx message tests
- Settings validation tests
- Deck manager tests

## Known Issues

### Clock Control Compatibility with Pillow 10.0.0+

**Issue**: Clock control may fail with `AttributeError: 'ImageDraw' object has no attribute 'textsize'` when using Pillow 10.0.0 or later.

**Fix**: Update `text_renderer.py` in the installed `devdeck-core` package to use `textbbox()` instead of `textsize()`.

**Windows Instructions**:
```powershell
# Find the file
Get-ChildItem -Path "venv\Lib\site-packages\devdeck_core\rendering\text_renderer.py" -Recurse

# Edit the file (replace python3.13 with your Python version if different)
notepad venv\Lib\site-packages\devdeck_core\rendering\text_renderer.py
```

**Linux/Raspberry Pi Instructions**:
```bash
# Find the file
find venv -name "text_renderer.py" -path "*/devdeck_core/*"

# Edit the file (replace python3.13 with your Python version)
nano venv/lib/python3.13/site-packages/devdeck_core/rendering/text_renderer.py
```

**Fix to Apply**:
Find this line (around line 258):
```python
label_w, label_h = draw.textsize('%s' % self.text, font=font)
```

Replace it with:
```python
# textsize() was deprecated and removed in Pillow 10.0.0, use textbbox() instead
bbox = draw.textbbox((0, 0), '%s' % self.text, font=font)
label_w = bbox[2] - bbox[0]  # right - left
label_h = bbox[3] - bbox[1]  # bottom - top
```

**Note**: This fix is applied to your local virtual environment. If you recreate the venv or reinstall `devdeck-core`, you'll need to reapply this fix. Consider submitting a patch to the `devdeck-core` project for a permanent solution.

### Windows: HIDAPI DLL Not Found

**Issue**: `ProbeError: No suitable LibUSB HIDAPI library found` even when `hidapi.dll` is in PATH.

**Fix**: Copy `hidapi.dll` to your Python Scripts directory:
```powershell
Copy-Item "C:\hidapi-win\x64\hidapi.dll" -Destination "venv\Scripts\hidapi.dll" -Force
```

### Stream Deck Application Conflict

**Issue**: Factory default images appear or devdeck controls don't work.

**Fix**: Close the official Stream Deck application completely before running devdeck. Only one application can control a Stream Deck at a time.

## Checking System Logs for Errors

When troubleshooting issues, especially on Raspberry Pi deployments, you may want to check the system logs for errors. Here are useful commands to check for errors in the logs:

### Check Wayvnc Service Status (Raspberry Pi)

**Check if Wayvnc is running:**
```bash
systemctl status wayvnc.service
```

This will show whether the Wayvnc VNC server is active and running on your Raspberry Pi.

### Check DevDeck Service Logs Since Last Boot

**View logs with errors only:**
```bash
sudo journalctl -u devdeck.service -b -p err -o cat
```

**View logs with warnings and errors:**
```bash
sudo journalctl -u devdeck.service -b -o cat | grep -i "error\|warning\|exception\|traceback\|failed"
```

**View all logs since last boot:**
```bash
bash scripts/manage/manage-service.sh logs-boot
```

**View last 50 lines with priority >= warning:**
```bash
sudo journalctl -u devdeck.service -n 50 -p warning -o cat
```

### Check for Specific Error Patterns

**Search for common error keywords:**
```bash
sudo journalctl -u devdeck.service -b -o cat | grep -E "(ERROR|CRITICAL|Exception|Traceback|Failed|failed)"
```

### Quick Status Check

**Check if the service is running:**
```bash
bash scripts/manage/manage-service.sh status
```

**Or directly:**
```bash
sudo systemctl status devdeck.service
```

**Note**: The `-o cat` flag suppresses journald's timestamp prefix, showing only the application's timestamp with millisecond precision (e.g., `2025-11-29 06:51:34,934`).

## Documentation

- **[USER_GUIDE.md](docs/USER_GUIDE.md)**: User documentation and usage examples
- **[MIDI_IMPLEMENTATION.md](docs/MIDI_IMPLEMENTATION.md)**: Detailed MIDI implementation guide
- **[PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)**: Project organization and file structure
- **[RASPBERRY_PI_DEPLOYMENT.md](docs/RASPBERRY_PI_DEPLOYMENT.md)**: Deployment guide for Raspberry Pi, including autostart setup and development workflow

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with appropriate tests
4. Ensure all tests pass
5. Submit a pull request

### Development Guidelines

- Follow existing code style and patterns
- Add tests for new functionality
- Update documentation as needed
- Use type hints where appropriate
- Follow the existing logging patterns

## License

See [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on [devdeck-core](https://github.com/jamesridgway/devdeck-core) by James Ridgway
- MIDI support via [mido](https://github.com/mido/mido) and [python-rtmidi](https://github.com/SpotlightKid/python-rtmidi)
- Stream Deck hardware support via [python-elgato-streamdeck](https://github.com/abcminiuser/python-elgato-streamdeck)
