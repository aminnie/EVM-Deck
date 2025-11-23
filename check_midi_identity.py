"""
Utility script to check how the application appears in Windows MIDI system.

This script helps identify what name/identifier the application uses when
opening MIDI ports on Windows.
"""

import sys
import platform

try:
    import mido
    from mido import get_output_names
except ImportError:
    print("ERROR: mido library not installed. Install with: pip install mido python-rtmidi")
    sys.exit(1)

def check_midi_ports():
    """Check available MIDI output ports and their properties"""
    print("=" * 70)
    print("MIDI Port Information")
    print("=" * 70)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print()
    
    # Get available ports
    try:
        ports = get_output_names()
        print(f"Available MIDI Output Ports ({len(ports)}):")
        print("-" * 70)
        if ports:
            for i, port_name in enumerate(ports, 1):
                print(f"  {i}. {port_name}")
        else:
            print("  No MIDI output ports found")
        print()
    except Exception as e:
        print(f"ERROR: Could not list MIDI ports: {e}")
        return
    
    # Try to open a port and see what happens
    if ports:
        print("Testing Port Opening:")
        print("-" * 70)
        test_port = ports[0]
        print(f"Attempting to open: {test_port}")
        
        try:
            port = mido.open_output(test_port)
            print(f"✓ Successfully opened port: {test_port}")
            
            # Try to get port properties
            if hasattr(port, 'name'):
                print(f"  Port name: {port.name}")
            if hasattr(port, 'is_input'):
                print(f"  Is input: {port.is_input}")
            if hasattr(port, 'is_output'):
                print(f"  Is output: {port.is_output}")
            if hasattr(port, 'closed'):
                print(f"  Closed: {port.closed}")
            
            # Check backend information
            print(f"  Backend: {mido.backend}")
            if hasattr(mido.backend, 'name'):
                print(f"  Backend name: {mido.backend.name}")
            
            port.close()
            print("✓ Port closed successfully")
        except Exception as e:
            print(f"✗ Error opening port: {e}")
            import traceback
            traceback.print_exc()
    
    print()
    print("=" * 70)
    print("Windows MIDI Registry Information")
    print("=" * 70)
    print("To check Windows Registry for MIDI devices:")
    print("1. Open Registry Editor (regedit.exe)")
    print("2. Navigate to: HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Multimedia\\Sound Mapper")
    print("3. Look for MIDI device entries")
    print()
    print("Or use PowerShell:")
    print('  Get-ItemProperty "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Multimedia\\Sound Mapper"')
    print()
    
    print("=" * 70)
    print("MIDI Monitoring Software")
    print("=" * 70)
    print("To see how your application appears in MIDI monitoring software:")
    print("1. Open MidiView or similar MIDI monitor")
    print("2. Look for active MIDI connections")
    print("3. The application will appear with the port name it opens")
    print("4. On Windows, hardware ports show their driver name")
    print("   (e.g., 'MidiView 1' shows as the MidiView driver name)")
    print()

if __name__ == '__main__':
    check_midi_ports()


