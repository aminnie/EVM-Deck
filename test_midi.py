"""
Test MIDI connectivity by playing "Ode to Joy" melody.

This script tests the MIDI subsystem by playing a recognizable melody.
It can be run anytime to verify MIDI functionality.

Usage:
    python test_midi.py [port_name]
    
    If port_name is not specified, uses the first available MIDI port.
"""

import time
import sys
from pathlib import Path

# Add devdeck to path
sys.path.insert(0, str(Path(__file__).parent))

from devdeck.midi_manager import MidiManager


def test_connectivity(port_name=None):
    """
    Test MIDI connectivity with audible notes - plays "Ode to Joy" melody.
    
    Args:
        port_name: Name of the MIDI port to use. If None, uses the first available port.
    
    Returns:
        True if test completed successfully, False otherwise
    """
    print("=" * 60)
    print("MIDI Connectivity Test - Playing 'Ode to Joy'")
    print("=" * 60)
    
    try:
        # Get MIDI manager instance
        midi = MidiManager()
        
        # List available ports
        ports = midi.list_output_ports()
        if not ports:
            print("ERROR: No MIDI output ports available!")
            print("Please connect a MIDI device and try again.")
            return False
        
        print(f"\nAvailable MIDI ports: {ports}")
        
        # Open MIDI port
        if port_name is None:
            # Default to "MidiView 1" if available, otherwise use first available port
            if "MidiView 1" in ports:
                port_name = "MidiView 1"
                print(f"\nUsing default port: {port_name}")
            else:
                port_name = ports[0]
                print(f"\nUsing first available port: {port_name}")
        else:
            print(f"\nUsing specified port: {port_name}")
        
        if not midi.open_port(port_name):
            print(f"ERROR: Failed to open MIDI port: {port_name}")
            return False
        
        print(f"Successfully opened MIDI port: {port_name}")
        print("\nPlaying 'Ode to Joy' melody...")
        print("(Make sure your MIDI device is connected and volume is up)\n")
        
        # Notes for "Ode to Joy" - using MIDI note numbers
        # C4=60, D4=62, E4=64, F4=65, G4=67, A4=69, B4=71, C5=72
        notes = [64, 64, 65, 67, 67, 65, 64, 62, 60, 60, 62, 64, 64, 62, 62]
        durations = [0.4] * len(notes)
        
        # Note names for display
        note_names = ['E4', 'E4', 'F4', 'G4', 'G4', 'F4', 'E4', 'D4', 'C4', 
                     'C4', 'D4', 'E4', 'E4', 'D4', 'D4']
        
        # Play the melody
        for i, (note, duration, note_name) in enumerate(zip(notes, durations, note_names), 1):
            print(f"  [{i:2d}/{len(notes)}] Playing {note_name} (note {note}) for {duration:.2f}s", end='', flush=True)
            
            # Send Note On
            if not midi.send_note_on(note, velocity=120, channel=0):
                print(" - FAILED")
                return False
            
            # Wait for note duration
            time.sleep(duration)
            
            # Send Note Off
            if not midi.send_note_off(note, velocity=0, channel=0):
                print(" - FAILED")
                return False
            
            # Short pause between notes
            time.sleep(duration / 4)
            print(" - OK")
        
        print("\n" + "=" * 60)
        print("MIDI test completed successfully!")
        print("=" * 60)
        
        # Close the port
        midi.close_port(port_name)
        print(f"\nClosed MIDI port: {port_name}")
        
        return True
        
    except Exception as e:
        print(f"\nERROR: MIDI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    # Allow port name to be specified as command line argument
    port_name = None
    if len(sys.argv) > 1:
        port_name = sys.argv[1]
        print(f"Using port specified on command line: {port_name}\n")
    
    success = test_connectivity(port_name)
    sys.exit(0 if success else 1)

