"""
Test USB device detection and control using pyusb library.

This test module uses the pyusb library to detect and interact with USB devices.
It is particularly useful for testing USB device detection on macOS systems like
the Mac Mini, where traditional methods (like lsusb) may not be available.

Reference documentation:
https://www.pythonhelp.org/tutorials/how-to-control-usb-port/

Usage:
    python tests/devdeck/usb/test_usb_devices.py

The test will:
1. List all connected USB devices
2. Display vendor and product IDs for each device
3. Test basic USB device detection capabilities
"""

import sys
from pathlib import Path

# Add project root to path to allow imports
# Path is now: tests/devdeck/usb/test_usb_devices.py
# Need to go up 5 levels to get to project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

try:
    import usb.core
    import usb.util
    PYUSB_AVAILABLE = True
except ImportError:
    PYUSB_AVAILABLE = False
    print("ERROR: pyusb library not installed. Install it with: pip install pyusb")


def list_usb_devices():
    """
    List all connected USB devices.
    
    Based on the method from:
    https://www.pythonhelp.org/tutorials/how-to-control-usb-port/
    
    Returns:
        List of USB device objects, or empty list if pyusb is not available.
    """
    if not PYUSB_AVAILABLE:
        print("ERROR: pyusb library not available")
        return []
    
    try:
        # Find all connected USB devices
        devices = usb.core.find(find_all=True)
        
        device_list = []
        for device in devices:
            try:
                vendor_id = device.idVendor
                product_id = device.idProduct
                device_list.append({
                    'device': device,
                    'vendor_id': vendor_id,
                    'product_id': product_id,
                    'vendor_id_hex': f"0x{vendor_id:04x}",
                    'product_id_hex': f"0x{product_id:04x}"
                })
            except Exception as e:
                print(f"Warning: Could not read device info: {e}")
                continue
        
        return device_list
    
    except Exception as e:
        print(f"ERROR: Failed to list USB devices: {e}")
        import traceback
        traceback.print_exc()
        return []


def print_device_info(device_info):
    """
    Print information about a USB device.
    
    Args:
        device_info: Dictionary containing device information
    """
    print(f"  Device: {device_info['vendor_id_hex']}:{device_info['product_id_hex']} "
          f"(Vendor: {device_info['vendor_id']}, Product: {device_info['product_id']})")


def test_detect_usb_devices():
    """
    Test detecting USB devices.
    
    Based on the method from:
    https://www.pythonhelp.org/tutorials/how-to-control-usb-port/
    
    Returns:
        True if test completed successfully, False otherwise
    """
    print("=" * 60)
    print("USB Device Detection Test using pyusb")
    print("=" * 60)
    print("\nReference: https://www.pythonhelp.org/tutorials/how-to-control-usb-port/")
    print()
    
    if not PYUSB_AVAILABLE:
        print("ERROR: pyusb library not installed")
        print("Install it with: pip install pyusb")
        return False
    
    try:
        print("Scanning for USB devices...")
        devices = list_usb_devices()
        
        if not devices:
            print("No USB devices found or unable to access USB devices.")
            print("\nPossible reasons:")
            print("  - No USB devices connected")
            print("  - Insufficient permissions (try running with sudo on Linux/macOS)")
            print("  - USB backend not properly configured")
            return False
        
        print(f"\nFound {len(devices)} USB device(s):\n")
        
        for i, device_info in enumerate(devices, 1):
            print(f"Device {i}:")
            print_device_info(device_info)
            print()
        
        print("=" * 60)
        print("USB device detection test completed successfully!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\nERROR: USB device detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_find_specific_device(vendor_id=None, product_id=None):
    """
    Test finding a specific USB device by vendor and product ID.
    
    Based on the method from:
    https://www.pythonhelp.org/tutorials/how-to-control-usb-port/
    
    Args:
        vendor_id: Vendor ID in hex format (e.g., 0x1234) or None to skip
        product_id: Product ID in hex format (e.g., 0x5678) or None to skip
    
    Returns:
        True if device found, False otherwise
    """
    if not PYUSB_AVAILABLE:
        print("ERROR: pyusb library not available")
        return False
    
    if vendor_id is None or product_id is None:
        print("Skipping specific device test (vendor_id and product_id required)")
        return True
    
    try:
        print(f"\nSearching for device: {vendor_id:04x}:{product_id:04x}...")
        device = usb.core.find(idVendor=vendor_id, idProduct=product_id)
        
        if device is None:
            print(f"Device {vendor_id:04x}:{product_id:04x} not found")
            return False
        
        print(f"Device found: {vendor_id:04x}:{product_id:04x}")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to find device: {e}")
        return False


def test_usb_device_access():
    """
    Test basic USB device access (configuration, endpoints).
    
    Based on the methods from:
    https://www.pythonhelp.org/tutorials/how-to-control-usb-port/
    
    Note: This test attempts to access device configurations, which may require
    elevated permissions on some systems.
    
    Returns:
        True if test completed successfully, False otherwise
    """
    if not PYUSB_AVAILABLE:
        print("ERROR: pyusb library not available")
        return False
    
    print("\n" + "=" * 60)
    print("USB Device Access Test")
    print("=" * 60)
    
    try:
        devices = list_usb_devices()
        
        if not devices:
            print("No devices available for access test")
            return False
        
        print(f"\nTesting access to {len(devices)} device(s)...\n")
        
        success_count = 0
        for i, device_info in enumerate(devices[:3], 1):  # Test first 3 devices
            device = device_info['device']
            print(f"Device {i} ({device_info['vendor_id_hex']}:{device_info['product_id_hex']}):")
            
            try:
                # Try to get device configuration
                # Note: This may fail on some systems due to permissions
                config = device.get_active_configuration()
                print(f"  Configuration: {config.bConfigurationValue}")
                
                # List interfaces
                interface_count = len(config)
                print(f"  Interfaces: {interface_count}")
                
                # Try to access first endpoint if available
                try:
                    interface = config[(0, 0)]
                    if len(interface) > 0:
                        endpoint = interface[0]
                        print(f"  First endpoint: {endpoint.bEndpointAddress:02x}")
                except (IndexError, AttributeError):
                    print(f"  No endpoints accessible")
                
                print("  Status: OK")
                success_count += 1
                
            except usb.core.USBError as e:
                print(f"  Status: Access denied or error - {e}")
                print("  (This is normal if you don't have permissions or the device is in use)")
            except Exception as e:
                print(f"  Status: Error - {e}")
        
        print(f"\nSuccessfully accessed {success_count}/{min(len(devices), 3)} device(s)")
        print("=" * 60)
        
        return success_count > 0
        
    except Exception as e:
        print(f"\nERROR: USB device access test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_usb_events():
    """
    Test monitoring USB device connections/disconnections.
    
    Based on the method from:
    https://www.pythonhelp.org/tutorials/how-to-control-usb-port/
    
    This is a simplified version that checks for devices at two time points.
    
    Returns:
        True if test completed successfully, False otherwise
    """
    if not PYUSB_AVAILABLE:
        print("ERROR: pyusb library not available")
        return False
    
    print("\n" + "=" * 60)
    print("USB Device Event Monitoring Test")
    print("=" * 60)
    print("\nChecking for device changes (wait 5 seconds, then check again)...")
    
    try:
        import time
        
        # Initial device count
        initial_devices = list_usb_devices()
        initial_count = len(initial_devices)
        print(f"\nInitial device count: {initial_count}")
        
        # Wait 5 seconds
        print("Waiting 5 seconds... (you can plug/unplug devices during this time)")
        time.sleep(5)
        
        # Check again
        final_devices = list_usb_devices()
        final_count = len(final_devices)
        print(f"Final device count: {final_count}")
        
        if initial_count != final_count:
            print(f"\nDevice count changed: {initial_count} -> {final_count}")
            print("This indicates a device was connected or disconnected.")
        else:
            print("\nDevice count unchanged.")
        
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\nERROR: USB event monitoring test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """
    Run all USB device tests.
    
    Returns:
        True if all tests passed, False otherwise
    """
    print("\n" + "=" * 60)
    print("Running All USB Device Tests")
    print("=" * 60)
    print("\nReference: https://www.pythonhelp.org/tutorials/how-to-control-usb-port/")
    print()
    
    results = []
    
    # Test 1: Detect USB devices
    print("\n[Test 1] USB Device Detection")
    print("-" * 60)
    results.append(("Device Detection", test_detect_usb_devices()))
    
    # Test 2: USB device access
    print("\n[Test 2] USB Device Access")
    print("-" * 60)
    results.append(("Device Access", test_usb_device_access()))
    
    # Test 3: USB events
    print("\n[Test 3] USB Device Event Monitoring")
    print("-" * 60)
    results.append(("Event Monitoring", test_usb_events()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"  {test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("All tests PASSED!")
    else:
        print("Some tests FAILED. Check output above for details.")
    print("=" * 60)
    
    return all_passed


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Test USB device detection using pyusb library',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Reference documentation:
https://www.pythonhelp.org/tutorials/how-to-control-usb-port/

Examples:
  # Run all tests
  python tests/devdeck/usb/test_usb_devices.py

  # Run only device detection test
  python tests/devdeck/usb/test_usb_devices.py --test detect

  # Run only device access test
  python tests/devdeck/usb/test_usb_devices.py --test access
        """
    )
    
    parser.add_argument(
        '--test',
        choices=['detect', 'access', 'events', 'all'],
        default='all',
        help='Which test to run (default: all)'
    )
    
    args = parser.parse_args()
    
    if args.test == 'detect':
        success = test_detect_usb_devices()
    elif args.test == 'access':
        success = test_usb_device_access()
    elif args.test == 'events':
        success = test_usb_events()
    else:
        success = run_all_tests()
    
    sys.exit(0 if success else 1)

