"""
Test Ketron Event detection using MIDI Universal System Exclusive Identity Request.

This script sends a MIDI Universal Identity Request message (F0 7E 7F 06 01 F7)
to all connected MIDI devices and listens for responses. It then parses the responses
to identify if a Ketron Event (or other Ketron device) is connected.

Usage:
    python tests/devdeck/ketron/test_ketron_identity.py [output_port_name]
    
    If output_port_name is not specified, uses the first available MIDI output port.
"""

import sys
import time
import threading
from pathlib import Path
from typing import List, Dict, Optional

# Add project root to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    import mido
    from mido import Message
except ImportError:
    print("ERROR: mido library not installed.")
    print("Install with: pip install mido python-rtmidi")
    sys.exit(1)


# MIDI Universal Identity Request message
# Format: F0 7E <device ID> 06 01 F7
# Device ID 7F = broadcast to all devices
IDENTITY_REQUEST = [0xF0, 0x7E, 0x7F, 0x06, 0x01, 0xF7]

# Known Ketron manufacturer IDs (SysEx manufacturer IDs)
# These are the first bytes after the identity response header
# Format: F0 7E <device ID> 06 02 <manufacturer ID> ...
KETRON_MANUFACTURER_IDS = [
    # Add known Ketron manufacturer IDs here
    # These are typically 1-3 bytes
    # Example: [0x43] for Yamaha, but we need Ketron's actual ID
    # For now, we'll look for "Ketron" in the device name from port listing
]


def parse_identity_response(data: List[int]) -> Optional[Dict[str, any]]:
    """
    Parse a MIDI Universal Identity Response message.
    
    Format: F0 7E <device ID> 06 02 <manufacturer ID> <family code> <family member code> <software revision> F7
    
    Args:
        data: List of bytes in the SysEx message (including F0 and F7)
    
    Returns:
        Dictionary with parsed information, or None if not a valid identity response
    """
    if len(data) < 6:
        return None
    
    # Check for identity response header: F0 7E <device ID> 06 02
    if data[0] != 0xF0 or data[1] != 0x7E or data[3] != 0x06 or data[4] != 0x02:
        return None
    
    if data[-1] != 0xF7:
        return None
    
    device_id = data[2]
    manufacturer_id_start = 5
    
    # Manufacturer ID can be 1 byte (0x00-0x7E) or 3 bytes (0x7F followed by 2 bytes)
    manufacturer_id = []
    if data[manufacturer_id_start] == 0x7F:
        # Extended manufacturer ID (3 bytes)
        if len(data) < manufacturer_id_start + 3:
            return None
        manufacturer_id = data[manufacturer_id_start:manufacturer_id_start + 3]
        family_code_start = manufacturer_id_start + 3
    else:
        # Standard manufacturer ID (1 byte)
        manufacturer_id = [data[manufacturer_id_start]]
        family_code_start = manufacturer_id_start + 1
    
    # Extract remaining fields if available
    remaining_data = data[family_code_start:-1]  # Exclude F7
    
    result = {
        'device_id': device_id,
        'manufacturer_id': manufacturer_id,
        'manufacturer_id_hex': ' '.join([f'{b:02X}' for b in manufacturer_id]),
        'raw_data': data,
        'raw_data_hex': ' '.join([f'{b:02X}' for b in data]),
    }
    
    # Add family code and member code if available
    if len(remaining_data) >= 2:
        result['family_code'] = remaining_data[0]
        result['family_member_code'] = remaining_data[1]
        if len(remaining_data) >= 3:
            result['software_revision'] = remaining_data[2]
    
    return result


def check_port_name_for_ketron(port_name: str) -> bool:
    """
    Check if a port name contains "Ketron" or "Event".
    
    Args:
        port_name: MIDI port name
    
    Returns:
        True if port name suggests it's a Ketron device
    """
    port_lower = port_name.lower()
    return 'ketron' in port_lower or 'event' in port_lower


def test_ketron_identity(output_port_name: Optional[str] = None, timeout: float = 2.0) -> bool:
    """
    Test for Ketron Event by sending MIDI Universal Identity Request.
    
    Args:
        output_port_name: Name of MIDI output port to use. If None, uses first available.
        timeout: Time to wait for responses (seconds)
    
    Returns:
        True if Ketron device was detected, False otherwise
    """
    print("=" * 70)
    print("Ketron Event Identity Detection Test")
    print("=" * 70)
    print("\nThis test sends a MIDI Universal Identity Request to detect")
    print("connected MIDI devices, specifically looking for Ketron Event.\n")
    
    # List available ports
    try:
        output_ports = mido.get_output_names()
        input_ports = mido.get_input_names()
    except Exception as e:
        print(f"ERROR: Failed to list MIDI ports: {e}")
        return False
    
    if not output_ports:
        print("ERROR: No MIDI output ports available!")
        print("Please connect a MIDI device and try again.")
        return False
    
    if not input_ports:
        print("ERROR: No MIDI input ports available!")
        print("Input port is needed to receive identity responses.")
        return False
    
    print(f"Available MIDI output ports: {output_ports}")
    print(f"Available MIDI input ports: {input_ports}\n")
    
    # Select output port
    if output_port_name is None:
        # Look for ports with "Ketron" or "Event" in the name
        ketron_ports = [p for p in output_ports if check_port_name_for_ketron(p)]
        if ketron_ports:
            output_port_name = ketron_ports[0]
            print(f"Found potential Ketron port: {output_port_name}")
        else:
            output_port_name = output_ports[0]
            print(f"Using first available output port: {output_port_name}")
    else:
        print(f"Using specified output port: {output_port_name}")
    
    # Use the same port name for input (most MIDI devices are bidirectional)
    input_port_name = None
    if output_port_name in input_ports:
        input_port_name = output_port_name
    else:
        # Try to find a matching input port
        for inp in input_ports:
            if check_port_name_for_ketron(inp) or output_port_name.lower() in inp.lower():
                input_port_name = inp
                break
        if input_port_name is None:
            input_port_name = input_ports[0]
    
    print(f"Using input port: {input_port_name}\n")
    
    # Open ports
    try:
        output_port = mido.open_output(output_port_name)
        input_port = mido.open_input(input_port_name)
    except Exception as e:
        print(f"ERROR: Failed to open MIDI ports: {e}")
        return False
    
    print(f"Opened output port: {output_port_name}")
    print(f"Opened input port: {input_port_name}\n")
    
    # Collect responses
    responses = []
    response_lock = threading.Lock()
    
    def receive_messages():
        """Thread function to receive MIDI messages"""
        try:
            for msg in input_port:
                if msg.type == 'sysex':
                    with response_lock:
                        responses.append(msg.data)
        except Exception as e:
            print(f"Error receiving messages: {e}")
    
    # Start receiving thread
    receive_thread = threading.Thread(target=receive_messages, daemon=True)
    receive_thread.start()
    
    # Send identity request
    print("Sending MIDI Universal Identity Request...")
    print(f"Message: {' '.join([f'{b:02X}' for b in IDENTITY_REQUEST])}\n")
    
    try:
        sysex_msg = Message('sysex', data=IDENTITY_REQUEST)
        output_port.send(sysex_msg)
        print("Identity request sent successfully.\n")
    except Exception as e:
        print(f"ERROR: Failed to send identity request: {e}")
        output_port.close()
        input_port.close()
        return False
    
    # Wait for responses
    print(f"Waiting {timeout} seconds for responses...\n")
    time.sleep(timeout)
    
    # Stop receiving (close port to stop the thread)
    input_port.close()
    
    # Parse responses
    with response_lock:
        num_responses = len(responses)
    
    print(f"Received {num_responses} SysEx message(s)\n")
    
    if num_responses == 0:
        print("=" * 70)
        print("RESULT: No identity responses received")
        print("=" * 70)
        print("\nPossible reasons:")
        print("  - Device is not connected or powered off")
        print("  - Device does not support MIDI Universal Identity Request")
        print("  - Wrong MIDI port selected")
        print("  - Device is not responding (try increasing timeout)")
        print("\nHowever, the device may still be connected.")
        print("Check port names above for 'Ketron' or 'Event' in the name.")
        output_port.close()
        return False
    
    # Parse and display responses
    ketron_found = False
    print("Identity Responses Received:")
    print("-" * 70)
    
    for i, response_data in enumerate(responses, 1):
        parsed = parse_identity_response(response_data)
        
        print(f"\nResponse {i}:")
        print(f"  Raw data: {' '.join([f'{b:02X}' for b in response_data])}")
        
        if parsed:
            print(f"  Device ID: {parsed['device_id']}")
            print(f"  Manufacturer ID: {parsed['manufacturer_id_hex']}")
            if 'family_code' in parsed:
                print(f"  Family Code: {parsed['family_code']}")
            if 'family_member_code' in parsed:
                print(f"  Family Member Code: {parsed['family_member_code']}")
            if 'software_revision' in parsed:
                print(f"  Software Revision: {parsed['software_revision']}")
            
            # Check if it might be a Ketron device
            # We'll check port names since we don't have Ketron's manufacturer ID
            if check_port_name_for_ketron(output_port_name) or check_port_name_for_ketron(input_port_name):
                print(f"  *** POTENTIAL KETRON DEVICE DETECTED ***")
                print(f"  (Based on port name containing 'Ketron' or 'Event')")
                ketron_found = True
        else:
            print(f"  (Could not parse as standard identity response)")
    
    print("\n" + "=" * 70)
    
    # Check port names for Ketron indicators
    port_based_detection = False
    if check_port_name_for_ketron(output_port_name) or check_port_name_for_ketron(input_port_name):
        port_based_detection = True
        print("Port Name Analysis:")
        print(f"  Output port '{output_port_name}' suggests Ketron device")
        print(f"  Input port '{input_port_name}' suggests Ketron device")
        ketron_found = True
    
    # Final result
    print("\n" + "=" * 70)
    if ketron_found:
        print("RESULT: ✓ Ketron Event (or Ketron device) DETECTED")
        print("=" * 70)
        print("\nThe device appears to be connected and responding.")
        if port_based_detection:
            print("Detection was based on port name containing 'Ketron' or 'Event'.")
        if num_responses > 0:
            print("Device responded to MIDI Universal Identity Request.")
    else:
        print("RESULT: ✗ Ketron Event NOT definitively detected")
        print("=" * 70)
        print("\nHowever, the device may still be connected.")
        print("Check the port names above - if you see 'Ketron' or 'Event',")
        print("the device is likely connected even if it didn't respond to")
        print("the identity request.")
    
    output_port.close()
    
    return ketron_found


if __name__ == '__main__':
    # Allow output port name to be specified as command line argument
    output_port_name = None
    if len(sys.argv) > 1:
        output_port_name = sys.argv[1]
        print(f"Using output port specified on command line: {output_port_name}\n")
    
    success = test_ketron_identity(output_port_name)
    sys.exit(0 if success else 1)

