# MIDI Implementation Guide

This document describes the MIDI implementation added to the devdeck application, including support for Control Change (CC) and System Exclusive (SysEx) messages.

## Overview

The MIDI implementation consists of two main components:

1. **MidiManager** (`devdeck/midi_manager.py`): A singleton service that manages MIDI port connections and provides methods to send MIDI messages.
2. **MidiControl** (`devdeck/controls/midi_control.py`): A deck control that can be configured to send CC or SysEx messages when a key is pressed.

## Dependencies

The implementation uses the following Python libraries:

- **mido**: High-level MIDI library for Python
- **python-rtmidi**: Cross-platform MIDI backend (works on Windows, Linux, macOS, and Raspberry Pi)

These are automatically installed when you install the project dependencies:

```bash
pip install -r requirements.txt
```

## Cross-Platform Compatibility

The implementation is designed to work on:
- **Windows**: Uses rtmidi backend with Windows MIDI support
- **Linux**: Uses rtmidi backend with ALSA/JACK support
- **Raspberry Pi 5**: Uses rtmidi backend with ALSA support (no special configuration needed)

The `mido` library with `python-rtmidi` backend automatically detects and uses the appropriate MIDI system for each platform.

## Usage

### Using MidiControl in settings.yml

#### Example 1: Send a MIDI CC Message

```yaml
- key: 0
  name: devdeck.midi.controls.midi_control.MidiControl
  settings:
    type: cc
    control: 102  # CC number (0-127)
    value: 64    # CC value (0-127)
    channel: 0   # MIDI channel (0-15, optional, default: 0)
    port: "MIDI Device"  # Optional: specific MIDI port name
    icon: "path/to/icon.png"  # Optional: icon file
```

#### Example 2: Send a SysEx Message

```yaml
- key: 1
  name: devdeck.midi.controls.midi_control.MidiControl
  settings:
    type: sysex
    data: [0x43, 0x10, 0x4C, 0x00, 0x00, 0x7E, 0x00]  # SysEx data (0xF0 and 0xF7 added automatically)
    port: "MIDI Device"  # Optional
```

#### Example 3: Send a Raw SysEx Message

```yaml
- key: 2
  name: devdeck.midi.controls.midi_control.MidiControl
  settings:
    type: sysex
    raw_data: [0xF0, 0x43, 0x10, 0x4C, 0x00, 0x00, 0x7E, 0x00, 0xF7]  # Raw SysEx including 0xF0 and 0xF7
    port: "MIDI Device"  # Optional
```

### Using MidiManager Programmatically

You can also use the MidiManager directly in your code:

```python
from devdeck.midi import MidiManager

# Get the singleton MIDI manager
midi = MidiManager()

# List available MIDI ports
ports = midi.list_output_ports()
print(f"Available ports: {ports}")

# Open a MIDI port (uses first available if None)
midi.open_port("MIDI Device")  # or None for first available

# Send a CC message
midi.send_cc(control=102, value=64, channel=0)

# Send a SysEx message
midi.send_sysex([0x43, 0x10, 0x4C, 0x00, 0x00, 0x7E, 0x00])

# Close the port when done
midi.close_port()
```

## MidiControl Settings

### Required Settings

- **type**: Either `'cc'` or `'sysex'` (required)

### For CC Messages (type='cc')

- **control**: CC number (0-127, required)
- **value**: CC value (0-127, required)
- **channel**: MIDI channel (0-15, optional, default: 0)

### For SysEx Messages (type='sysex')

Either:
- **data**: List of bytes (0-127) for SysEx message (0xF0 and 0xF7 are added automatically)
- OR
- **raw_data**: List of bytes including 0xF0 at start and 0xF7 at end

### Optional Settings

- **port**: MIDI port name. If not specified, uses the first available port
- **icon**: Path to icon file for the key display

## MidiManager API

### Methods

- `list_output_ports()`: Returns a list of available MIDI output port names
- `open_port(port_name=None)`: Opens a MIDI output port. If `port_name` is None, opens the first available port
- `close_port(port_name=None)`: Closes a MIDI port. If `port_name` is None, closes all ports
- `send_cc(control, value, channel=0, port_name=None)`: Sends a MIDI CC message
- `send_sysex(data, port_name=None)`: Sends a MIDI SysEx message (data should not include 0xF0/0xF7)
- `send_sysex_raw(raw_data, port_name=None)`: Sends a raw SysEx message (includes 0xF0 and 0xF7)
- `is_port_open(port_name=None)`: Checks if a MIDI port is open

## Error Handling

The implementation includes comprehensive error handling:

- If `mido` or `python-rtmidi` are not installed, the MIDI functionality gracefully degrades with warning messages
- Invalid MIDI parameters are validated and logged
- Port connection errors are caught and logged
- The control displays error messages on the deck key if MIDI operations fail

## Thread Safety

The MidiManager is thread-safe and can be used from multiple controls simultaneously. All port operations are protected by locks.

## Integration with Ketron

The MIDI implementation works seamlessly with the existing Ketron MIDI mappings in `devdeck/ketron.py`. You can use the MidiControl to send the MIDI messages defined in the KetronMidi class.

## Testing on Raspberry Pi 5

To test on Raspberry Pi 5:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Connect your MIDI device (USB MIDI interface or hardware)

3. List available MIDI ports:
   ```python
   from devdeck.midi import MidiManager
   midi = MidiManager()
   print(midi.list_output_ports())
   ```

4. Configure your MIDI controls in `settings.yml` as shown above

5. Run the application:
   ```bash
   python -m devdeck.main
   ```

The implementation should work without any special configuration on Raspberry Pi 5, as it uses the standard ALSA MIDI system that's available on Linux.

## Troubleshooting

### No MIDI ports available

- Ensure your MIDI device is connected and recognized by the system
- On Linux/Raspberry Pi, check with: `aconnect -l` or `amidi -l`
- On Windows, check Device Manager for MIDI devices

### MIDI messages not being sent

- Check that the MIDI port is open (the control will attempt to open it automatically)
- Verify the MIDI port name matches exactly (case-sensitive on some systems)
- Check the application logs for error messages
- Ensure the MIDI device is not being used by another application

### Import errors

- Ensure `mido` and `python-rtmidi` are installed: `pip install mido python-rtmidi`
- On Raspberry Pi, you may need to install system dependencies:
  ```bash
  sudo apt-get install libasound2-dev libjack-dev
  ```

