"""
List all available MIDI output ports.

This script helps identify MIDI port names, including the Ketron EVM/Event port.

Usage:
    python list_midi_ports.py
"""

import sys
from pathlib import Path

# Add devdeck to path
sys.path.insert(0, str(Path(__file__).parent))

from devdeck.midi_manager import MidiManager


def list_ports():
    """List all available MIDI output ports"""
    print("=" * 60)
    print("Available MIDI Output Ports")
    print("=" * 60)
    
    try:
        midi = MidiManager()
        ports = midi.list_output_ports()
        
        if not ports:
            print("\nNo MIDI output ports found.")
            print("Make sure your MIDI device (e.g., Ketron EVM/Event) is connected and powered on.")
            return
        
        print(f"\nFound {len(ports)} MIDI port(s):\n")
        for i, port in enumerate(ports, 1):
            print(f"  {i}. {port}")
        
        print("\n" + "=" * 60)
        print("To use a specific port in your settings.yml, use:")
        print(f'  port: "{ports[0]}"')
        print("=" * 60)
        
        # Look for Ketron-related ports
        ketron_ports = [p for p in ports if 'ketron' in p.lower() and ('evm' in p.lower() or 'event' in p.lower())]
        if ketron_ports:
            print("\n⚠️  Possible Ketron EVM/Event port(s) found:")
            for port in ketron_ports:
                print(f"  → {port}")
        
    except Exception as e:
        print(f"Error listing MIDI ports: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    list_ports()

