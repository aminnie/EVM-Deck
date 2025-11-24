"""
MIDI Manager for handling MIDI port connections and message sending.

This module provides a singleton MIDI manager that handles MIDI port connections
and provides methods to send MIDI CC and SysEx messages. It uses the mido library
with python-rtmidi backend for cross-platform compatibility (Windows, Linux, Raspberry Pi).
"""

import logging
import platform
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
                
                # Check if port exists
                if port_name not in available_ports:
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
            self.__logger.debug(f"Sent CC: channel={channel}, control={control}, value={value}")
            return True
            
        except Exception as e:
            self.__logger.error(f"Error sending CC message: {e}")
            return False
    
    def send_sysex(self, data: List[int], port_name: Optional[str] = None) -> bool:
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
            self.__logger.debug(f"Sent SysEx: {len(data)} bytes")
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
        
        return self.send_sysex(data, port_name)
    
    def _get_port(self, port_name: Optional[str] = None):
        """
        Get a MIDI output port.
        
        Args:
            port_name: Name of the port. If None, returns the first open port.
        
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
                if port_name not in self._output_ports:
                    self.__logger.error(f"Port '{port_name}' is not open")
                    return None
                return self._output_ports[port_name]
    
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
            port_name: Name of the port. If None, checks if any port is open.
        
        Returns:
            True if port is open, False otherwise
        """
        with self._port_lock:
            if port_name is None:
                return len(self._output_ports) > 0
            return port_name in self._output_ports

