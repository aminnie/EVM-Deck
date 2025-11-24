"""
Check what MIDI port name the application is using.

This script shows what port name your application opens, which is how
it appears in MIDI monitoring software on Windows.
"""

import sys
import os

# Add the project root to the path (two levels up from scripts/check/)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

try:
    from devdeck.midi import MidiManager
except ImportError as e:
    print(f"ERROR: Could not import MidiManager: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

def main():
    print("=" * 70)
    print("Application MIDI Identity Check")
    print("=" * 70)
    print()
    
    # Get MIDI manager instance
    midi = MidiManager()
    
    # List available ports
    print("Available MIDI Output Ports:")
    print("-" * 70)
    available_ports = midi.list_output_ports()
    if available_ports:
        for i, port in enumerate(available_ports, 1):
            print(f"  {i}. {port}")
    else:
        print("  No MIDI output ports available")
    print()
    
    # Try to open a port (simulating what the app does)
    print("Simulating Application Port Opening:")
    print("-" * 70)
    
    # Open port the same way the app does (no port name = auto-select)
    if midi.open_port(port_name=None, use_virtual=False):
        open_ports = midi.get_open_ports()
        if open_ports:
            print(f"[OK] Application opened port: {open_ports[0]}")
            print()
            print("This is how your application appears in MIDI monitoring software:")
            print(f"  → Port Name: '{open_ports[0]}'")
            print()
            
            # Get port info
            port_info = midi.get_port_info()
            if port_info:
                print("Port Information:")
                print(f"  - Name: {port_info.get('name', 'N/A')}")
                print(f"  - Is Virtual: {port_info.get('is_virtual', False)}")
                print(f"  - Closed: {port_info.get('closed', False)}")
            
            print()
            print("Note: On Windows, hardware MIDI ports show their driver/device name.")
            print("      To get a custom name like 'EVM Stream Deck Controller', you need")
            print("      to install a virtual MIDI driver like loopMIDI.")
            
            # Close the port
            midi.close_port()
        else:
            print("[ERROR] Port opened but no port names found")
    else:
        print("[ERROR] Failed to open MIDI port")
        print("  Check that MIDI devices are connected and available")
    
    print()
    print("=" * 70)

if __name__ == '__main__':
    main()

