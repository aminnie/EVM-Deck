"""
MIDI Manager for handling MIDI port connections and message sending.

This module provides a singleton MIDI manager that handles MIDI port connections
and provides methods to send MIDI CC and SysEx messages. It uses the mido library
with python-rtmidi backend for cross-platform compatibility (Windows, Linux, Raspberry Pi).
"""

import logging
import platform
import re
import threading
from typing import Optional, List

try:
    import mido
    from mido import Message, MidiFile
except ImportError:
    mido = None
    Message = None
    MidiFile = None


class MidiManager:
    """
    Singleton MIDI manager for handling MIDI port connections and message sending.
    
    This class manages MIDI output ports and provides thread-safe methods
    to send MIDI CC and SysEx messages.
    """
    
    # Supported USB-to-MIDI device vendor IDs for auto-detection
    # This list can be expanded for future USB-to-MIDI devices
    SUPPORTED_MIDI_VENDOR_IDS = ['1a86']  # CH345 USB-to-MIDI adapter
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MidiManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the MIDI manager"""
        if self._initialized:
            return
            
        self.__logger = logging.getLogger('devdeck')
        self._output_ports = {}
        self._port_lock = threading.Lock()
        self._initialized = True
        
        # Check if mido is available (reference module-level variable)
        # Import mido at module level - check if it was successfully imported
        import sys
        current_module = sys.modules[__name__]
        mido_module = getattr(current_module, 'mido', None)
        
        if mido_module is None:
            self.__logger.warning("mido library not installed. MIDI functionality will be disabled.")
            self.__logger.warning("Install with: pip install mido python-rtmidi")
        else:
            # Set backend to rtmidi for cross-platform support
            # Note: python-rtmidi must be installed for this to work
            try:
                import mido.backends.rtmidi
                mido_module.set_backend('mido.backends.rtmidi')
                self.__logger.info("MIDI backend set to rtmidi")
            except ImportError:
                self.__logger.warning("python-rtmidi not installed. Install with: pip install python-rtmidi")
                self.__logger.info("Using default MIDI backend (may have limited functionality)")
            except Exception as e:
                self.__logger.warning(f"Could not set rtmidi backend: {e}. Using default backend.")
    
    def list_output_ports(self) -> List[str]:
        """
        List all available MIDI output ports.
        
        Returns:
            List of port names
        """
        if mido is None:
            return []
        
        try:
            return mido.get_output_names()
        except Exception as e:
            self.__logger.error(f"Error listing MIDI output ports: {e}")
            return []
    
    def find_port_by_partial_name(self, partial_name: str) -> Optional[str]:
        """
        Find a MIDI port by partial name match.
        
        This is useful when USB MIDI port numbers change after reboot.
        For example, "CH345:CH345 MIDI 1" will match "CH345:CH345 MIDI 1 16:0" or "CH345:CH345 MIDI 1 24:0".
        Also handles full port names like "CH345:CH345 MIDI 1 24:0" matching "CH345:CH345 MIDI 1 16:0".
        
        Args:
            partial_name: Partial port name to search for (case-insensitive)
        
        Returns:
            Full port name if found, None otherwise
        """
        if mido is None:
            return None
        
        try:
            available_ports = mido.get_output_names()
            partial_lower = partial_name.lower()
            
            # First try exact match
            for port in available_ports:
                if port == partial_name:
                    return port
            
            # Extract device name from full port name (remove port number suffix like " 24:0")
            # Port names typically follow pattern: "DeviceName PortNumber:SubPort"
            # Try to extract just the device name part
            # Match pattern like " 16:0" or " 24:0" at the end
            device_name_match = re.match(r'^(.+?)\s+\d+:\d+$', partial_name)
            if device_name_match:
                device_name = device_name_match.group(1)
                device_name_lower = device_name.lower()
                # Look for ports that start with the device name
                matches = [p for p in available_ports if p.lower().startswith(device_name_lower)]
                if matches:
                    return matches[0]
            
            # Then try partial match (port name starts with or contains the partial name)
            # Prefer ports that start with the partial name
            matches_starting = [p for p in available_ports if p.lower().startswith(partial_lower)]
            if matches_starting:
                return matches_starting[0]
            
            # If no starting match, try contains match
            matches_containing = [p for p in available_ports if partial_lower in p.lower()]
            if matches_containing:
                return matches_containing[0]
            
            return None
        except Exception as e:
            self.__logger.error(f"Error finding port by partial name: {e}")
            return None
    
    def find_port_by_vendor_id_list(self, vendor_ids: List[str]) -> Optional[str]:
        """
        Find a MIDI port by matching vendor IDs (macOS) or device patterns (Linux/Raspberry Pi).
        
        On macOS, MIDI port names contain vendor IDs (e.g., "1a86" for CH345).
        On Linux/Raspberry Pi, ports are identified by device name patterns (e.g., "CH345").
        
        Args:
            vendor_ids: List of vendor IDs to search for (e.g., ['1a86'] for CH345)
        
        Returns:
            Full port name if found, None otherwise
        """
        if mido is None:
            return None
        
        try:
            available_ports = mido.get_output_names()
            system = platform.system()
            
            if system == 'Darwin':  # macOS
                # On macOS, port names contain vendor IDs (e.g., "1a86")
                # Search for ports containing any of the vendor IDs
                for vendor_id in vendor_ids:
                    vendor_id_lower = vendor_id.lower()
                    for port in available_ports:
                        if vendor_id_lower in port.lower():
                            self.__logger.info(f"Found MIDI port by vendor ID {vendor_id}: {port}")
                            return port
                self.__logger.debug(f"No MIDI port found containing vendor IDs: {vendor_ids}")
                return None
            else:
                # On Linux/Raspberry Pi, use device name patterns
                # For CH345 (vendor ID 1a86), search for "CH345" in port name
                device_patterns = {
                    '1a86': 'CH345',  # CH345 USB-to-MIDI adapter
                    # Add more mappings here for future devices
                }
                
                for vendor_id in vendor_ids:
                    if vendor_id.lower() in device_patterns:
                        pattern = device_patterns[vendor_id.lower()]
                        matched_port = self.find_port_by_partial_name(pattern)
                        if matched_port:
                            self.__logger.info(f"Found MIDI port by device pattern '{pattern}' (vendor ID {vendor_id}): {matched_port}")
                            return matched_port
                
                self.__logger.debug(f"No MIDI port found for vendor IDs: {vendor_ids}")
                return None
                
        except Exception as e:
            self.__logger.error(f"Error finding port by vendor ID list: {e}")
            return None
    
    def auto_detect_midi_port(self) -> Optional[str]:
        """
        Automatically detect MIDI port using supported vendor IDs.
        
        This method:
        - Uses SUPPORTED_MIDI_VENDOR_IDS to find matching ports
        - On macOS: searches for ports containing vendor IDs
        - On Linux/Raspberry Pi: searches for ports by device name patterns
        - Falls back to existing auto_connect_hardware_port() if no match found
        
        Returns:
            Port name if found, None otherwise
        """
        if mido is None:
            self.__logger.error("mido library not available. Cannot auto-detect MIDI port.")
            return None
        
        try:
            # Try to find port by vendor ID list
            detected_port = self.find_port_by_vendor_id_list(self.SUPPORTED_MIDI_VENDOR_IDS)
            if detected_port:
                self.__logger.info(f"Auto-detected MIDI port: {detected_port}")
                return detected_port
            
            # Fallback: use existing auto-connect logic
            self.__logger.debug("No port found by vendor ID, falling back to auto-connect hardware port")
            # Note: auto_connect_hardware_port() opens the port, but we just want the name
            # So we'll use a different approach - just return None and let the caller handle it
            return None
            
        except Exception as e:
            self.__logger.error(f"Error in auto_detect_midi_port: {e}", exc_info=True)
            return None
    
    def open_port(self, port_name: Optional[str] = None, use_virtual: bool = True) -> bool:
        """
        Open a MIDI output port.
        
        Args:
            port_name: Name of the MIDI port to open. If None and use_virtual=True, creates a virtual port.
                      If None and use_virtual=False, opens the first available hardware port.
            use_virtual: If True and port_name is None, creates a virtual port with client name.
                        If False or port_name is specified, opens an existing hardware port.
        
        Returns:
            True if port was opened successfully, False otherwise
        """
        if mido is None:
            self.__logger.error("mido library not available. Cannot open MIDI port.")
            return False
        
        try:
            with self._port_lock:
                # If port is already open, close it first
                if port_name and port_name in self._output_ports:
                    try:
                        self._output_ports[port_name].close()
                    except Exception:
                        pass
                
                # If no port name specified and use_virtual is True, try to create a virtual port
                # Note: Virtual ports are not supported on Windows with the default MIDI API
                if port_name is None and use_virtual:
                    # Check if we're on Windows - virtual ports aren't supported
                    is_windows = platform.system() == 'Windows'
                    
                    if not is_windows:
                        # Try to create a virtual port (Linux/macOS support this)
                        virtual_port_name = "EVM Stream Deck Controller"
                        try:
                            port = mido.open_output(virtual_port_name, virtual=True)
                            self._output_ports[virtual_port_name] = port
                            self.__logger.info(f"Created virtual MIDI output port: {virtual_port_name}")
                            self.__logger.info("Note: You may need to route this virtual port to your hardware MIDI device in your MIDI software")
                            return True
                        except Exception as e:
                            self.__logger.warning(f"Could not create virtual port: {e}. Falling back to hardware port.")
                            # Fall through to hardware port opening
                    else:
                        # On Windows, virtual ports aren't supported by default MIDI API
                        # Skip the attempt and go straight to hardware port
                        self.__logger.debug("Windows detected - virtual ports not supported, using hardware port")
                        # Fall through to hardware port opening
                
                # Get available hardware ports
                available_ports = mido.get_output_names()
                
                if not available_ports:
                    self.__logger.error("No MIDI output ports available")
                    return False
                
                # If no port name specified, prefer certain ports over others
                if port_name is None:
                    # Preferred port names (in order of preference)
                    preferred_ports = ['Midiview', 'midiview', 'MIDIVIEW']
                    
                    # Try to find a preferred port first
                    port_name = None
                    for preferred in preferred_ports:
                        # Check for exact match or if port name contains preferred name
                        for available_port in available_ports:
                            if preferred.lower() in available_port.lower():
                                port_name = available_port
                                self.__logger.info(f"No port specified, using preferred port: {port_name}")
                                break
                        if port_name:
                            break
                    
                    # If no preferred port found, use first available (but skip GS Wavetable Synth)
                    if port_name is None:
                        for available_port in available_ports:
                            # Skip Microsoft GS Wavetable Synth
                            if 'GS Wavetable Synth' not in available_port and 'gs wavetable synth' not in available_port.lower():
                                port_name = available_port
                                self.__logger.info(f"No port specified, using first available (excluding GS Wavetable): {port_name}")
                                break
                        
                        # If only GS Wavetable Synth is available, use it as last resort
                        if port_name is None:
                            port_name = available_ports[0]
                            self.__logger.warning(f"No port specified, only GS Wavetable Synth available, using: {port_name}")
                
                # Check if port exists - try exact match first, then partial match
                if port_name not in available_ports:
                    # Try to find port by partial name match (useful when USB port numbers change)
                    matched_port = self.find_port_by_partial_name(port_name)
                    if matched_port:
                        self.__logger.info(f"Port '{port_name}' not found exactly, but found matching port: '{matched_port}'")
                        port_name = matched_port
                    else:
                        self.__logger.error(f"MIDI port '{port_name}' not found. Available ports: {available_ports}")
                        return False
                
                # Open the hardware port
                try:
                    port = mido.open_output(port_name)
                    self._output_ports[port_name] = port
                    self.__logger.info(f"Opened MIDI output port: {port_name}")
                    return True
                except Exception as e:
                    self.__logger.error(f"Error opening MIDI port '{port_name}': {e}", exc_info=True)
                    return False
                    
        except Exception as e:
            self.__logger.error(f"Error in open_port: {e}")
            return False
    
    def close_port(self, port_name: Optional[str] = None):
        """
        Close a MIDI output port.
        
        Args:
            port_name: Name of the MIDI port to close. If None, closes all ports.
        """
        with self._port_lock:
            if port_name is None:
                # Close all ports
                for name, port in list(self._output_ports.items()):
                    try:
                        port.close()
                        self.__logger.info(f"Closed MIDI output port: {name}")
                    except Exception as e:
                        self.__logger.warning(f"Error closing port {name}: {e}")
                self._output_ports.clear()
            else:
                # Close specific port
                if port_name in self._output_ports:
                    try:
                        self._output_ports[port_name].close()
                        self.__logger.info(f"Closed MIDI output port: {port_name}")
                    except Exception as e:
                        self.__logger.warning(f"Error closing port {port_name}: {e}")
                    del self._output_ports[port_name]
    
    def send_cc(self, control: int, value: int, channel: int = 0, port_name: Optional[str] = None) -> bool:
        """
        Send a MIDI Control Change (CC) message.
        
        Args:
            control: CC number (0-127)
            value: CC value (0-127)
            channel: MIDI channel (0-15, default: 0)
            port_name: Name of the MIDI port to use. If None, uses the first open port.
        
        Returns:
            True if message was sent successfully, False otherwise
        """
        if mido is None:
            self.__logger.error("mido library not available. Cannot send CC message.")
            return False
        
        # Validate parameters
        if not (0 <= control <= 127):
            self.__logger.error(f"Invalid CC number: {control}. Must be 0-127")
            return False
        if not (0 <= value <= 127):
            self.__logger.error(f"Invalid CC value: {value}. Must be 0-127")
            return False
        if not (0 <= channel <= 15):
            self.__logger.error(f"Invalid MIDI channel: {channel}. Must be 0-15")
            return False
        
        try:
            # Create CC message
            msg = Message('control_change', channel=channel, control=control, value=value)
            
            # Get port to send to
            port = self._get_port(port_name)
            if port is None:
                return False
            
            # Send message
            port.send(msg)
            
            # Log exact MIDI CC message bytes
            # MIDI CC message format: Status byte (0xB0-0xBF for channels 0-15), Control, Value
            status_byte = 0xB0 + channel
            self.__logger.info(
                f"MIDI CC: 0x{status_byte:02X} 0x{control:02X} 0x{value:02X} "
                f"(channel={channel+1}, control={control}, value={value})"
            )
            return True
            
        except Exception as e:
            self.__logger.error(f"Error sending CC message: {e}")
            return False
    
    def send_sysex(self, data: List[int], port_name: Optional[str] = None, skip_log: bool = False) -> bool:
        """
        Send a MIDI System Exclusive (SysEx) message.
        
        Args:
            data: List of bytes (0-127) for the SysEx message (excluding 0xF0 and 0xF7)
            port_name: Name of the MIDI port to use. If None, uses the first open port.
        
        Returns:
            True if message was sent successfully, False otherwise
        """
        if mido is None:
            self.__logger.error("mido library not available. Cannot send SysEx message.")
            return False
        
        # Validate data
        if not isinstance(data, list):
            self.__logger.error(f"Invalid SysEx data: must be a list of integers")
            return False
        
        for byte_val in data:
            if not (0 <= byte_val <= 127):
                self.__logger.error(f"Invalid SysEx byte: {byte_val}. Must be 0-127")
                return False
        
        try:
            # Create SysEx message (mido automatically adds 0xF0 and 0xF7)
            msg = Message('sysex', data=data)
            
            # Get port to send to
            port = self._get_port(port_name)
            if port is None:
                return False
            
            # Send message
            port.send(msg)
            
            # Log exact SysEx message bytes (including F0 and F7) unless skip_log is True
            if not skip_log:
                sysex_bytes = [0xF0] + data + [0xF7]
                sysex_hex = ' '.join([f'0x{b:02X}' for b in sysex_bytes])
                self.__logger.info(
                    f"MIDI SysEx: {sysex_hex} ({len(data)} data bytes)"
                )
            return True
            
        except Exception as e:
            self.__logger.error(f"Error sending SysEx message: {e}")
            return False
    
    def send_sysex_raw(self, raw_data: List[int], port_name: Optional[str] = None) -> bool:
        """
        Send a raw SysEx message (including 0xF0 and 0xF7).
        
        Args:
            raw_data: List of bytes including 0xF0 at start and 0xF7 at end
            port_name: Name of the MIDI port to use. If None, uses the first open port.
        
        Returns:
            True if message was sent successfully, False otherwise
        """
        if mido is None:
            self.__logger.error("mido library not available. Cannot send SysEx message.")
            return False
        
        # Validate that message starts with 0xF0 and ends with 0xF7
        if not raw_data or raw_data[0] != 0xF0:
            self.__logger.error("SysEx message must start with 0xF0")
            return False
        
        if raw_data[-1] != 0xF7:
            self.__logger.error("SysEx message must end with 0xF7")
            return False
        
        # Extract data (remove 0xF0 and 0xF7)
        data = raw_data[1:-1]
        
        # Log exact SysEx message bytes before sending
        sysex_hex = ' '.join([f'0x{b:02X}' for b in raw_data])
        self.__logger.info(
            f"MIDI SysEx: {sysex_hex} ({len(data)} data bytes)"
        )
        
        # Skip logging in send_sysex since we already logged above
        return self.send_sysex(data, port_name, skip_log=True)
    
    def _get_port(self, port_name: Optional[str] = None):
        """
        Get a MIDI output port.
        
        Args:
            port_name: Name of the port (supports partial matching). If None, returns the first open port.
        
        Returns:
            MidiOutput port or None if not available
        """
        with self._port_lock:
            if not self._output_ports:
                self.__logger.error("No MIDI ports open. Call open_port() first.")
                return None
            
            if port_name is None:
                # Return first available port
                return next(iter(self._output_ports.values()))
            else:
                # First try exact match
                if port_name in self._output_ports:
                    return self._output_ports[port_name]
                
                # Then try partial match (useful when USB port numbers change)
                port_lower = port_name.lower()
                for open_port_name, open_port in self._output_ports.items():
                    # Check if open port starts with or contains the requested port name
                    if open_port_name.lower().startswith(port_lower) or port_lower in open_port_name.lower():
                        return open_port
                
                self.__logger.error(f"Port '{port_name}' is not open")
                return None
    
    def send_note_on(self, note: int, velocity: int = 64, channel: int = 0, port_name: Optional[str] = None) -> bool:
        """
        Send a MIDI Note On message.
        
        Args:
            note: MIDI note number (0-127)
            velocity: Note velocity (0-127, default: 64)
            channel: MIDI channel (0-15, default: 0)
            port_name: Name of the MIDI port to use. If None, uses the first open port.
        
        Returns:
            True if message was sent successfully, False otherwise
        """
        if mido is None:
            self.__logger.error("mido library not available. Cannot send Note On message.")
            return False
        
        # Validate parameters
        if not (0 <= note <= 127):
            self.__logger.error(f"Invalid note number: {note}. Must be 0-127")
            return False
        if not (0 <= velocity <= 127):
            self.__logger.error(f"Invalid velocity: {velocity}. Must be 0-127")
            return False
        if not (0 <= channel <= 15):
            self.__logger.error(f"Invalid MIDI channel: {channel}. Must be 0-15")
            return False
        
        try:
            # Create Note On message
            msg = Message('note_on', channel=channel, note=note, velocity=velocity)
            
            # Get port to send to
            port = self._get_port(port_name)
            if port is None:
                return False
            
            # Send message
            port.send(msg)
            self.__logger.debug(f"Sent Note On: channel={channel}, note={note}, velocity={velocity}")
            return True
            
        except Exception as e:
            self.__logger.error(f"Error sending Note On message: {e}")
            return False
    
    def send_note_off(self, note: int, velocity: int = 0, channel: int = 0, port_name: Optional[str] = None) -> bool:
        """
        Send a MIDI Note Off message.
        
        Args:
            note: MIDI note number (0-127)
            velocity: Note off velocity (0-127, default: 0)
            channel: MIDI channel (0-15, default: 0)
            port_name: Name of the MIDI port to use. If None, uses the first open port.
        
        Returns:
            True if message was sent successfully, False otherwise
        """
        if mido is None:
            self.__logger.error("mido library not available. Cannot send Note Off message.")
            return False
        
        # Validate parameters
        if not (0 <= note <= 127):
            self.__logger.error(f"Invalid note number: {note}. Must be 0-127")
            return False
        if not (0 <= velocity <= 127):
            self.__logger.error(f"Invalid velocity: {velocity}. Must be 0-127")
            return False
        if not (0 <= channel <= 15):
            self.__logger.error(f"Invalid MIDI channel: {channel}. Must be 0-15")
            return False
        
        try:
            # Create Note Off message
            msg = Message('note_off', channel=channel, note=note, velocity=velocity)
            
            # Get port to send to
            port = self._get_port(port_name)
            if port is None:
                return False
            
            # Send message
            port.send(msg)
            self.__logger.debug(f"Sent Note Off: channel={channel}, note={note}, velocity={velocity}")
            return True
            
        except Exception as e:
            self.__logger.error(f"Error sending Note Off message: {e}")
            return False
    
    def get_open_ports(self) -> List[str]:
        """
        Get a list of all currently open MIDI port names.
        
        Returns:
            List of open port names
        """
        with self._port_lock:
            return list(self._output_ports.keys())
    
    def get_port_info(self, port_name: Optional[str] = None) -> Optional[dict]:
        """
        Get information about an open MIDI port.
        
        Args:
            port_name: Name of the port. If None, returns info for the first open port.
        
        Returns:
            Dictionary with port information, or None if port not found
        """
        with self._port_lock:
            if port_name is None:
                if not self._output_ports:
                    return None
                port_name = list(self._output_ports.keys())[0]
            
            if port_name not in self._output_ports:
                return None
            
            port = self._output_ports[port_name]
            info = {
                'name': port_name,
                'is_virtual': getattr(port, 'is_virtual', False),
                'closed': getattr(port, 'closed', False),
            }
            
            # Try to get additional info if available
            if hasattr(port, 'name'):
                info['port_name'] = port.name
            
            return info
    
    def is_port_open(self, port_name: Optional[str] = None) -> bool:
        """
        Check if a MIDI port is open.
        
        Args:
            port_name: Name of the port (supports partial matching). If None, checks if any port is open.
        
        Returns:
            True if port is open, False otherwise
        """
        with self._port_lock:
            if port_name is None:
                return len(self._output_ports) > 0
            
            # First try exact match
            if port_name in self._output_ports:
                return True
            
            # Then try partial match (useful when USB port numbers change)
            port_lower = port_name.lower()
            for open_port in self._output_ports.keys():
                # Check if open port starts with or contains the requested port name
                if open_port.lower().startswith(port_lower) or port_lower in open_port.lower():
                    return True
            
            return False
    
    def auto_connect_hardware_port(self) -> bool:
        """
        Automatically detect and connect to the first available hardware MIDI output port.
        
        This method:
        - Lists all available MIDI output ports
        - Filters out virtual ports and "Midi Through" ports
        - Connects to the first available hardware MIDI port
        - Prefers ports with known MIDI device names
        
        Returns:
            True if a hardware port was successfully connected, False otherwise
        """
        if mido is None:
            self.__logger.error("mido library not available. Cannot auto-connect MIDI port.")
            return False
        
        # Check if a port is already open
        if len(self._output_ports) > 0:
            self.__logger.info("MIDI port already open, skipping auto-connect")
            return True
        
        try:
            available_ports = mido.get_output_names()
            
            if not available_ports:
                self.__logger.error("No MIDI output ports available for auto-connect")
                return False
            
            self.__logger.info(f"Available MIDI ports: {available_ports}")
            
            # Filter out virtual ports and "Midi Through"
            # Virtual ports typically have specific names or can be detected by trying to open them
            hardware_ports = []
            
            for port_name in available_ports:
                # Skip "Midi Through" ports
                if 'Midi Through' in port_name or 'midi through' in port_name.lower():
                    self.__logger.debug(f"Skipping Midi Through port: {port_name}")
                    continue
                
                # Skip Microsoft GS Wavetable Synth (Windows software synth)
                if 'GS Wavetable Synth' in port_name or 'gs wavetable synth' in port_name.lower():
                    self.__logger.debug(f"Skipping GS Wavetable Synth: {port_name}")
                    continue
                
                # Try to determine if it's a virtual port
                # On Linux, virtual ports are typically created by applications
                # We'll try to open the port and check if it's virtual
                try:
                    # Try to open the port to check if it's hardware
                    test_port = mido.open_output(port_name)
                    is_virtual = getattr(test_port, 'is_virtual', False)
                    test_port.close()
                    
                    if not is_virtual:
                        hardware_ports.append(port_name)
                        self.__logger.debug(f"Found hardware MIDI port: {port_name}")
                    else:
                        self.__logger.debug(f"Skipping virtual port: {port_name}")
                except Exception as e:
                    # If we can't open it, skip it
                    self.__logger.debug(f"Could not test port {port_name}: {e}")
                    # Still add it as a potential hardware port (might be a permission issue)
                    hardware_ports.append(port_name)
            
            if not hardware_ports:
                self.__logger.error("No hardware MIDI output ports found (only virtual ports or Midi Through available)")
                return False
            
            # Prefer ports with known MIDI device names (USB MIDI devices, etc.)
            preferred_names = ['USB MIDI', 'CH345', 'MIDI', 'Roland', 'M-Audio', 'Yamaha', 'Korg']
            preferred_port = None
            
            for preferred_name in preferred_names:
                for port in hardware_ports:
                    if preferred_name.lower() in port.lower():
                        preferred_port = port
                        self.__logger.info(f"Found preferred MIDI port: {preferred_port}")
                        break
                if preferred_port:
                    break
            
            # Use preferred port if found, otherwise use first hardware port
            port_to_connect = preferred_port if preferred_port else hardware_ports[0]
            
            self.__logger.info(f"Auto-connecting to MIDI hardware port: {port_to_connect}")
            
            # Connect to the selected port
            return self.open_port(port_to_connect, use_virtual=False)
            
        except Exception as e:
            self.__logger.error(f"Error in auto_connect_hardware_port: {e}", exc_info=True)
            return False

