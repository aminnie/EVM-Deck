"""
Test MIDI Output - Verify MIDI messages are leaving the Raspberry Pi.

This script sends various MIDI messages to test if MIDI traffic is actually
leaving the Raspberry Pi through the USB MIDI interface.

Usage:
    python3 scripts/test/test_midi_output.py [port_name]
    
    If port_name is not specified, lists available ports and uses the first one.
"""

import sys
import os
import time

# Add project root to path (three levels up from scripts/test/)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from devdeck.midi import MidiManager


def test_midi_output(port_name=None):
    """
    Test MIDI output by sending various MIDI messages.
    
    Args:
        port_name: Name of the MIDI port to use. If None, uses the first available port.
    
    Returns:
        True if test completed successfully, False otherwise
    """
    print("=" * 70)
    print("MIDI Output Test - Verify MIDI Traffic Leaving Raspberry Pi")
    print("=" * 70)
    print()
    
    try:
        # Get MIDI manager instance
        midi = MidiManager()
        
        # List available ports
        ports = midi.list_output_ports()
        if not ports:
            print("ERROR: No MIDI output ports available!")
            print("Please connect a USB MIDI interface and try again.")
            return False
        
        print("Available MIDI Output Ports:")
        print("-" * 70)
        for i, port in enumerate(ports, 1):
            print(f"  {i}. {port}")
        print()
        
        # Select port
        if port_name is None:
            port_name = ports[0]
            print(f"Using first available port: {port_name}")
        else:
            if port_name not in ports:
                print(f"ERROR: Port '{port_name}' not found in available ports!")
                return False
            print(f"Using specified port: {port_name}")
        
        print()
        print("-" * 70)
        
        # Open MIDI port
        if not midi.open_port(port_name):
            print(f"ERROR: Failed to open MIDI port: {port_name}")
            return False
        
        print(f"✓ Successfully opened MIDI port: {port_name}")
        print()
        
        # Test 1: Send MIDI CC (Control Change) messages
        print("Test 1: Sending MIDI CC (Control Change) Messages")
        print("-" * 70)
        print("Sending CC 102 (value 64) on channel 0...")
        if midi.send_cc(102, 64, 0, port_name):
            print("  ✓ CC message sent successfully")
        else:
            print("  ✗ Failed to send CC message")
            return False
        
        time.sleep(0.5)
        
        print("Sending CC 102 (value 127) on channel 0...")
        if midi.send_cc(102, 127, 0, port_name):
            print("  ✓ CC message sent successfully")
        else:
            print("  ✗ Failed to send CC message")
            return False
        
        time.sleep(0.5)
        
        print("Sending CC 102 (value 0) on channel 0...")
        if midi.send_cc(102, 0, 0, port_name):
            print("  ✓ CC message sent successfully")
        else:
            print("  ✗ Failed to send CC message")
            return False
        
        print()
        
        # Test 2: Send MIDI Note messages
        print("Test 2: Sending MIDI Note Messages")
        print("-" * 70)
        # Send 10 different notes (C major scale: C, D, E, F, G, A, B, C, D, E)
        # MIDI note numbers: C4=60, D4=62, E4=64, F4=65, G4=67, A4=69, B4=71, C5=72, D5=74, E5=76
        notes = [60, 62, 64, 65, 67, 69, 71, 72, 74, 76]
        note_names = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5', 'D5', 'E5']
        
        print(f"Sending {len(notes)} different notes...")
        for i, (note, note_name) in enumerate(zip(notes, note_names), 1):
            print(f"  [{i:2d}/{len(notes)}] Sending Note On ({note_name}, note {note}, velocity 100)...", end='', flush=True)
            if midi.send_note_on(note, velocity=100, channel=0, port_name=port_name):
                print(" ✓", flush=True)
            else:
                print(" ✗", flush=True)
                return False
            
            time.sleep(0.2)  # Short delay between notes
        
        time.sleep(0.5)
        
        print(f"Sending Note Off for all {len(notes)} notes...")
        for i, (note, note_name) in enumerate(zip(notes, note_names), 1):
            print(f"  [{i:2d}/{len(notes)}] Sending Note Off ({note_name}, note {note})...", end='', flush=True)
            if midi.send_note_off(note, velocity=0, channel=0, port_name=port_name):
                print(" ✓", flush=True)
            else:
                print(" ✗", flush=True)
                return False
            time.sleep(0.1)  # Short delay between note offs
        
        print()
        
        # Test 3: Send MIDI SysEx message (Ketron Start/Stop command)
        print("Test 3: Sending MIDI SysEx Message (Ketron Start/Stop)")
        print("-" * 70)
        # Ketron SysEx format for Start/Stop pedal command (based on CircuitPython implementation):
        # Format: F0 26 79 [0x03] [command_byte] [state_value] F7
        # Manufacturer ID: 0x26, 0x79 (2-byte manufacturer ID for pedals)
        # First data byte: 0x03 (pedal command type)
        # Start/Stop pedal value: 0x12 (18)
        # ON state: 0x7F (127), OFF state: 0x00 (0)
        
        # Send Start/Stop ON message
        # Note: send_sysex() expects data WITHOUT 0xF0 and 0xF7
        sysex_on = [0x26, 0x79, 0x03, 0x12, 0x7F]  # Manufacturer (2 bytes), Type, Start/Stop, ON
        print(f"Sending Start/Stop ON: F0 {' '.join([hex(b) for b in sysex_on])} F7")
        if midi.send_sysex(sysex_on, port_name):
            print("  ✓ Start/Stop ON message sent successfully")
        else:
            print("  ✗ Failed to send Start/Stop ON message")
            return False
        
        time.sleep(0.5)  # Delay between ON and OFF (simulates key press duration)
        
        # Send Start/Stop OFF message
        sysex_off = [0x43, 0x00, 0x12, 0x00]  # Manufacturer, Device, Start/Stop, OFF
        print(f"Sending Start/Stop OFF: F0 {' '.join([hex(b) for b in sysex_off])} F7")
        if midi.send_sysex(sysex_off, port_name):
            print("  ✓ Start/Stop OFF message sent successfully")
        else:
            print("  ✗ Failed to send Start/Stop OFF message")
            return False
        
        print()
        
        # Test 4: Send multiple rapid messages
        print("Test 4: Sending Multiple Rapid Messages")
        print("-" * 70)
        print("Sending 10 CC messages rapidly...")
        success_count = 0
        for i in range(10):
            if midi.send_cc(102, i * 12, 0, port_name):
                success_count += 1
            time.sleep(0.1)
        
        print(f"  ✓ Sent {success_count}/10 messages successfully")
        
        print()
        print("=" * 70)
        print("MIDI Output Test Completed!")
        print("=" * 70)
        print()
        print("IMPORTANT: To verify MIDI is actually leaving the Raspberry Pi:")
        print("  1. Connect a MIDI monitor (like MidiView on Windows) to the USB MIDI interface")
        print("  2. Or connect the MIDI interface to a MIDI device and check if it responds")
        print("  3. Or use 'aseqdump' to monitor MIDI traffic:")
        print(f"     aseqdump -p '{port_name}'")
        print()
        
        # Close the port
        midi.close_port(port_name)
        print(f"Closed MIDI port: {port_name}")
        
        return True
        
    except Exception as e:
        print(f"\nERROR: MIDI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    # Allow port name to be specified as command line argument
    port_name = sys.argv[1] if len(sys.argv) > 1 else None
    
    success = test_midi_output(port_name)
    sys.exit(0 if success else 1)

