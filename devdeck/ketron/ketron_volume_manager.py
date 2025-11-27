"""
Ketron Volume Manager for tracking and managing volume levels.

This module provides a singleton volume manager that tracks volume levels
for various Ketron MIDI controls. Each volume can be incremented, decremented,
or muted (set to 0). When volumes are changed, MIDI CC commands are automatically
sent based on the last pressed button.
"""

import logging
import threading
from typing import Optional

from devdeck.ketron import KetronMidi
from devdeck.midi import MidiManager


class KetronVolumeManager:
    """
    Singleton volume manager for tracking Ketron volume levels.
    
    This class manages volume levels for various Ketron controls:
    - lower (LOWERS)
    - voice1 (VOICE1)
    - voice2 (VOICE2)
    - drawbars (DRAWBARS)
    - style (STYLE)
    - drum (DRUM)
    - chord (CHORD)
    - realchord (REALCHORD)
    
    Each volume is an integer between 0 and 127 (inclusive).
    """
    
    _instance = None
    _lock = threading.Lock()
    _MIN_VOLUME = 0
    _MAX_VOLUME = 127
    
    def __new__(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(KetronVolumeManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the volume manager"""
        if self._initialized:
            return
        
        self.__logger = logging.getLogger('devdeck')
        self._volume_lock = threading.Lock()
        
        # Initialize all volumes to 80 by default
        self._lower = 80
        self._voice1 = 80
        self._voice2 = 80
        self._drawbars = 80
        self._style = 80
        self._drum = 80
        self._chord = 80
        self._realchord = 80
        self._bass = 80
        self._master = 80  # Master volume
        
        # Initialize MIDI output channel (1-16, default: 16)
        self._midi_out_channel = 16
        
        # Track last pressed button key_name from SecondPageDeckController
        # Default to "Style" so Volume Up/Down always have a target
        self._last_pressed_key_name: Optional[str] = "Style"
        
        # Initialize KetronMidi and MidiManager for sending CC commands
        self.ketron_midi = KetronMidi()
        self.midi_manager = MidiManager()
        
        # Mapping from cc_midis key_name to volume variable name
        # Note: Keys should be uppercase since lookup uses key_name.upper()
        self._key_name_to_volume = {
            "LOWERS": "lower",
            "VOICE1": "voice1",
            "VOICE2": "voice2",
            "DRAW ORGAN": "drawbars",  # For "Draw Organ" in cc_midis
            "DRAWBARS": "drawbars",  # For "drawbars" in cc_midis
            "STYLE": "style",
            "Style": "style",
            "DRUM": "drum",
            "Drums": "drum",
            "CHORD": "chord",
            "Chords": "chord",
            "REALCHORD": "realchord",
            "REAL CHORD": "realchord",  # For "REAL CHORD" in cc_midis
            "Real Chords": "realchord",
            "BASS": "bass",
            "Bass": "bass",
            "MASTER VOLUME": "master",
            "MASTER": "master"
        }
        
        self._initialized = True
        self.__logger.info("KetronVolumeManager initialized")
    
    # Property getter for MIDI output channel
    @property
    def midi_out_channel(self) -> int:
        """Get the MIDI output channel (1-16)"""
        with self._volume_lock:
            return self._midi_out_channel
    
    # Property getter/setter for last pressed key name
    @property
    def last_pressed_key_name(self) -> Optional[str]:
        """Get the last pressed button key_name"""
        with self._volume_lock:
            return self._last_pressed_key_name
    
    def set_last_pressed_key_name(self, key_name: Optional[str]):
        """
        Set the last pressed button key_name.
        
        Args:
            key_name: The key_name from the pressed button (e.g., "LOWERS", "VOICE1", etc.)
                     or None to clear
        """
        with self._volume_lock:
            self._last_pressed_key_name = key_name
        if key_name:
            self.__logger.debug(f"Set last pressed key_name to: {key_name}")
        else:
            self.__logger.debug("Cleared last pressed key_name")
    
    # Property getters for all volumes
    @property
    def lower(self) -> int:
        """Get the lower volume (0-127)"""
        with self._volume_lock:
            return self._lower
    
    @property
    def voice1(self) -> int:
        """Get the voice1 volume (0-127)"""
        with self._volume_lock:
            return self._voice1
    
    @property
    def voice2(self) -> int:
        """Get the voice2 volume (0-127)"""
        with self._volume_lock:
            return self._voice2
    
    @property
    def drawbars(self) -> int:
        """Get the drawbars volume (0-127)"""
        with self._volume_lock:
            return self._drawbars
    
    @property
    def style(self) -> int:
        """Get the style volume (0-127)"""
        with self._volume_lock:
            return self._style
    
    @property
    def drum(self) -> int:
        """Get the drum volume (0-127)"""
        with self._volume_lock:
            return self._drum
    
    @property
    def chord(self) -> int:
        """Get the chord volume (0-127)"""
        with self._volume_lock:
            return self._chord
    
    @property
    def realchord(self) -> int:
        """Get the realchord volume (0-127)"""
        with self._volume_lock:
            return self._realchord
    
    @property
    def bass(self) -> int:
        """Get the bass volume (0-127)"""
        with self._volume_lock:
            return self._bass
    
    @property
    def master(self) -> int:
        """Get the master volume (0-127)"""
        with self._volume_lock:
            return self._master
    
    def _clamp_volume(self, value: int) -> int:
        """Clamp volume value to valid range (0-127)"""
        return max(self._MIN_VOLUME, min(self._MAX_VOLUME, value))
    
    def _clamp_channel(self, value: int) -> int:
        """Clamp MIDI channel value to valid range (1-16)"""
        return max(1, min(16, value))
    
    def _send_midi_cc_for_volume(self, volume_name: str, volume_value: int, port_name: Optional[str] = None) -> bool:
        """
        Send MIDI CC command for a volume change based on last pressed key.
        
        Args:
            volume_name: Name of the volume variable ('lower', 'voice1', etc.)
            volume_value: The new volume value (0-127)
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            True if CC was sent successfully, False otherwise
        """
        # Get the last pressed key_name
        key_name = self.last_pressed_key_name
        
        if not key_name:
            self.__logger.debug("No last pressed key_name set, skipping MIDI CC send")
            return False
        
        # Look up the key_name in cc_midis (case-insensitive)
        matched_key = None
        for cc_key in self.ketron_midi.cc_midis.keys():
            if cc_key.upper() == key_name.upper():
                matched_key = cc_key
                break
        
        if matched_key is None:
            self.__logger.warning(f"Key name '{key_name}' not found in cc_midis, cannot send MIDI CC")
            return False
        
        # Get the CC control number
        cc_control = self.ketron_midi.cc_midis[matched_key]
        
        # Verify the key_name maps to the correct volume
        # Convert to uppercase for lookup since _key_name_to_volume uses uppercase keys
        expected_volume_name = self._key_name_to_volume.get(matched_key.upper())
        if expected_volume_name != volume_name:
            self.__logger.warning(
                f"Key name '{matched_key}' maps to volume '{expected_volume_name}', "
                f"but trying to update '{volume_name}'. MIDI CC may be incorrect."
            )
        
        # All MIDI CC volume commands are sent on the configured MIDI output channel
        # Convert from 1-16 (property) to 0-15 (MidiManager format)
        # CircuitPython uses channel 15 (0-indexed) = channel 16 (1-indexed)
        midi_channel = self.midi_out_channel - 1  # Convert from 1-based (16) to 0-based (15)
        
        # Send the MIDI CC command
        success = self.midi_manager.send_cc(cc_control, volume_value, midi_channel, port_name)
        
        if success:
            self.__logger.info(
                f"Sent MIDI CC: control={cc_control} (0x{cc_control:02X}), "
                f"value={volume_value}, channel={self.midi_out_channel} "
                f"for key_name='{matched_key}' -> volume='{volume_name}'"
            )
        else:
            # Check if mido is available - if not, this is expected in test environments
            try:
                import mido
                mido_available = mido is not None
            except ImportError:
                mido_available = False
            
            if not mido_available:
                # mido not installed - this is expected in test environments, use debug level
                self.__logger.debug(
                    f"MIDI CC not sent (mido library not available): control={cc_control}, "
                    f"value={volume_value}, channel={self.midi_out_channel} for key_name='{matched_key}'"
                )
            else:
                # mido is available but send failed - this is a real error
                self.__logger.error(
                    f"Failed to send MIDI CC: control={cc_control}, value={volume_value}, "
                    f"channel={self.midi_out_channel} for key_name='{matched_key}'"
                )
        
        return success
    
    def _set_volume(self, volume_name: str, value: int):
        """Internal method to set a volume value"""
        value = self._clamp_volume(value)
        with self._volume_lock:
            setattr(self, f"_{volume_name}", value)
        self.__logger.debug(f"Set {volume_name} volume to {value}")
    
    def _get_volume(self, volume_name: str) -> int:
        """Internal method to get a volume value"""
        with self._volume_lock:
            return getattr(self, f"_{volume_name}")
    
    # Lower volume methods
    def increment_lower(self, amount: int = 1, port_name: Optional[str] = None) -> int:
        """
        Increment the lower volume and send MIDI CC command.
        
        Args:
            amount: Amount to increment by (default: 1)
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0-127)
        """
        current = self._get_volume("lower")
        new_value = self._clamp_volume(current + amount)
        self._set_volume("lower", new_value)
        self._send_midi_cc_for_volume("lower", new_value, port_name)
        return new_value
    
    def decrement_lower(self, amount: int = 1, port_name: Optional[str] = None) -> int:
        """
        Decrement the lower volume and send MIDI CC command.
        
        Args:
            amount: Amount to decrement by (default: 1)
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0-127)
        """
        current = self._get_volume("lower")
        new_value = self._clamp_volume(current - amount)
        self._set_volume("lower", new_value)
        self._send_midi_cc_for_volume("lower", new_value, port_name)
        return new_value
    
    def mute_lower(self, port_name: Optional[str] = None) -> int:
        """
        Mute the lower volume (set to 0) and send MIDI CC command.
        
        Args:
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0)
        """
        self._set_volume("lower", 0)
        self._send_midi_cc_for_volume("lower", 0, port_name)
        return 0
    
    # Voice1 volume methods
    def increment_voice1(self, amount: int = 1, port_name: Optional[str] = None) -> int:
        """
        Increment the voice1 volume and send MIDI CC command.
        
        Args:
            amount: Amount to increment by (default: 1)
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0-127)
        """
        current = self._get_volume("voice1")
        new_value = self._clamp_volume(current + amount)
        self._set_volume("voice1", new_value)
        self._send_midi_cc_for_volume("voice1", new_value, port_name)
        return new_value
    
    def decrement_voice1(self, amount: int = 1, port_name: Optional[str] = None) -> int:
        """
        Decrement the voice1 volume and send MIDI CC command.
        
        Args:
            amount: Amount to decrement by (default: 1)
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0-127)
        """
        current = self._get_volume("voice1")
        new_value = self._clamp_volume(current - amount)
        self._set_volume("voice1", new_value)
        self._send_midi_cc_for_volume("voice1", new_value, port_name)
        return new_value
    
    def mute_voice1(self, port_name: Optional[str] = None) -> int:
        """
        Mute the voice1 volume (set to 0) and send MIDI CC command.
        
        Args:
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0)
        """
        self._set_volume("voice1", 0)
        self._send_midi_cc_for_volume("voice1", 0, port_name)
        return 0
    
    # Voice2 volume methods
    def increment_voice2(self, amount: int = 1, port_name: Optional[str] = None) -> int:
        """
        Increment the voice2 volume and send MIDI CC command.
        
        Args:
            amount: Amount to increment by (default: 1)
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0-127)
        """
        current = self._get_volume("voice2")
        new_value = self._clamp_volume(current + amount)
        self._set_volume("voice2", new_value)
        self._send_midi_cc_for_volume("voice2", new_value, port_name)
        return new_value
    
    def decrement_voice2(self, amount: int = 1, port_name: Optional[str] = None) -> int:
        """
        Decrement the voice2 volume and send MIDI CC command.
        
        Args:
            amount: Amount to decrement by (default: 1)
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0-127)
        """
        current = self._get_volume("voice2")
        new_value = self._clamp_volume(current - amount)
        self._set_volume("voice2", new_value)
        self._send_midi_cc_for_volume("voice2", new_value, port_name)
        return new_value
    
    def mute_voice2(self, port_name: Optional[str] = None) -> int:
        """
        Mute the voice2 volume (set to 0) and send MIDI CC command.
        
        Args:
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0)
        """
        self._set_volume("voice2", 0)
        self._send_midi_cc_for_volume("voice2", 0, port_name)
        return 0
    
    # Drawbars volume methods
    def increment_drawbars(self, amount: int = 1, port_name: Optional[str] = None) -> int:
        """
        Increment the drawbars volume and send MIDI CC command.
        
        Args:
            amount: Amount to increment by (default: 1)
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0-127)
        """
        current = self._get_volume("drawbars")
        new_value = self._clamp_volume(current + amount)
        self._set_volume("drawbars", new_value)
        self._send_midi_cc_for_volume("drawbars", new_value, port_name)
        return new_value
    
    def decrement_drawbars(self, amount: int = 1, port_name: Optional[str] = None) -> int:
        """
        Decrement the drawbars volume and send MIDI CC command.
        
        Args:
            amount: Amount to decrement by (default: 1)
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0-127)
        """
        current = self._get_volume("drawbars")
        new_value = self._clamp_volume(current - amount)
        self._set_volume("drawbars", new_value)
        self._send_midi_cc_for_volume("drawbars", new_value, port_name)
        return new_value
    
    def mute_drawbars(self, port_name: Optional[str] = None) -> int:
        """
        Mute the drawbars volume (set to 0) and send MIDI CC command.
        
        Args:
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0)
        """
        self._set_volume("drawbars", 0)
        self._send_midi_cc_for_volume("drawbars", 0, port_name)
        return 0
    
    # Style volume methods
    def increment_style(self, amount: int = 1, port_name: Optional[str] = None) -> int:
        """
        Increment the style volume and send MIDI CC command.
        
        Args:
            amount: Amount to increment by (default: 1)
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0-127)
        """
        current = self._get_volume("style")
        new_value = self._clamp_volume(current + amount)
        self._set_volume("style", new_value)
        self._send_midi_cc_for_volume("style", new_value, port_name)
        return new_value
    
    def decrement_style(self, amount: int = 1, port_name: Optional[str] = None) -> int:
        """
        Decrement the style volume and send MIDI CC command.
        
        Args:
            amount: Amount to decrement by (default: 1)
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0-127)
        """
        current = self._get_volume("style")
        new_value = self._clamp_volume(current - amount)
        self._set_volume("style", new_value)
        self._send_midi_cc_for_volume("style", new_value, port_name)
        return new_value
    
    def mute_style(self, port_name: Optional[str] = None) -> int:
        """
        Mute the style volume (set to 0) and send MIDI CC command.
        
        Args:
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0)
        """
        self._set_volume("style", 0)
        self._send_midi_cc_for_volume("style", 0, port_name)
        return 0
    
    # Drum volume methods
    def increment_drum(self, amount: int = 1, port_name: Optional[str] = None) -> int:
        """
        Increment the drum volume and send MIDI CC command.
        
        Args:
            amount: Amount to increment by (default: 1)
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0-127)
        """
        current = self._get_volume("drum")
        new_value = self._clamp_volume(current + amount)
        self._set_volume("drum", new_value)
        self._send_midi_cc_for_volume("drum", new_value, port_name)
        return new_value
    
    def decrement_drum(self, amount: int = 1, port_name: Optional[str] = None) -> int:
        """
        Decrement the drum volume and send MIDI CC command.
        
        Args:
            amount: Amount to decrement by (default: 1)
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0-127)
        """
        current = self._get_volume("drum")
        new_value = self._clamp_volume(current - amount)
        self._set_volume("drum", new_value)
        self._send_midi_cc_for_volume("drum", new_value, port_name)
        return new_value
    
    def mute_drum(self, port_name: Optional[str] = None) -> int:
        """
        Mute the drum volume (set to 0) and send MIDI CC command.
        
        Args:
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0)
        """
        self._set_volume("drum", 0)
        self._send_midi_cc_for_volume("drum", 0, port_name)
        return 0
    
    # Chord volume methods
    def increment_chord(self, amount: int = 1, port_name: Optional[str] = None) -> int:
        """
        Increment the chord volume and send MIDI CC command.
        
        Args:
            amount: Amount to increment by (default: 1)
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0-127)
        """
        current = self._get_volume("chord")
        new_value = self._clamp_volume(current + amount)
        self._set_volume("chord", new_value)
        self._send_midi_cc_for_volume("chord", new_value, port_name)
        return new_value
    
    def decrement_chord(self, amount: int = 1, port_name: Optional[str] = None) -> int:
        """
        Decrement the chord volume and send MIDI CC command.
        
        Args:
            amount: Amount to decrement by (default: 1)
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0-127)
        """
        current = self._get_volume("chord")
        new_value = self._clamp_volume(current - amount)
        self._set_volume("chord", new_value)
        self._send_midi_cc_for_volume("chord", new_value, port_name)
        return new_value
    
    def mute_chord(self, port_name: Optional[str] = None) -> int:
        """
        Mute the chord volume (set to 0) and send MIDI CC command.
        
        Args:
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0)
        """
        self._set_volume("chord", 0)
        self._send_midi_cc_for_volume("chord", 0, port_name)
        return 0
    
    # Realchord volume methods
    def increment_realchord(self, amount: int = 1, port_name: Optional[str] = None) -> int:
        """
        Increment the realchord volume and send MIDI CC command.
        
        Args:
            amount: Amount to increment by (default: 1)
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0-127)
        """
        current = self._get_volume("realchord")
        new_value = self._clamp_volume(current + amount)
        self._set_volume("realchord", new_value)
        self._send_midi_cc_for_volume("realchord", new_value, port_name)
        return new_value
    
    def decrement_realchord(self, amount: int = 1, port_name: Optional[str] = None) -> int:
        """
        Decrement the realchord volume and send MIDI CC command.
        
        Args:
            amount: Amount to decrement by (default: 1)
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0-127)
        """
        current = self._get_volume("realchord")
        new_value = self._clamp_volume(current - amount)
        self._set_volume("realchord", new_value)
        self._send_midi_cc_for_volume("realchord", new_value, port_name)
        return new_value
    
    def mute_realchord(self, port_name: Optional[str] = None) -> int:
        """
        Mute the realchord volume (set to 0) and send MIDI CC command.
        
        Args:
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0)
        """
        self._set_volume("realchord", 0)
        self._send_midi_cc_for_volume("realchord", 0, port_name)
        return 0
    
    # Bass volume methods
    def increment_bass(self, amount: int = 1, port_name: Optional[str] = None) -> int:
        """
        Increment the bass volume and send MIDI CC command.
        
        Args:
            amount: Amount to increment by (default: 1)
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0-127)
        """
        current = self._get_volume("bass")
        new_value = self._clamp_volume(current + amount)
        self._set_volume("bass", new_value)
        self._send_midi_cc_for_volume("bass", new_value, port_name)
        return new_value
    
    def decrement_bass(self, amount: int = 1, port_name: Optional[str] = None) -> int:
        """
        Decrement the bass volume and send MIDI CC command.
        
        Args:
            amount: Amount to decrement by (default: 1)
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0-127)
        """
        current = self._get_volume("bass")
        new_value = self._clamp_volume(current - amount)
        self._set_volume("bass", new_value)
        self._send_midi_cc_for_volume("bass", new_value, port_name)
        return new_value
    
    def mute_bass(self, port_name: Optional[str] = None) -> int:
        """
        Mute the bass volume (set to 0) and send MIDI CC command.
        
        Args:
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0)
        """
        self._set_volume("bass", 0)
        self._send_midi_cc_for_volume("bass", 0, port_name)
        return 0
    
    # Master volume methods
    def increment_master(self, amount: int = 1, port_name: Optional[str] = None) -> int:
        """
        Increment the master volume and send MIDI CC Expression (0x07) command.
        
        Args:
            amount: Amount to increment by (default: 1)
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0-127)
        """
        current = self._get_volume("master")
        new_value = self._clamp_volume(current + amount)
        self._set_volume("master", new_value)
        self._send_master_expression_cc(new_value, port_name)
        return new_value
    
    def decrement_master(self, amount: int = 1, port_name: Optional[str] = None) -> int:
        """
        Decrement the master volume and send MIDI CC Expression (0x07) command.
        
        Args:
            amount: Amount to decrement by (default: 1)
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0-127)
        """
        current = self._get_volume("master")
        new_value = self._clamp_volume(current - amount)
        self._set_volume("master", new_value)
        self._send_master_expression_cc(new_value, port_name)
        return new_value
    
    def mute_master(self, port_name: Optional[str] = None) -> int:
        """
        Mute the master volume (set to 0) and send MIDI CC Expression (0x07) command.
        
        Args:
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0)
        """
        self._set_volume("master", 0)
        self._send_master_expression_cc(0, port_name)
        return 0
    
    def _send_master_expression_cc(self, volume_value: int, port_name: Optional[str] = None) -> bool:
        """
        Send MIDI CC Expression (0x07) command for master volume.
        
        Args:
            volume_value: The master volume value (0-127)
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            True if CC was sent successfully, False otherwise
        """
        expression_cc = 0x07  # MIDI CC 7 = Expression
        # Convert from 1-16 (property) to 0-15 (MidiManager format)
        # CircuitPython uses channel 15 (0-indexed) = channel 16 (1-indexed)
        midi_channel = self.midi_out_channel - 1  # Convert from 1-based (16) to 0-based (15)
        
        # Send the MIDI CC command
        success = self.midi_manager.send_cc(expression_cc, volume_value, midi_channel, port_name)
        
        if success:
            self.__logger.info(
                f"Sent Master Volume Expression CC: control={expression_cc} (0x{expression_cc:02X}), "
                f"value={volume_value}, channel={self.midi_out_channel}"
            )
        else:
            # Check if mido is available - if not, this is expected in test environments
            try:
                import mido
                mido_available = mido is not None
            except ImportError:
                mido_available = False
            
            if not mido_available:
                # mido not installed - this is expected in test environments, use debug level
                self.__logger.debug(
                    f"Master Volume Expression CC not sent (mido library not available): control={expression_cc}, "
                    f"value={volume_value}, channel={self.midi_out_channel}"
                )
            else:
                # mido is available but send failed - this is a real error
                self.__logger.error(
                    f"Failed to send Master Volume Expression CC: control={expression_cc}, value={volume_value}, "
                    f"channel={self.midi_out_channel}"
                )
        
        return success
    
    def get_all_volumes(self) -> dict:
        """
        Get all volume levels as a dictionary.
        
        Returns:
            Dictionary with all volume levels
        """
        return {
            'lower': self.lower,
            'voice1': self.voice1,
            'voice2': self.voice2,
            'drawbars': self.drawbars,
            'style': self.style,
            'drum': self.drum,
            'chord': self.chord,
            'realchord': self.realchord,
            'bass': self.bass,
            'master': self.master
        }
    
    def set_volume(self, volume_name: str, value: int) -> int:
        """
        Set a specific volume by name.
        
        Args:
            volume_name: Name of the volume ('lower', 'voice1', 'voice2', 'drawbars', 
                         'style', 'drum', 'chord', 'realchord')
            value: Volume value (0-127)
        
        Returns:
            New volume value (clamped to 0-127)
        
        Raises:
            ValueError: If volume_name is not recognized
        """
        valid_names = ['lower', 'voice1', 'voice2', 'drawbars', 'style', 'drum', 'chord', 'realchord', 'bass', 'master']
        if volume_name not in valid_names:
            raise ValueError(f"Invalid volume name: {volume_name}. Must be one of {valid_names}")
        
        self._set_volume(volume_name, value)
        return self._get_volume(volume_name)
    
    def set_midi_out_channel(self, channel: int) -> int:
        """
        Set the MIDI output channel.
        
        Args:
            channel: MIDI channel number (1-16)
        
        Returns:
            New channel value (clamped to 1-16)
        """
        channel = self._clamp_channel(channel)
        with self._volume_lock:
            self._midi_out_channel = channel
        self.__logger.info(f"Set MIDI output channel to {channel}")
        return channel
    
    def increment_last_pressed_volume(self, amount: int = 1, port_name: Optional[str] = None) -> Optional[int]:
        """
        Increment the volume for the last pressed volume key.
        
        Args:
            amount: Amount to increment by (default: 1)
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0-127) if successful, None if no last pressed key or invalid key
        """
        key_name = self.last_pressed_key_name
        if not key_name:
            self.__logger.warning("No last pressed volume key set, cannot increment")
            return None
        
        # Map key_name to volume variable name
        volume_name = self._key_name_to_volume.get(key_name.upper())
        if not volume_name:
            self.__logger.warning(f"Key name '{key_name}' does not map to a volume variable")
            return None
        
        # Special handling for master volume (uses Expression CC instead of regular CC)
        if volume_name == "master":
            return self.increment_master(amount, port_name)
        
        # Call the appropriate increment method for other volumes
        method_name = f"increment_{volume_name}"
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            return method(amount, port_name)
        else:
            self.__logger.error(f"Increment method '{method_name}' not found for volume '{volume_name}'")
            return None
    
    def decrement_last_pressed_volume(self, amount: int = 1, port_name: Optional[str] = None) -> Optional[int]:
        """
        Decrement the volume for the last pressed volume key.
        
        Args:
            amount: Amount to decrement by (default: 1)
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0-127) if successful, None if no last pressed key or invalid key
        """
        key_name = self.last_pressed_key_name
        if not key_name:
            self.__logger.warning("No last pressed volume key set, cannot decrement")
            return None
        
        # Map key_name to volume variable name
        volume_name = self._key_name_to_volume.get(key_name.upper())
        if not volume_name:
            self.__logger.warning(f"Key name '{key_name}' does not map to a volume variable")
            return None
        
        # Special handling for master volume (uses Expression CC instead of regular CC)
        if volume_name == "master":
            return self.decrement_master(amount, port_name)
        
        # Call the appropriate decrement method for other volumes
        method_name = f"decrement_{volume_name}"
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            return method(amount, port_name)
        else:
            self.__logger.error(f"Decrement method '{method_name}' not found for volume '{volume_name}'")
            return None
    
    def toggle_mute_last_pressed_volume(self, port_name: Optional[str] = None) -> Optional[int]:
        """
        Toggle mute for the last pressed volume key.
        - If volume is 0 (muted), restore to 80
        - If volume is not 0, mute it (set to 0)
        
        Args:
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            New volume value (0 or 80) if successful, None if no last pressed key or invalid key
        """
        key_name = self.last_pressed_key_name
        if not key_name:
            self.__logger.warning("No last pressed volume key set, cannot toggle mute")
            return None
        
        # Map key_name to volume variable name
        volume_name = self._key_name_to_volume.get(key_name.upper())
        if not volume_name:
            self.__logger.warning(f"Key name '{key_name}' does not map to a volume variable")
            return None
        
        # Get current volume
        current_volume = self._get_volume(volume_name)
        
        # Toggle: if muted (0), restore to 80; otherwise mute (set to 0)
        if current_volume == 0:
            # Restore to 80
            new_volume = 80
            self._set_volume(volume_name, new_volume)
            # Special handling for master volume (uses Expression CC)
            if volume_name == "master":
                self._send_master_expression_cc(new_volume, port_name)
            else:
                self._send_midi_cc_for_volume(volume_name, new_volume, port_name)
            self.__logger.info(f"Unmuted {volume_name} (restored to {new_volume})")
        else:
            # Mute (set to 0)
            new_volume = 0
            self._set_volume(volume_name, new_volume)
            # Special handling for master volume (uses Expression CC)
            if volume_name == "master":
                self._send_master_expression_cc(new_volume, port_name)
            else:
                self._send_midi_cc_for_volume(volume_name, new_volume, port_name)
            self.__logger.info(f"Muted {volume_name} (set to {new_volume})")
        
        return new_volume

