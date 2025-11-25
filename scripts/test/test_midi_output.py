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
        print("Sending Note On (C4, velocity 100) on channel 0...")
        if midi.send_note_on(60, velocity=100, channel=0, port_name=port_name):
            print("  ✓ Note On message sent successfully")
        else:
            print("  ✗ Failed to send Note On message")
            return False
        
        time.sleep(0.5)
        
        print("Sending Note Off (C4) on channel 0...")
        if midi.send_note_off(60, velocity=0, channel=0, port_name=port_name):
            print("  ✓ Note Off message sent successfully")
        else:
            print("  ✗ Failed to send Note Off message")
            return False
        
        print()
        
        # Test 3: Send MIDI SysEx message
        print("Test 3: Sending MIDI SysEx Message")
        print("-" * 70)
        # Simple SysEx message (Universal Identity Request)
        sysex_data = [0xF0, 0x7E, 0x7F, 0x06, 0x01, 0xF7]
        print(f"Sending SysEx message: {[hex(b) for b in sysex_data]}")
        if midi.send_sysex(sysex_data, port_name):
            print("  ✓ SysEx message sent successfully")
        else:
            print("  ✗ Failed to send SysEx message")
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

