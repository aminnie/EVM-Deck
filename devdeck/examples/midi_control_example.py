"""
Example usage of MIDI Control for sending CC and SysEx messages.

This example shows how to configure MIDI controls in your settings.yml file.
"""

# Example settings.yml configuration for MIDI controls:

EXAMPLE_CC_CONTROL = """
- key: 0
  name: devdeck.controls.midi_control.MidiControl
  settings:
    type: cc
    control: 102  # CC number (0-127)
    value: 64     # CC value (0-127)
    channel: 0    # MIDI channel (0-15, optional, default: 0)
    port: "MIDI Device"  # Optional: specific MIDI port name
    icon: "path/to/icon.png"  # Optional: icon file
"""

EXAMPLE_SYSEX_CONTROL = """
- key: 1
  name: devdeck.controls.midi_control.MidiControl
  settings:
    type: sysex
    data: [0x43, 0x10, 0x4C, 0x00, 0x00, 0x7E, 0x00]  # SysEx data (0xF0 and 0xF7 added automatically)
    port: "MIDI Device"  # Optional
    icon: "path/to/icon.png"  # Optional
"""

EXAMPLE_SYSEX_RAW_CONTROL = """
- key: 2
  name: devdeck.controls.midi_control.MidiControl
  settings:
    type: sysex
    raw_data: [0xF0, 0x43, 0x10, 0x4C, 0x00, 0x00, 0x7E, 0x00, 0xF7]  # Raw SysEx including 0xF0 and 0xF7
    port: "MIDI Device"  # Optional
"""

# Example: Using MidiManager programmatically
"""
from devdeck.midi_manager import MidiManager

# Get the singleton MIDI manager
midi = MidiManager()

# List available MIDI ports
ports = midi.list_output_ports()
print(f"Available ports: {ports}")

# Open a MIDI port
midi.open_port("MIDI Device")  # or None for first available

# Send a CC message
midi.send_cc(control=102, value=64, channel=0)

# Send a SysEx message
midi.send_sysex([0x43, 0x10, 0x4C, 0x00, 0x00, 0x7E, 0x00])

# Close the port when done
midi.close_port()
"""

