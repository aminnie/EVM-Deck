"""
Ketron Key Mapping Control for sending MIDI messages based on key_mappings.json.

This control loads key mappings from key_mappings.json and sends the appropriate
MIDI messages (pedal, tab, or CC) when a Stream Deck key is pressed.
"""

import json
import logging
import os
from pathlib import Path

from devdeck_core.controls.deck_control import DeckControl
from devdeck.controls.base_control import BaseDeckControl
from devdeck.ketron import KetronMidi, COLOR_MAP, KetronVolumeManager
from devdeck.midi import MidiManager
from devdeck.controls.text_control import wrap_text_to_lines


class KetronKeyMappingControl(BaseDeckControl):
    """
    Control that sends Ketron MIDI messages based on key_mappings.json.
    
    When a key is pressed, this control:
    1. Looks up the key_no in key_mappings.json
    2. Uses key_name and source_list_name to determine the MIDI message type
    3. Sends the appropriate message:
       - pedal_midis -> send_pedal_command()
       - tab_midis -> send_tab_command()
       - cc_midis -> send_cc()
    
    Settings:
        key_mappings_file: Path to key_mappings.json (optional, defaults to config/key_mappings.json)
        port: MIDI port name (optional, uses first available if not specified)
        cc_value: CC value to send for cc_midis (optional, default: 64)
        cc_channel: MIDI channel for CC messages (optional, default: 0)
    """
    
    _key_mappings_cache = None
    _key_mappings_file = None
    _key_mappings_mtime = None  # File modification time for cache invalidation
    
    def __init__(self, key_no, **kwargs):
        self.__logger = logging.getLogger('devdeck')
        self.key_no = key_no  # Store key_no explicitly
        self.ketron_midi = KetronMidi()
        self.midi_manager = MidiManager()
        self.volume_manager = KetronVolumeManager()
        self.key_mapping = None
        super().__init__(key_no, **kwargs)
    
    @classmethod
    def _load_key_mappings(cls, key_mappings_file=None):
        """
        Load key mappings from JSON file with caching.
        
        Args:
            key_mappings_file: Path to key_mappings.json file
        
        Returns:
            Dictionary mapping key_no to mapping data, or None if file not found
        """
        # Use cached data if file hasn't changed
        if cls._key_mappings_cache is not None and cls._key_mappings_file == key_mappings_file:
            # Check if file was modified by comparing modification times
            if key_mappings_file is not None:
                key_mappings_path = Path(key_mappings_file) if isinstance(key_mappings_file, str) else key_mappings_file
                if key_mappings_path.exists():
                    current_mtime = key_mappings_path.stat().st_mtime
                    if cls._key_mappings_mtime is not None and current_mtime == cls._key_mappings_mtime:
                        return cls._key_mappings_cache
                    # File was modified, clear cache
                    cls._key_mappings_cache = None
                    cls._key_mappings_mtime = None
                else:
                    # File no longer exists, clear cache
                    cls._key_mappings_cache = None
                    cls._key_mappings_file = None
                    cls._key_mappings_mtime = None
                    return None
            else:
                # No file specified, return cached data if available
                return cls._key_mappings_cache
        
        if key_mappings_file is None:
            # Try to find key_mappings.json in config directory (preferred location)
            # Path is now: devdeck/ketron/controls/ketron_key_mapping_control.py
            # Need to go up 4 levels to get to project root
            project_root = Path(__file__).parent.parent.parent.parent
            key_mappings_file = project_root / 'config' / 'key_mappings.json'
            
            # Fallback to project root
            if not key_mappings_file.exists():
                key_mappings_file = project_root / 'key_mappings.json'
        
        # Convert to Path if it's a string
        if isinstance(key_mappings_file, str):
            key_mappings_file = Path(key_mappings_file)
        
        # Validate path to prevent directory traversal attacks
        if key_mappings_file is not None:
            try:
                # Resolve path to prevent directory traversal
                key_mappings_file = key_mappings_file.resolve()
                # Check if path exists
                if not key_mappings_file.exists():
                    return None
                # Additional validation: ensure it's a file (not a directory)
                if not key_mappings_file.is_file():
                    logger = logging.getLogger('devdeck')
                    logger.error("Key mappings path is not a file: %s", key_mappings_file)
                    return None
            except (OSError, ValueError) as e:
                logger = logging.getLogger('devdeck')
                logger.error("Invalid key mappings file path %s: %s", key_mappings_file, e)
                return None
        else:
            return None
        
        try:
            # Try UTF-16 first (Windows default), then UTF-8
            try:
                with open(key_mappings_file, 'r', encoding='utf-16') as f:
                    content = f.read().strip()
            except (UnicodeDecodeError, UnicodeError):
                with open(key_mappings_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
            
            if not content:
                return None
            
            key_mappings_data = json.loads(content)
            
            # Handle both named structure {"key_mappings": [...]} and direct array [...]
            if isinstance(key_mappings_data, dict) and 'key_mappings' in key_mappings_data:
                key_mappings = key_mappings_data['key_mappings']
            elif isinstance(key_mappings_data, list):
                key_mappings = key_mappings_data
            else:
                return None
            
            # Create a dictionary for quick lookup: key_no -> mapping
            mappings_dict = {mapping['key_no']: mapping for mapping in key_mappings}
            
            # Cache the result along with file modification time
            cls._key_mappings_cache = mappings_dict
            cls._key_mappings_file = key_mappings_file
            cls._key_mappings_mtime = key_mappings_file.stat().st_mtime
            
            return mappings_dict
            
        except Exception as e:
            logger = logging.getLogger('devdeck')
            logger.error(f"Error loading key mappings from {key_mappings_file}: {e}")
            return None
    
    def _get_key_mapping(self):
        """Get the mapping for this control's key_no"""
        key_mappings_file = self.settings.get('key_mappings_file')
        mappings = self._load_key_mappings(key_mappings_file)
        
        if mappings is None:
            return None
        
        # Use offset_key_no if available (for SecondPageDeckController which maps keys 0-14 to mappings 15-29)
        lookup_key = getattr(self, 'offset_key_no', self.key_no)
        
        return mappings.get(lookup_key)
    
    def initialize(self):
        """Initialize the control and render the key"""
        # Load the mapping for this key
        # Note: offset_key_no may be set by SecondPageDeckController after this,
        # so we'll re-fetch in pressed() to ensure correct mapping
        self.key_mapping = self._get_key_mapping()
        
        # Configure MIDI output channel for volume CC messages if specified
        # This can be set at the deck level (in deck settings) or control level
        midi_channel = self.settings.get('midi_channel')
        if midi_channel is not None:
            # Convert from 1-16 to 1-16 (validate range)
            if 1 <= midi_channel <= 16:
                self.volume_manager.set_midi_out_channel(midi_channel)
                self.__logger.info(f"Configured MIDI output channel to {midi_channel} (from settings)")
            else:
                self.__logger.warning(f"Invalid MIDI channel {midi_channel}, must be 1-16. Using default channel 16.")
        
        # Open MIDI port if specified or if no ports are open
        port_name = self.settings.get('port')
        
        if not self.midi_manager.is_port_open(port_name):
            if port_name:
                self.__logger.info(f"Opening MIDI port: {port_name}")
            else:
                self.__logger.info("Opening first available MIDI port")
            
            if not self.midi_manager.open_port(port_name):
                self.__logger.error("Failed to open MIDI port")
                self._render_error("MIDI\nPORT\nERROR")
                return
        
        # Render the control
        self._render()
    
    def _render(self):
        """Render the control with text and colors from key_mappings.json"""
        with self.deck_context() as context:
            with context.renderer() as r:
                if self.key_mapping is None:
                    # No mapping found, render error
                    r.text("NO\nMAP")\
                        .font_size(100)\
                        .color('red')\
                        .center_vertically()\
                        .center_horizontally()\
                        .end()
                    return
                
                # Get text and colors from mapping
                key_name = self.key_mapping.get('key_name', '')
                text_color = self.key_mapping.get('text_color', 'white')
                background_color = self.key_mapping.get('background_color', 'black')
                
                # Wrap text to maximum 6 characters per line
                wrapped_text = wrap_text_to_lines(key_name, max_chars_per_line=6)
                # Convert \n escape sequences to actual newlines for rendering
                wrapped_text = wrapped_text.replace('\\n', '\n')
                
                # Map custom color names to hex values
                standard_colors = {'blue', 'green', 'red', 'yellow', 'orange', 'purple', 'white', 'black', 'grey', 'gray', 'cyan', 'magenta', 'pink', 'brown', 'teal', 'navy', 'maroon', 'lime', 'silver', 'gold', 'lightblue', 'lightgreen', 'lightgray', 'darkblue', 'darkgreen', 'darkred'}
                
                if background_color.lower() not in standard_colors:
                    # It's a custom color name, check COLOR_MAP
                    if background_color in COLOR_MAP:
                        hex_value = COLOR_MAP[background_color]
                        background_color = f"#{hex_value:06X}"
                    elif background_color.lower() in COLOR_MAP:
                        hex_value = COLOR_MAP[background_color.lower()]
                        background_color = f"#{hex_value:06X}"
                
                r.background_color(background_color)
                r.text(wrapped_text)\
                    .font_size(100)\
                    .color(text_color)\
                    .center_vertically()\
                    .center_horizontally()\
                    .end()
    
    def _find_key_in_dict(self, key_name, dictionary):
        """
        Find a key in a dictionary with case-insensitive matching.
        
        Args:
            key_name: The key name to find
            dictionary: The dictionary to search in
        
        Returns:
            The matching key from the dictionary, or None if not found
        """
        # Try exact match first
        if key_name in dictionary:
            return key_name
        
        # Try case-insensitive match
        key_name_lower = key_name.lower()
        for dict_key in dictionary.keys():
            if dict_key.lower() == key_name_lower:
                return dict_key
        
        return None
    
    def pressed(self):
        """Send MIDI message when key is pressed"""
        # Re-fetch the mapping in case offset_key_no was set after initialize()
        # This ensures SecondPageDeckController uses the correct offset
        lookup_key = getattr(self, 'offset_key_no', self.key_no)
        self.__logger.info(f"KetronKeyMappingControl.pressed() called for key {self.key_no} (lookup_key: {lookup_key}, offset_key_no: {getattr(self, 'offset_key_no', 'not set')})")
        
        self.key_mapping = self._get_key_mapping()
        
        if self.key_mapping is None:
            # Log with offset info for debugging
            self.__logger.warning(f"No mapping found for key {self.key_no} (lookup_key: {lookup_key}, offset_key_no: {getattr(self, 'offset_key_no', 'not set')})")
            return
        
        # Log which mapping is being used (for debugging)
        self.__logger.info(f"Key {self.key_no} pressed, using mapping from key_mappings[{lookup_key}]: {self.key_mapping.get('key_name', 'N/A')}")
        
        key_name = self.key_mapping.get('key_name', '').strip()
        source_list_name = self.key_mapping.get('source_list_name', '')
        port_name = self.settings.get('port')
        
        # Skip if key_name is empty or just whitespace
        if not key_name:
            self.__logger.debug(f"Key {self.key_no} has empty key_name, skipping MIDI send")
            return
        
        # Special handling for Volume Up, Volume Down, and Mute buttons
        # These work regardless of source_list_name
        if key_name.upper() == "VOLUME UP":
            # Increment the last pressed volume
            new_volume = self.volume_manager.increment_last_pressed_volume(port_name=port_name)
            if new_volume is None:
                self.__logger.warning("Volume Up pressed but no last pressed volume key set")
                self._render_error("NO\nVOLUME\nSELECTED")
            else:
                self.__logger.info(f"Volume Up: incremented to {new_volume}")
            return
        
        elif key_name.upper() == "VOLUME DOWN":
            # Decrement the last pressed volume
            new_volume = self.volume_manager.decrement_last_pressed_volume(port_name=port_name)
            if new_volume is None:
                self.__logger.warning("Volume Down pressed but no last pressed volume key set")
                self._render_error("NO\nVOLUME\nSELECTED")
            else:
                self.__logger.info(f"Volume Down: decremented to {new_volume}")
            return
        
        elif key_name.upper() == "MUTE":
            # Toggle mute for the last pressed volume
            new_volume = self.volume_manager.toggle_mute_last_pressed_volume(port_name=port_name)
            if new_volume is None:
                self.__logger.warning("Mute pressed but no last pressed volume key set")
                self._render_error("NO\nVOLUME\nSELECTED")
            else:
                if new_volume == 0:
                    self.__logger.info(f"Mute: muted volume (set to {new_volume})")
                else:
                    self.__logger.info(f"Mute: unmuted volume (restored to {new_volume})")
            return
        
        elif key_name.upper() == "MASTER VOLUME":
            # Track this as the last pressed volume key for volume manager
            # This allows increment/decrement to know which volume to adjust
            self.volume_manager.set_last_pressed_key_name("MASTER VOLUME")
            self.__logger.debug(f"Tracked last pressed volume key: MASTER VOLUME for key {self.key_no}")
            
            # Send MIDI CC 0x07 (Expression) on channel 16 with current master volume value
            master_volume = self.volume_manager.master
            expression_cc = 0x07  # MIDI CC 7 = Expression
            cc_channel = 15  # Channel 16 (0-indexed: 15)
            
            success = self.midi_manager.send_cc(expression_cc, master_volume, cc_channel, port_name)
            if not success:
                self.__logger.error(f"Failed to send Master Volume CC: control={expression_cc}, value={master_volume}, channel=16")
                self._render_error("SEND\nFAILED")
            else:
                self.__logger.info(f"Sent Master Volume CC: control={expression_cc} (Expression), value={master_volume}, channel=16 for key {self.key_no}")
            return
        
        try:
            if source_list_name == 'pedal_midis':
                # Find the matching key (case-insensitive)
                matched_key = self._find_key_in_dict(key_name, self.ketron_midi.pedal_midis)
                if matched_key is None:
                    self.__logger.error(f"Key name '{key_name}' not found in pedal_midis for key {self.key_no}")
                    self._render_error("INVALID\nKEY")
                    return
                
                # Send pedal command
                success = self.ketron_midi.send_pedal_command(matched_key, port_name)
                if not success:
                    self.__logger.error(f"Failed to send pedal command '{matched_key}' for key {self.key_no}")
                    self._render_error("SEND\nFAILED")
                else:
                    self.__logger.info(f"Sent pedal command '{matched_key}' for key {self.key_no}")
            
            elif source_list_name == 'tab_midis':
                # Find the matching key (case-insensitive)
                matched_key = self._find_key_in_dict(key_name, self.ketron_midi.tab_midis)
                if matched_key is None:
                    self.__logger.error(f"Key name '{key_name}' not found in tab_midis for key {self.key_no}")
                    self._render_error("INVALID\nKEY")
                    return
                
                # Send tab command
                success = self.ketron_midi.send_tab_command(matched_key, port_name)
                if not success:
                    self.__logger.error(f"Failed to send tab command '{matched_key}' for key {self.key_no}")
                    self._render_error("SEND\nFAILED")
                else:
                    self.__logger.info(f"Sent tab command '{matched_key}' for key {self.key_no}")
            
            elif source_list_name == 'cc_midis':
                # For CC buttons, find the matching key (case-insensitive)
                matched_key = self._find_key_in_dict(key_name, self.ketron_midi.cc_midis)
                if matched_key is None:
                    self.__logger.error(f"Key name '{key_name}' not found in cc_midis for key {self.key_no}")
                    self._render_error("INVALID\nKEY")
                    return
                
                # Track this as the last pressed volume key for volume manager
                # This allows increment/decrement to know which volume to adjust
                self.volume_manager.set_last_pressed_key_name(matched_key)
                self.__logger.debug(f"Tracked last pressed volume key: {matched_key} for key {self.key_no}")
                
                cc_control = self.ketron_midi.cc_midis[matched_key]
                
                # Check if this is a volume button - if so, send current volume value on channel 16
                # Convert to uppercase for lookup since _key_name_to_volume uses uppercase keys
                volume_name = self.volume_manager._key_name_to_volume.get(matched_key.upper())
                if volume_name:
                    # This is a volume button - send current volume value on channel 16
                    # Use property getter to get current volume
                    current_volume = getattr(self.volume_manager, volume_name)
                    cc_value = current_volume
                    cc_channel = 15  # Channel 16 (0-indexed: 15)
                    self.__logger.debug(f"Volume button '{matched_key}' pressed - sending current volume {current_volume} on channel 16")
                else:
                    # Not a volume button - use settings or default
                    cc_value = self.settings.get('cc_value', 64)  # Default to middle value
                    cc_channel = self.settings.get('cc_channel', 0)
                
                success = self.midi_manager.send_cc(cc_control, cc_value, cc_channel, port_name)
                if not success:
                    self.__logger.error(f"Failed to send CC message: control={cc_control}, value={cc_value}, channel={cc_channel}")
                    self._render_error("SEND\nFAILED")
                else:
                    if volume_name:
                        self.__logger.info(f"Sent CC message: control={cc_control}, value={cc_value} (current {volume_name} volume), channel=16 for key {self.key_no}")
                    else:
                        self.__logger.info(f"Sent CC message: control={cc_control}, value={cc_value}, channel={cc_channel} for key {self.key_no}")
            
            else:
                self.__logger.error(f"Invalid source_list_name '{source_list_name}' for key {self.key_no}")
                self._render_error("INVALID\nSOURCE")
        
        except Exception as e:
            self.__logger.error(f"Error sending MIDI message for key {self.key_no}: {e}", exc_info=True)
            self._render_error("ERROR")
    
    def released(self):
        """Re-render on key release to ensure image stays visible"""
        self._render()
    
    def settings_schema(self):
        """Define the settings schema for KetronKeyMappingControl"""
        return {
            'key_mappings_file': {
                'type': 'string',
                'required': False
            },
            'port': {
                'type': 'string',
                'required': False
            },
            'cc_value': {
                'type': 'integer',
                'required': False,
                'min': 0,
                'max': 127
            },
            'cc_channel': {
                'type': 'integer',
                'required': False,
                'min': 0,
                'max': 15
            },
            # Allow TextControl settings for backward compatibility (they're ignored)
            'text': {
                'type': 'string',
                'required': False
            },
            'font_size': {
                'type': 'integer',
                'required': False
            },
            'color': {
                'type': 'string',
                'required': False
            },
            'background_color': {
                'type': 'string',
                'required': False
            }
        }

