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
    Get a list of all connected USB devices by parsing `lsusb` output.
    
    Returns:
        List of USBDevice objects. Returns empty list on Windows or if lsusb is not available.
    """
    # Works on Linux and macOS (Darwin) systems
    system = platform.system()
    if system not in ('Linux', 'Darwin'):
        return []

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
        Tuple of (is_connected, device_info). On Windows, returns (True, None) since
        we rely on StreamDeck library detection instead.
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
        logger.warning("No USB devices detected via lsusb")
    
    # Elgato Stream Deck detection: vendor ID or name string
    elgato_vendor_id = '0fd9'
    
    for device in devices:
        # Check by vendor ID or by name string in description
        if (device.vendor_id == elgato_vendor_id or 
            'elgato' in device.description.lower()):
            logger.info(f"Elgato Stream Deck detected: {device}")
            return (True, device)
    
    logger.error("Elgato Stream Deck not detected via USB")
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
        Tuple of (is_connected, device_info). On Windows, returns (True, None) since
        we rely on MIDI port enumeration instead.
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

