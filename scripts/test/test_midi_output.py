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
        
        # Test 1: Send MIDI CC (Control Change) messages on channel 16
        print("Test 1: Sending MIDI CC (Control Change) Messages on Channel 16")
        print("-" * 70)
        midi_channel = 15  # Channel 16 (0-indexed: 15)
        print(f"Sending CC 102 (value 64) on channel 16...")
        if midi.send_cc(102, 64, midi_channel, port_name):
            print("  ✓ CC message sent successfully")
        else:
            print("  ✗ Failed to send CC message")
            return False
        
        time.sleep(0.5)
        
        print(f"Sending CC 102 (value 127) on channel 16...")
        if midi.send_cc(102, 127, midi_channel, port_name):
            print("  ✓ CC message sent successfully")
        else:
            print("  ✗ Failed to send CC message")
            return False
        
        time.sleep(0.5)
        
        print(f"Sending CC 102 (value 0) on channel 16...")
        if midi.send_cc(102, 0, midi_channel, port_name):
            print("  ✓ CC message sent successfully")
        else:
            print("  ✗ Failed to send CC message")
            return False
        
        print()
        
        # Test 2: Send MIDI Note messages on channel 4 with volume ramping (Upper) on channel 16
        print("Test 2: Sending MIDI Note Messages on Channel 4 with Volume Ramping (Upper) on Channel 16")
        print("-" * 70)
        # Send 40 different notes (C major scale extended across multiple octaves)
        # MIDI note numbers: C3=48 through A7=105 (extended C major scale)
        notes = [48, 50, 52, 53, 55, 57, 59, 60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81, 83, 84, 86, 88, 89, 91, 93, 95, 96, 98, 100, 101, 103, 105, 107, 108, 110, 112, 113, 115]
        note_names = ['C3', 'D3', 'E3', 'F3', 'G3', 'A3', 'B3', 'C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5', 'D5', 'E5', 'F5', 'G5', 'A5', 'B5', 'C6', 'D6', 'E6', 'F6', 'G6', 'A6', 'B6', 'C7', 'D7', 'E7', 'F7', 'G7', 'A7', 'B7', 'C8', 'D8', 'E8', 'F8', 'G8']
        
        # VOICE1_CC = 0x72 = 114 (volume control for upper/voice1 voices)
        VOICE1_CC = 0x72
        midi_channel_4 = 3   # Channel 4 (0-indexed: 3) for notes
        midi_channel_16 = 15 # Channel 16 (0-indexed: 15) for volume CC
        
        print(f"Sending {len(notes)} different notes on MIDI channel 4...")
        print("Ramping 'upper' volume CC (114) on channel 16 from 0 to 127 in steps of 16, then back down...")
        print()
        
        # Create volume ramp: 0, 16, 32, 48, 64, 80, 96, 112, 127, 112, 96, 80, 64, 48, 32, 16, 0
        volume_up = list(range(0, 128, 16))  # [0, 16, 32, 48, 64, 80, 96, 112]
        volume_up.append(127)  # Add 127 as max
        volume_down = list(reversed(volume_up[1:]))  # [112, 96, 80, 64, 48, 32, 16, 0] (skip 127 to avoid duplicate)
        volume_ramp = volume_up + volume_down  # [0, 16, 32, ..., 127, 112, 96, ..., 16, 0]
        
        # Calculate how many notes per volume step (distribute notes across volume ramp)
        notes_per_volume = max(1, len(notes) // len(volume_ramp))
        
        volume_index = 0
        for i, (note, note_name) in enumerate(zip(notes, note_names), 1):
            # Update volume at the start and periodically during the sequence
            if (i - 1) % notes_per_volume == 0 and volume_index < len(volume_ramp):
                volume = volume_ramp[volume_index]
                
                # Send volume CC (Upper/Voice1) on channel 16
                print(f"  [{i:2d}/{len(notes)}] Volume → {volume:3d} (CC 114 Upper, ch 16)...", end='', flush=True)
                if midi.send_cc(VOICE1_CC, volume, midi_channel_16, port_name):
                    print(" ✓", flush=True)
                else:
                    print(" ✗", flush=True)
                    return False
                
                volume_index += 1
                time.sleep(0.05)  # Brief delay after volume change
            
            # Send note on
            print(f"  [{i:2d}/{len(notes)}] Note On ({note_name}, note {note}, vel 100, ch 4)...", end='', flush=True)
            if midi.send_note_on(note, velocity=100, channel=midi_channel_4, port_name=port_name):
                print(" ✓", flush=True)
            else:
                print(" ✗", flush=True)
                return False
            
            time.sleep(0.2)  # Short delay between notes
        
        time.sleep(0.5)
        
        print(f"\nSending Note Off for all {len(notes)} notes...")
        for i, (note, note_name) in enumerate(zip(notes, note_names), 1):
            print(f"  [{i:2d}/{len(notes)}] Sending Note Off ({note_name}, note {note}, ch 4)...", end='', flush=True)
            if midi.send_note_off(note, velocity=0, channel=midi_channel_4, port_name=port_name):
                print(" ✓", flush=True)
            else:
                print(" ✗", flush=True)
                return False
            time.sleep(0.1)  # Short delay between note offs
        
        print()
        
        # Test 3: Send MIDI SysEx message (Ketron Start/Stop command) - DISABLED
        # Uncomment the section below to enable Start/Stop SysEx testing
        """
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
        sysex_off = [0x26, 0x79, 0x03, 0x12, 0x00]  # Manufacturer (2 bytes), Type, Start/Stop, OFF
        print(f"Sending Start/Stop OFF: F0 {' '.join([hex(b) for b in sysex_off])} F7")
        if midi.send_sysex(sysex_off, port_name):
            print("  ✓ Start/Stop OFF message sent successfully")
        else:
            print("  ✗ Failed to send Start/Stop OFF message")
            return False
        
        print()
        """
        
        print()
        
        # Test 4: Send multiple rapid messages on channel 16
        print("Test 4: Sending Multiple Rapid Messages on Channel 16")
        print("-" * 70)
        midi_channel = 15  # Channel 16 (0-indexed: 15)
        print("Sending 10 CC messages rapidly...")
        success_count = 0
        for i in range(10):
            if midi.send_cc(102, i * 12, midi_channel, port_name):
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

