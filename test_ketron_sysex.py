"""
Test Ketron SysEx message formatting and sending.

This script tests the Ketron SysEx message formatting for pedal commands,
specifically testing the "Start/Stop" command.

Usage:
    python test_ketron_sysex.py [port_name]
"""

import sys
from pathlib import Path

# Add devdeck to path
sys.path.insert(0, str(Path(__file__).parent))

from devdeck.ketron import KetronMidi


def test_ketron_sysex(port_name=None):
    """
    Test Ketron SysEx message formatting and sending.
    
    Args:
        port_name: MIDI port name (optional, uses default if None)
    """
    print("=" * 60)
    print("Ketron SysEx Message Test")
    print("=" * 60)
    
    try:
        # Create KetronMidi instance
        ketron = KetronMidi()
        
        # Test formatting "Start/Stop" SysEx messages (ON and OFF)
        print("\n1. Formatting 'Start/Stop' SysEx messages (ON and OFF)...")
        try:
            sysex_on = ketron.format_pedal_sysex("Start/Stop", on_state=True)
            sysex_off = ketron.format_pedal_sysex("Start/Stop", on_state=False)
            print(f"   [OK] ON message (without F0/F7):  {[hex(b) for b in sysex_on]}")
            print(f"   [OK] ON message:  F0 {' '.join([hex(b) for b in sysex_on])} F7")
            print(f"   [OK] OFF message (without F0/F7): {[hex(b) for b in sysex_off]}")
            print(f"   [OK] OFF message: F0 {' '.join([hex(b) for b in sysex_off])} F7")
        except KeyError as e:
            print(f"   [ERROR] {e}")
            return False
        
        # Test sending the message
        print("\n2. Sending 'Start/Stop' SysEx message...")
        if port_name:
            print(f"   Using port: {port_name}")
        else:
            print("   Using default port (MidiView 1)")
            port_name = "MidiView 1"
        
        success = ketron.test_start_stop(port_name)
        
        if success:
            print("\n" + "=" * 60)
            print("Test completed successfully!")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("Test failed - check MIDI port connection")
            print("=" * 60)
        
        return success
        
    except Exception as e:
        print(f"\nERROR: Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    # Allow port name to be specified as command line argument
    port_name = None
    if len(sys.argv) > 1:
        port_name = sys.argv[1]
    
    success = test_ketron_sysex(port_name)
    sys.exit(0 if success else 1)

