# DevDeck

**Stream Deck control software for software developers with MIDI and Ketron EVM integration**

[![CI](https://github.com/jamesridgway/devdeck/workflows/CI/badge.svg?branch=main)](https://github.com/jamesridgway/devdeck/actions)

DevDeck is a Python-based control system for Elgato Stream Deck devices that enables developers to create custom button layouts and controls. The project extends the original devdeck with specialized MIDI support and Ketron EVM/Event device integration, making it ideal for musicians and audio professionals who need to control MIDI devices from their Stream Deck.

## Table of Contents

- [Quick Start](#quick-start)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Built-in Controls](#built-in-controls)
- [Development](#development)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Documentation](#documentation)

## Quick Start

1. **Prerequisites**: Python 3.12+, Elgato Stream Deck, MIDI output device
2. **Install**:
   ```bash
   git clone <repository-url>
   cd devdeck-main
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```
3. **Run**: `python -m devdeck.main` (starts with GUI by default)
4. **Configure**: Edit `config/settings.yml` (auto-generated on first run)

**Note**: The GUI control panel starts automatically. Use `--no-gui` flag to run without the GUI interface.

**Note**: Close the official Stream Deck application before running DevDeck, as only one application can control a Stream Deck at a time.

## Features

- **Multi-Device Support**: Manage multiple Stream Deck devices with independent configurations
- **MIDI Integration**: Send MIDI Control Change (CC) and System Exclusive (SysEx) messages
- **Ketron EVM Control**: Specialized integration for Ketron EVM/Event devices
- **GUI Control Panel**: Simple graphical interface for application control and MIDI monitoring
- **Visual Feedback**: Keys flash white (success) or red (failure) for 100ms after MIDI sends
- **Automatic Device Detection**: Validates USB devices and auto-connects to MIDI hardware ports
- **Extensible Architecture**: Plugin-based control system for custom functionality
- **Cross-Platform**: Works on Windows, Linux, macOS, and Raspberry Pi

## Installation

### Prerequisites

- **Python 3.12 or higher**
- **Windows**: LibUSB HIDAPI backend (hidapi.dll), Visual C++ Redistributable
- **Linux/macOS**: ALSA/JACK MIDI support, libusb development libraries
- **Raspberry Pi**: ALSA MIDI support (built-in)

### Setup

1. Clone the repository and navigate to the project directory
2. Create and activate a virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Run the setup script: `./setup.sh` (Linux/macOS) or `.\setup.sh` (Windows Git Bash)

### First Run

On first run, DevDeck will:
- Validate USB devices (Elgato Stream Deck and MIDI output device)
- Auto-connect to the first available hardware MIDI port
- Detect Stream Deck devices
- Generate default `config/settings.yml` if none exists
- Populate basic clock controls for each device

If devices are missing, DevDeck will exit with clear error messages. On Linux/Raspberry Pi, verify with:
- `lsusb | grep -i elgato` (Stream Deck)
- `lsusb | grep -i midi` (MIDI device)

### Package Installation

Install as a package for system-wide use:

```bash
# Development mode (editable)
pip install -e .

# Or from source
pip install .

# After installation, use the console script
devdeck
```

For Raspberry Pi autostart setup, see [RASPBERRY_PI_DEPLOYMENT.md](docs/RASPBERRY_PI_DEPLOYMENT.md).

## Configuration

### Settings File Location

- **Project-based**: `config/settings.yml` (for development)
- **User-based**: `~/.devdeck/settings.yml` (for installed packages)

### Basic Configuration Structure

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
            port: "MIDI Device"  # Optional
```

### Ketron Key Mappings

Ketron key mappings can be imported from `config/key_mappings.json` and are automatically loaded on startup if present.

For detailed configuration examples, see [USER_GUIDE.md](docs/USER_GUIDE.md).

## GUI Control Panel

DevDeck includes a simple graphical user interface that provides:

### Application Control
- **Start/Stop/Restart Buttons**: Control the DevDeck application lifecycle
- **Status Indicator**: Visual feedback showing application state (Running/Stopped)
- **Thread-Safe Operation**: Application runs in a separate thread, keeping the GUI responsive

### MIDI Monitoring
- **Key Press Monitor**: Real-time display of MIDI Note ON/OFF messages
- **Scrolling Log**: Shows the last ~50 MIDI key events with timestamps
- **Start/Stop Monitoring**: Toggle MIDI input monitoring on demand
- **Message Details**: Displays note number, velocity, and MIDI channel for each key press

### Device Information
- **MIDI Input Display**: Shows all connected MIDI input devices
- **MIDI Output Display**: Shows connected MIDI output devices (highlights currently open ports)
- **Refresh Button**: Update device list without restarting

### Usage

```bash
# Start with GUI (default)
python -m devdeck.main

# Start without GUI
python -m devdeck.main --no-gui
```

The GUI is built with tkinter (included with Python) and works on macOS, Raspberry Pi, and other platforms with Python GUI support.

## Built-in Controls

### General Controls

- **ClockControl**: Displays current date and time (auto-updates every second)
- **CommandControl**: Executes system commands on key press
- **TextControl**: Displays custom text with configurable colors and fonts
- **TimerControl**: Stopwatch with start/stop/reset operations
- **NameListControl**: Cycles through a list of names/initials
- **NavigationToggleControl**: Navigates between deck pages
- **MicMuteControl**: Toggles microphone mute (Linux/PulseAudio)
- **VolumeLevelControl**: Sets audio output volume to specific level
- **VolumeMuteControl**: Toggles audio output mute

### MIDI Controls

- **MidiControl**: Sends MIDI CC or SysEx messages with visual feedback
- **KetronKeyMappingControl**: Maps Stream Deck keys to Ketron functions via SysEx

All MIDI controls provide visual feedback: keys flash white (100ms) for successful sends, red (100ms) for failures.

For detailed control documentation and examples, see [USER_GUIDE.md](docs/USER_GUIDE.md).

## Development

### Setup

```bash
git clone <repository-url>
cd devdeck-main
./setup.sh
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

### Running

```bash
# Development mode (with GUI by default)
python -m devdeck.main

# Without GUI
python -m devdeck.main --no-gui

# Or use run scripts
./scripts/run/run-devdeck.sh  # Linux/macOS
.\scripts\run\run-devdeck.ps1  # Windows PowerShell
```

### Code Organization

- **Controls**: Inherit from `BaseDeckControl` (extends `devdeck-core.DeckControl`)
- **Decks**: Implement `DeckController` interface from `devdeck-core`
- **Settings**: Use `DevDeckSettings` class for loading and validation
- **MIDI**: Use `MidiManager` singleton for all MIDI operations

### Adding New Controls

1. Create a control class in `devdeck/controls/` inheriting from `BaseDeckControl`
2. Implement `render()` and `pressed()` methods
3. Register in `settings.yml` with the full class path

See [USER_GUIDE.md](docs/USER_GUIDE.md) for detailed examples.

## Testing

### Running Tests

```bash
./scripts/run/run-tests.sh  # Linux/macOS
# or
python -m pytest tests/
```

### MIDI Testing

```bash
# List available MIDI ports
python tests/list_midi_ports.py

# Test MIDI connectivity
python tests/devdeck/midi/test_midi.py [port_name]

# Test Ketron SysEx
python tests/devdeck/ketron/test_ketron_sysex.py [port_name]

# Check MIDI identity
python scripts/check/check_app_midi_identity.py
```

## Troubleshooting

### Stream Deck Application Conflict

**Issue**: Factory default images appear or controls don't work.

**Fix**: Close the official Stream Deck application completely. Only one application can control a Stream Deck at a time.

### Windows: HIDAPI DLL Not Found

**Issue**: `ProbeError: No suitable LibUSB HIDAPI library found` even when `hidapi.dll` is in PATH.

**Fix**: Copy `hidapi.dll` to your Python Scripts directory:
```powershell
Copy-Item "C:\hidapi-win\x64\hidapi.dll" -Destination "venv\Scripts\hidapi.dll" -Force
```

### Device Detection Errors

**Elgato Stream Deck not detected**:
- Verify USB connection
- On Linux/Raspberry Pi: `lsusb | grep -i elgato`
- On Windows: Check device manager

**MIDI device not detected**:
- Ensure MIDI adapter is connected
- On Linux/Raspberry Pi: `lsusb | grep -i midi`
- Check MIDI port availability: `python tests/list_midi_ports.py`

### Checking Logs (Raspberry Pi)

For service logs on Raspberry Pi:
```bash
# View logs with errors
sudo journalctl -u devdeck.service -b -p err -o cat

# View all logs since last boot
bash scripts/manage/manage-service.sh logs-boot

# Check service status
bash scripts/manage/manage-service.sh status
```

For more troubleshooting information, see [USER_GUIDE.md](docs/USER_GUIDE.md) and [RASPBERRY_PI_DEPLOYMENT.md](docs/RASPBERRY_PI_DEPLOYMENT.md).

## Documentation

- **[USER_GUIDE.md](docs/USER_GUIDE.md)**: Complete user documentation with control examples and usage
- **[MIDI_IMPLEMENTATION.md](docs/MIDI_IMPLEMENTATION.md)**: Detailed MIDI implementation guide
- **[PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)**: Project organization and file structure
- **[RASPBERRY_PI_DEPLOYMENT.md](docs/RASPBERRY_PI_DEPLOYMENT.md)**: Complete Raspberry Pi deployment guide including autostart setup

## Technical Architecture

DevDeck uses a modular architecture:

- **Deck Manager**: Centralized management of Stream Deck devices and controllers
- **Control System**: Plugin-based controls inheriting from `BaseDeckControl`
- **MIDI Manager**: Thread-safe singleton for MIDI port management with automatic connection
- **Settings System**: YAML-based configuration with Cerberus schema validation
- **Deck Stack**: Navigation between decks using a stack-based approach

**Technology Stack**: Python 3.12+, devdeck-core 1.0.7, mido + python-rtmidi, PyYAML, Cerberus, Pillow (<10.0.0), pulsectl (Linux)

For detailed architecture information, see [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md).

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
