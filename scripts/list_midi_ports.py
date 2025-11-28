"""
MIDI Port List Utility

This script lists available MIDI output ports using both direct mido access
and the MidiManager class, allowing you to compare what each method sees.
It also provides an interactive interface to select and test a MIDI port.

Usage:
    python scripts/list_midi_ports.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    import mido
except ImportError:
    print("Error: mido library not installed.")
    print("Install with: pip install mido python-rtmidi")
    sys.exit(1)

from devdeck.midi import MidiManager


def list_ports_direct_mido():
    """
    List MIDI output ports using direct mido access.
    
    Returns:
        List of port names, or None if error
    """
    try:
        return mido.get_output_names()
    except Exception as e:
        print(f"Error listing ports with direct mido: {e}")
        return None


def list_ports_midi_manager():
    """
    List MIDI output ports using MidiManager.
    
    Returns:
        List of port names, or None if error
    """
    try:
        midi = MidiManager()
        return midi.list_output_ports()
    except Exception as e:
        print(f"Error listing ports with MidiManager: {e}")
        return None


def compare_port_lists(mido_ports, manager_ports):
    """
    Compare two lists of MIDI ports and report differences.
    
    Args:
        mido_ports: List of ports from direct mido
        manager_ports: List of ports from MidiManager
    
    Returns:
        Dictionary with comparison results
    """
    mido_set = set(mido_ports) if mido_ports else set()
    manager_set = set(manager_ports) if manager_ports else set()
    
    only_mido = mido_set - manager_set
    only_manager = manager_set - mido_set
    common = mido_set & manager_set
    
    return {
        'only_mido': sorted(list(only_mido)),
        'only_manager': sorted(list(only_manager)),
        'common': sorted(list(common)),
        'identical': mido_set == manager_set
    }


def select_midi_output_port(port_list):
    """
    Lists available MIDI output ports and allows the user to select one.
    
    Args:
        port_list: List of port names to choose from
    
    Returns:
        The selected output port object, or None if no port is selected.
    """
    if not port_list:
        print("No MIDI output ports found.")
        return None
    
    print("\n" + "=" * 60)
    print("Available MIDI Output Ports:")
    print("=" * 60)
    for i, port_name in enumerate(port_list):
        print(f"{i}: {port_name}")
    
    while True:
        try:
            selection = input("\nEnter the number of the desired output port (or 'q' to quit): ")
            if selection.lower() == 'q':
                return None
            
            index = int(selection)
            if 0 <= index < len(port_list):
                selected_port_name = port_list[index]
                print(f"Selected port: {selected_port_name}")
                try:
                    return mido.open_output(selected_port_name)
                except Exception as e:
                    print(f"Error opening port: {e}")
                    return None
            else:
                print("Invalid selection. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number or 'q'.")


def get_backend_info():
    """Get information about the current mido backend."""
    try:
        backend = mido.backend
        backend_name = backend.__name__ if hasattr(backend, '__name__') else str(backend)
        return backend_name
    except Exception as e:
        return f"Unknown (error: {e})"


def main():
    """Main function to list and compare MIDI ports."""
    print("=" * 60)
    print("MIDI Port List Utility")
    print("=" * 60)
    
    # Get backend information
    backend_info = get_backend_info()
    print(f"\nCurrent mido backend: {backend_info}")
    
    # List ports using direct mido
    print("\n" + "-" * 60)
    print("Ports detected by direct mido.get_output_names():")
    print("-" * 60)
    mido_ports = list_ports_direct_mido()
    
    if mido_ports is None:
        print("Failed to list ports with direct mido.")
        return
    
    if not mido_ports:
        print("No MIDI output ports found via direct mido.")
    else:
        print(f"Found {len(mido_ports)} port(s):")
        for i, port in enumerate(mido_ports):
            print(f"  {i}: {port}")
    
    # List ports using MidiManager
    print("\n" + "-" * 60)
    print("Ports detected by MidiManager.list_output_ports():")
    print("-" * 60)
    manager_ports = list_ports_midi_manager()
    
    if manager_ports is None:
        print("Failed to list ports with MidiManager.")
        return
    
    if not manager_ports:
        print("No MIDI output ports found via MidiManager.")
    else:
        print(f"Found {len(manager_ports)} port(s):")
        for i, port in enumerate(manager_ports):
            print(f"  {i}: {port}")
    
    # Compare the two lists
    print("\n" + "-" * 60)
    print("Comparison:")
    print("-" * 60)
    comparison = compare_port_lists(mido_ports, manager_ports)
    
    if comparison['identical']:
        print("✓ Both methods see the same ports (identical lists)")
    else:
        print("⚠ Differences detected between the two methods:")
        
        if comparison['only_mido']:
            print(f"\n  Ports only seen by direct mido ({len(comparison['only_mido'])}):")
            for port in comparison['only_mido']:
                print(f"    - {port}")
        
        if comparison['only_manager']:
            print(f"\n  Ports only seen by MidiManager ({len(comparison['only_manager'])}):")
            for port in comparison['only_manager']:
                print(f"    - {port}")
        
        if comparison['common']:
            print(f"\n  Ports seen by both methods ({len(comparison['common'])}):")
            for port in comparison['common']:
                print(f"    - {port}")
    
    # Interactive port selection
    print("\n" + "=" * 60)
    print("Interactive Port Selection")
    print("=" * 60)
    print("\nSelect which port list to use for selection:")
    print("  1: Use ports from direct mido")
    print("  2: Use ports from MidiManager")
    print("  q: Quit without selecting")
    
    while True:
        choice = input("\nEnter choice (1, 2, or 'q'): ").strip().lower()
        
        if choice == 'q':
            print("Exiting without selecting a port.")
            return
        elif choice == '1':
            selected_port = select_midi_output_port(mido_ports)
            port_list_source = "direct mido"
            break
        elif choice == '2':
            selected_port = select_midi_output_port(manager_ports)
            port_list_source = "MidiManager"
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 'q'.")
    
    if selected_port:
        print(f"\n✓ Successfully opened MIDI output port via {port_list_source}: {selected_port.name}")
        print("\nYou can now send MIDI messages through this port.")
        print("Example:")
        print("  msg = mido.Message('note_on', note=60, velocity=64)")
        print("  selected_port.send(msg)")
        
        # Ask if user wants to test the port
        test = input("\nWould you like to send a test note? (y/n): ").strip().lower()
        if test == 'y':
            try:
                msg = mido.Message('note_on', note=60, velocity=64)
                selected_port.send(msg)
                print("✓ Sent test note (C4, velocity=64)")
                
                # Send note off after a moment
                import time
                time.sleep(0.1)
                msg_off = mido.Message('note_off', note=60, velocity=0)
                selected_port.send(msg_off)
                print("✓ Sent note off")
            except Exception as e:
                print(f"Error sending test message: {e}")
        
        # Close the port
        try:
            selected_port.close()
            print(f"\n✓ Closed MIDI output port: {selected_port.name}")
        except Exception as e:
            print(f"Warning: Error closing port: {e}")
    else:
        print("\nNo MIDI output port selected.")


if __name__ == "__main__":
    main()

