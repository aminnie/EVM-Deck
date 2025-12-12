"""
USB Device Detection Utility for checking required USB devices.

This module provides functions to detect USB devices via the `lsusb` command
on Linux/Raspberry Pi systems. On Windows, it relies on the StreamDeck library
and MIDI port enumeration instead.
"""

import logging
import platform
import re
import subprocess
import xml.etree.ElementTree as ET
from typing import List, Optional, Tuple


class USBDevice:
    """Represents a USB device with vendor and product IDs."""
    
    def __init__(self, bus: str, device: str, vendor_id: str, product_id: str, description: str):
        self.bus = bus
        self.device = device
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.description = description
    
    def __repr__(self):
        return f"USBDevice(bus={self.bus}, device={self.device}, id={self.vendor_id}:{self.product_id}, desc='{self.description}')"


def get_usb_devices() -> List[USBDevice]:
    """
    Get a list of all connected USB devices.
    
    On Linux: Uses `lsusb` command
    On macOS: Uses `system_profiler SPUSBDataType` command
    On Windows: Returns empty list (relies on library detection instead)
    
    Returns:
        List of USBDevice objects. Returns empty list on Windows or if commands are not available.
    """
    system = platform.system()
    logger = logging.getLogger('devdeck')
    
    if system == 'Windows':
        return []
    elif system == 'Darwin':  # macOS
        return _get_usb_devices_macos()
    else:  # Linux
        return _get_usb_devices_linux()


def _get_usb_devices_linux() -> List[USBDevice]:
    """Get USB devices on Linux using lsusb."""
    logger = logging.getLogger('devdeck')
    try:
        # Run lsusb command
        result = subprocess.run(
            ['lsusb'],
            capture_output=True,
            text=True,
            timeout=5,
            check=False
        )
        
        logger.debug(f"lsusb return code: {result.returncode}")
        logger.debug(f"lsusb stdout length: {len(result.stdout)}")
        logger.debug(f"lsusb stderr: {result.stderr}")
        
        if result.returncode != 0:
            logger.warning(f"lsusb command failed with return code {result.returncode}: {result.stderr}")
            return []
        
        if not result.stdout.strip():
            logger.warning("lsusb returned empty output")
            return []
        
        devices = []
        # Parse lsusb output format: "Bus 001 Device 002: ID 1a86:752d QinHeng Electronics CH345 MIDI adapter"
        # Description is optional (some devices may not have one)
        pattern = r'Bus (\d+)\s+Device (\d+):\s+ID\s+([0-9a-fA-F]{4}):([0-9a-fA-F]{4})(?:\s+(.+))?'
        
        lines = result.stdout.strip().split('\n')
        logger.debug(f"Parsing {len(lines)} lines from lsusb output")
        
        for line_num, line in enumerate(lines, 1):
            if not line.strip():  # Skip empty lines
                continue
            match = re.match(pattern, line)
            if match:
                bus, device, vendor_id, product_id, description = match.groups()
                # Handle case where description might be None
                description = description.strip() if description else "Unknown device"
                devices.append(USBDevice(bus, device, vendor_id.lower(), product_id.lower(), description))
                logger.debug(f"Parsed line {line_num}: {line} -> vendor_id={vendor_id.lower()}")
            else:
                logger.debug(f"Failed to parse line {line_num}: {line}")
        
        logger.debug(f"Total devices parsed: {len(devices)}")
        return devices
    
    except FileNotFoundError:
        logging.getLogger('devdeck').warning("lsusb command not found. USB device detection unavailable.")
        return []
    except subprocess.TimeoutExpired:
        logging.getLogger('devdeck').warning("lsusb command timed out.")
        return []
    except Exception as e:
        logging.getLogger('devdeck').warning(f"Error running lsusb: {e}")
        return []


def _get_usb_devices_macos() -> List[USBDevice]:
    """Get USB devices on macOS using system_profiler with XML parsing."""
    logger = logging.getLogger('devdeck')
    try:
        # First try system_profiler with text output (simpler to parse)
        result = subprocess.run(
            ['system_profiler', 'SPUSBDataType'],
            capture_output=True,
            text=True,
            timeout=10,
            check=False
        )
        
        if result.returncode == 0 and result.stdout.strip():
            # Try parsing text output first (more reliable)
            devices = _parse_system_profiler_text(result.stdout, logger)
            if devices:
                logger.info(f"Found {len(devices)} USB device(s) via system_profiler text on macOS")
                return devices
        
        # Fallback to XML parsing
        result = subprocess.run(
            ['system_profiler', 'SPUSBDataType', '-xml'],
            capture_output=True,
            text=True,
            timeout=10,
            check=False
        )
        
        if result.returncode != 0:
            logger.warning(f"system_profiler failed with return code {result.returncode}: {result.stderr}")
            return _try_ioreg_macos() or _try_lsusb_macos()
        
        if not result.stdout.strip():
            logger.warning("system_profiler returned empty output")
            return _try_ioreg_macos() or _try_lsusb_macos()
        
        try:
            # Parse XML output
            root = ET.fromstring(result.stdout)
            devices = []
            bus_num = "0"  # system_profiler doesn't provide bus numbers, use 0 as placeholder
            device_num = 0
            
            def extract_devices(element):
                """Recursively extract USB device information from XML tree."""
                nonlocal device_num
                
                # system_profiler XML structure: plist -> array -> dict -> _items -> array -> dict (devices)
                # Each device dict has key-value pairs
                for item in element.findall('.//dict'):
                    vendor_id = None
                    product_id = None
                    description = "Unknown device"
                    
                    # Parse key-value pairs in the dict
                    # XML structure: <key>vendor_id</key><integer>0x0fd9</integer> or <string>...</string>
                    children = list(item)
                    i = 0
                    while i < len(children):
                        child = children[i]
                        if child.tag == 'key' and child.text:
                            key = child.text
                            # Next sibling should be the value
                            if i + 1 < len(children):
                                value_elem = children[i + 1]
                                value = value_elem.text if value_elem.text else ""
                                
                                if key == 'vendor_id':
                                    try:
                                        # Convert to hex string (4 digits, lowercase)
                                        vendor_int = int(value, 16) if value.startswith('0x') else int(value)
                                        vendor_id = f"{vendor_int:04x}".lower()
                                    except (ValueError, AttributeError):
                                        pass
                                elif key == 'product_id':
                                    try:
                                        # Convert to hex string (4 digits, lowercase)
                                        product_int = int(value, 16) if value.startswith('0x') else int(value)
                                        product_id = f"{product_int:04x}".lower()
                                    except (ValueError, AttributeError):
                                        pass
                                elif key in ('_name', 'product_name'):
                                    description = value or "Unknown device"
                            i += 2
                        else:
                            i += 1
                    
                    # If we found both vendor and product IDs, create a device entry
                    if vendor_id and product_id:
                        device_num += 1
                        devices.append(USBDevice(
                            bus_num,
                            str(device_num),
                            vendor_id,
                            product_id,
                            description
                        ))
                        logger.debug(f"Found USB device: {vendor_id}:{product_id} - {description}")
                
                # Recursively process child elements
                for child in element:
                    extract_devices(child)
            
            extract_devices(root)
            
            if devices:
                logger.info(f"Found {len(devices)} USB device(s) via system_profiler XML on macOS")
                return devices
            else:
                logger.debug("system_profiler XML found no USB devices, trying ioreg fallback")
                # Try ioreg as intermediate fallback before lsusb
                return _try_ioreg_macos() or _try_lsusb_macos()
        
        except ET.ParseError as e:
            logger.warning(f"Failed to parse system_profiler XML output: {e}, trying ioreg fallback")
            return _try_ioreg_macos() or _try_lsusb_macos()
    
    except FileNotFoundError:
        logger.warning("system_profiler not found, trying ioreg fallback")
        return _try_ioreg_macos() or _try_lsusb_macos()
    except Exception as e:
        logger.warning(f"Error running system_profiler: {e}, trying ioreg fallback")
        import traceback
        logger.debug(traceback.format_exc())
        return _try_ioreg_macos() or _try_lsusb_macos()


def _parse_system_profiler_text(output: str, logger) -> List[USBDevice]:
    """Parse system_profiler text output to extract USB devices."""
    devices = []
    bus_num = "0"
    device_num = 0
    
    # Look for vendor ID and product ID patterns in the text output
    # Format example:
    #     Product ID: 0x0060
    #     Vendor ID: 0x0fd9
    #     Product Name: Stream Deck
    
    lines = output.split('\n')
    current_device = {}
    in_device_section = False
    
    for line in lines:
        stripped = line.strip()
        
        # Detect start of a device section (usually starts with device name or "USB Device")
        if ':' in stripped and not in_device_section:
            # Check if this looks like a device header
            if any(keyword in stripped.lower() for keyword in ['usb device', 'product id', 'vendor id']):
                in_device_section = True
                current_device = {}
        
        # Extract Vendor ID
        vendor_match = re.search(r'Vendor ID:\s*(?:0x)?([0-9a-fA-F]{4})', stripped, re.IGNORECASE)
        if vendor_match:
            try:
                vendor_val = vendor_match.group(1)
                vendor_int = int(vendor_val, 16) if vendor_val.startswith('0x') else int(vendor_val)
                current_device['vendor_id'] = f"{vendor_int:04x}".lower()
            except ValueError:
                pass
        
        # Extract Product ID
        product_match = re.search(r'Product ID:\s*(?:0x)?([0-9a-fA-F]{4})', stripped, re.IGNORECASE)
        if product_match:
            try:
                product_val = product_match.group(1)
                product_int = int(product_val, 16) if product_val.startswith('0x') else int(product_val)
                current_device['product_id'] = f"{product_int:04x}".lower()
            except ValueError:
                pass
        
        # Extract Product Name
        name_match = re.search(r'Product Name:\s*(.+)', stripped, re.IGNORECASE)
        if name_match:
            current_device['description'] = name_match.group(1).strip()
        
        # When we have both IDs, create device and reset
        if 'vendor_id' in current_device and 'product_id' in current_device:
            device_num += 1
            description = current_device.get('description', 'Unknown device')
            devices.append(USBDevice(
                bus_num,
                str(device_num),
                current_device['vendor_id'],
                current_device['product_id'],
                description
            ))
            logger.debug(f"Found USB device from text: {current_device['vendor_id']}:{current_device['product_id']} - {description}")
            current_device = {}
            in_device_section = False
    
    return devices


def _try_ioreg_macos() -> List[USBDevice]:
    """Try to use ioreg on macOS as a fallback method."""
    logger = logging.getLogger('devdeck')
    try:
        # Use ioreg to get USB device information
        # Try multiple ioreg command variations for better compatibility
        ioreg_commands = [
            ['ioreg', '-p', 'IOUSB', '-w0', '-l'],
            ['ioreg', '-p', 'IOUSB', '-r'],
            ['ioreg', '-p', 'IOUSB', '-r', '-n', 'IOUSBDevice'],
        ]
        
        for cmd in ioreg_commands:
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=False
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    devices = _parse_ioreg_output(result.stdout, logger)
                    if devices:
                        logger.info(f"Found {len(devices)} USB device(s) via ioreg on macOS")
                        return devices
            except Exception as e:
                logger.debug(f"ioreg command {cmd} failed: {e}")
                continue
        
        return []
    except Exception as e:
        logger.debug(f"Error trying ioreg on macOS: {e}")
        return []


def _parse_ioreg_output(output: str, logger) -> List[USBDevice]:
    """Parse ioreg output to extract USB devices."""
    devices = []
    bus_num = "0"
    device_num = 0
    
    # Look for vendor and product IDs in the output
    # Format: "idVendor" = 0x0fd9 or "idVendor" = 4057 (decimal)
    vendor_pattern = r'"idVendor"\s*=\s*(?:0x)?([0-9a-fA-F]+)'
    product_pattern = r'"idProduct"\s*=\s*(?:0x)?([0-9a-fA-F]+)'
    name_patterns = [
        r'"USB Product Name"\s*=\s*"([^"]+)"',
        r'"Product Name"\s*=\s*"([^"]+)"',
        r'"_name"\s*=\s*"([^"]+)"',
        r'"IOName"\s*=\s*"([^"]+)"',
    ]
    
    lines = output.split('\n')
    current_device = {}
    
    for line in lines:
        # Extract vendor ID
        vendor_match = re.search(vendor_pattern, line, re.IGNORECASE)
        if vendor_match:
            try:
                vendor_val = vendor_match.group(1)
                vendor_int = int(vendor_val, 16) if '0x' in line.lower() else int(vendor_val)
                current_device['vendor_id'] = f"{vendor_int:04x}".lower()
            except ValueError:
                pass
        
        # Extract product ID
        product_match = re.search(product_pattern, line, re.IGNORECASE)
        if product_match:
            try:
                product_val = product_match.group(1)
                product_int = int(product_val, 16) if '0x' in line.lower() else int(product_val)
                current_device['product_id'] = f"{product_int:04x}".lower()
            except ValueError:
                pass
        
        # Extract device name (try multiple patterns)
        for name_pattern in name_patterns:
            name_match = re.search(name_pattern, line)
            if name_match:
                current_device['description'] = name_match.group(1)
                break
        
        # When we have both IDs, create device and reset
        if 'vendor_id' in current_device and 'product_id' in current_device:
            device_num += 1
            description = current_device.get('description', 'Unknown device')
            devices.append(USBDevice(
                bus_num,
                str(device_num),
                current_device['vendor_id'],
                current_device['product_id'],
                description
            ))
            logger.debug(f"Found USB device via ioreg: {current_device['vendor_id']}:{current_device['product_id']} - {description}")
            current_device = {}
    
    return devices


def _try_lsusb_macos() -> List[USBDevice]:
    """Try to use lsusb on macOS (if installed via Homebrew)."""
    logger = logging.getLogger('devdeck')
    try:
        # Try lsusb (might be installed via Homebrew)
        result = subprocess.run(
            ['lsusb'],
            capture_output=True,
            text=True,
            timeout=5,
            check=False
        )
        
        if result.returncode == 0 and result.stdout.strip():
            # Parse same format as Linux
            devices = []
            pattern = r'Bus (\d+)\s+Device (\d+):\s+ID\s+([0-9a-fA-F]{4}):([0-9a-fA-F]{4})(?:\s+(.+))?'
            lines = result.stdout.strip().split('\n')
            
            for line in lines:
                if not line.strip():
                    continue
                match = re.match(pattern, line)
                if match:
                    bus, device, vendor_id, product_id, description = match.groups()
                    description = description.strip() if description else "Unknown device"
                    devices.append(USBDevice(bus, device, vendor_id.lower(), product_id.lower(), description))
            
            logger.debug(f"Found {len(devices)} USB devices via lsusb on macOS")
            return devices
        else:
            logger.debug("lsusb not available or returned no output on macOS")
            return []
    
    except FileNotFoundError:
        logger.debug("lsusb not installed on macOS (install via: brew install lsusb)")
        return []
    except Exception as e:
        logger.debug(f"Error trying lsusb on macOS: {e}")
        return []


def check_elgato_stream_deck() -> Tuple[bool, Optional[USBDevice]]:
    """
    Check if an Elgato Stream Deck is connected via USB.
    
    Elgato Stream Deck vendor ID: 0fd9
    Common product IDs:
    - 0060: Stream Deck (original)
    - 0063: Stream Deck Mini
    - 006c: Stream Deck XL
    - 006d: Stream Deck (rev2)
    - 0080: Stream Deck +
    - 0084: Stream Deck Pedal
    - 00b9: Stream Deck MK.2
    
    Returns:
        Tuple of (is_connected, device_info). On Windows/macOS, also tries StreamDeck library
        detection as a fallback if USB enumeration fails.
    """
    logger = logging.getLogger('devdeck')
    
    # On Windows, skip USB-level check and rely on StreamDeck library
    if platform.system() == 'Windows':
        logger.debug("Windows detected - skipping USB-level Stream Deck check (using library detection)")
        return (True, None)
    
    devices = get_usb_devices()
    
    # Log all detected USB devices for debugging
    if devices:
        logger.info(f"Detected {len(devices)} USB device(s):")
        for device in devices:
            logger.info(f"  - {device}")
    else:
        logger.warning("No USB devices detected via USB enumeration")
        # On macOS, if lsusb/system_profiler fails, try StreamDeck library as fallback
        if platform.system() == 'Darwin':
            logger.info("Attempting StreamDeck library detection as fallback...")
            try:
                from StreamDeck.DeviceManager import DeviceManager
                streamdecks = DeviceManager().enumerate()
                if streamdecks:
                    logger.info(f"StreamDeck library detected {len(streamdecks)} device(s)")
                    # Return True but no USB device info (library detection doesn't provide USB details)
                    return (True, None)
            except Exception as e:
                logger.debug(f"StreamDeck library detection failed: {e}")
    
    # Elgato Stream Deck detection: vendor ID or name string
    elgato_vendor_id = '0fd9'
    
    for device in devices:
        # Check by vendor ID or by name string in description
        if (device.vendor_id == elgato_vendor_id or 
            'elgato' in device.description.lower()):
            logger.info(f"Elgato Stream Deck detected: {device}")
            return (True, device)
    
    # If USB enumeration didn't find it, try StreamDeck library as fallback (macOS)
    if platform.system() == 'Darwin' and not devices:
        logger.info("Attempting StreamDeck library detection as fallback...")
        try:
            from StreamDeck.DeviceManager import DeviceManager
            streamdecks = DeviceManager().enumerate()
            if streamdecks:
                logger.info(f"StreamDeck library detected {len(streamdecks)} device(s)")
                return (True, None)
        except Exception as e:
            logger.debug(f"StreamDeck library detection failed: {e}")
    
    logger.error("Elgato Stream Deck not detected via USB or library")
    return (False, None)


def check_midi_output_device() -> Tuple[bool, Optional[USBDevice]]:
    """
    Check if a MIDI output USB device is connected.
    
    This function looks for USB devices that are likely MIDI devices.
    It checks for:
    - Known MIDI chip vendors (e.g., CH345 with vendor ID 1a86)
    - Devices with "MIDI" in their description
    - Common MIDI interface vendor IDs
    
    Returns:
        Tuple of (is_connected, device_info). On Windows/macOS, also tries MIDI port
        enumeration as a fallback if USB enumeration fails.
    """
    logger = logging.getLogger('devdeck')
    
    # On Windows, skip USB-level check and rely on MIDI port enumeration
    if platform.system() == 'Windows':
        logger.debug("Windows detected - skipping USB-level MIDI check (using port enumeration)")
        return (True, None)
    
    devices = get_usb_devices()
    
    # Known MIDI-related vendor IDs (excluding CH345 and Ketron which are checked separately)
    midi_vendor_ids = {
        '0582',  # Roland
        '0763',  # M-Audio
        '0b0e',  # Yamaha
        '0944',  # Korg
        '0a92',  # Akai
        '17cc',  # Novation
        '1235',  # Focusrite
    }
    
    # Check for specific devices by vendor ID or name string
    for device in devices:
        # CH345: vendor ID 1a86 or "CH345" in description
        if (device.vendor_id == '1a86' or 'ch345' in device.description.lower()):
            logger.info(f"MIDI device detected (CH345): {device}")
            return (True, device)
        
        # Ketron: vendor ID 157b or "Ketron" in description
        if (device.vendor_id == '157b' or 'ketron' in device.description.lower()):
            logger.info(f"MIDI device detected (Ketron): {device}")
            return (True, device)
        
        # Other known MIDI vendor IDs
        if device.vendor_id in midi_vendor_ids:
            logger.info(f"MIDI device detected (by vendor ID): {device}")
            return (True, device)
    
    # Check for devices with "MIDI" in description (case-insensitive)
    for device in devices:
        if 'midi' in device.description.lower():
            logger.info(f"MIDI device detected (by description): {device}")
            return (True, device)
    
    # If USB enumeration didn't find it, try MIDI port enumeration as fallback (macOS)
    if platform.system() == 'Darwin' and not devices:
        logger.info("Attempting MIDI port enumeration as fallback...")
        try:
            import mido
            output_ports = mido.get_output_names()
            if output_ports:
                logger.info(f"MIDI port enumeration found {len(output_ports)} output port(s)")
                # Return True but no USB device info (port enumeration doesn't provide USB details)
                return (True, None)
        except Exception as e:
            logger.debug(f"MIDI port enumeration failed: {e}")
    
    logger.error("No MIDI output USB device detected")
    return (False, None)


def check_midi_input_device() -> Tuple[bool, Optional[USBDevice]]:
    """
    Check if a MIDI input USB device is connected.
    
    This function looks for USB devices that are MIDI input devices, such as
    Adafruit MacroPad (vendor ID 239a) used for Stream Deck input.
    
    Returns:
        Tuple of (is_connected, device_info). On Windows, returns (True, None) since
        we rely on MIDI port enumeration instead.
    """
    logger = logging.getLogger('devdeck')
    
    # On Windows, skip USB-level check and rely on MIDI port enumeration
    if platform.system() == 'Windows':
        logger.debug("Windows detected - skipping USB-level MIDI input check (using port enumeration)")
        return (True, None)
    
    devices = get_usb_devices()
    
    # Known MIDI input device vendor IDs
    midi_input_vendor_ids = {
        '239a',  # Adafruit (MacroPad for Stream Deck input)
    }
    
    # Check for known MIDI input vendor IDs
    for device in devices:
        if device.vendor_id in midi_input_vendor_ids:
            logger.info(f"MIDI input device detected (by vendor ID): {device}")
            return (True, device)
    
    logger.debug("No MIDI input USB device detected")
    return (False, None)

