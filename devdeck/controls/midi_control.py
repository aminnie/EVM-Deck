"""
MIDI Control for sending MIDI CC and SysEx messages from deck keys.

This control allows you to send MIDI Control Change (CC) or System Exclusive (SysEx)
messages when a deck key is pressed. It uses the MidiManager for port management.
"""

import logging
import os

from devdeck_core.controls.deck_control import DeckControl
from devdeck.midi_manager import MidiManager


class MidiControl(DeckControl):
    """
    Control that sends MIDI CC or SysEx messages when a key is pressed.
    
    Settings:
        type: 'cc' or 'sysex' (required)
        port: MIDI port name (optional, uses first available if not specified)
        
        For CC messages:
            control: CC number (0-127, required for type='cc')
            value: CC value (0-127, required for type='cc')
            channel: MIDI channel (0-15, optional, default: 0)
        
        For SysEx messages:
            data: List of bytes (0-127) for SysEx message (required for type='sysex')
            OR
            raw_data: List of bytes including 0xF0 and 0xF7 (alternative to data)
        
        icon: Path to icon file (optional)
    """
    
    def __init__(self, key_no, **kwargs):
        self.__logger = logging.getLogger('devdeck')
        self.midi_manager = MidiManager()
        super().__init__(key_no, **kwargs)
    
    def initialize(self):
        """Initialize the control and open MIDI port if needed"""
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
        """Render the control icon or text"""
        with self.deck_context() as context:
            with context.renderer() as r:
                # If icon is specified, use it
                if 'icon' in self.settings and self.settings['icon']:
                    icon_path = os.path.expanduser(self.settings['icon'])
                    if os.path.exists(icon_path):
                        r.image(icon_path).end()
                        return
                    else:
                        self.__logger.warning(f"Icon file not found: {icon_path}")
                
                # Otherwise, render text based on type
                msg_type = self.settings.get('type', 'cc').upper()
                if msg_type == 'CC':
                    control = self.settings.get('control', '?')
                    value = self.settings.get('value', '?')
                    text = f"CC\n{control}\n{value}"
                elif msg_type == 'SYSEX':
                    text = "SysEx"
                else:
                    text = "MIDI"
                
                r.text(text)\
                    .font_size(100)\
                    .color('white')\
                    .center_vertically()\
                    .center_horizontally()\
                    .end()
    
    def _render_error(self, error_text):
        """Render an error message"""
        with self.deck_context() as context:
            with context.renderer() as r:
                r.text(error_text)\
                    .font_size(70)\
                    .color('red')\
                    .center_vertically()\
                    .center_horizontally()\
                    .end()
    
    def pressed(self):
        """Send MIDI message when key is pressed"""
        msg_type = self.settings.get('type', 'cc').lower()
        port_name = self.settings.get('port')
        
        if msg_type == 'cc':
            self._send_cc(port_name)
        elif msg_type == 'sysex':
            self._send_sysex(port_name)
        else:
            self.__logger.error(f"Invalid MIDI message type: {msg_type}. Must be 'cc' or 'sysex'")
            self._render_error("INVALID\nTYPE")
    
    def _send_cc(self, port_name):
        """Send a MIDI CC message"""
        control = self.settings.get('control')
        value = self.settings.get('value')
        channel = self.settings.get('channel', 0)
        
        if control is None or value is None:
            self.__logger.error("CC message requires 'control' and 'value' settings")
            self._render_error("MISSING\nSETTINGS")
            return
        
        try:
            control = int(control)
            value = int(value)
            channel = int(channel)
        except (ValueError, TypeError) as e:
            self.__logger.error(f"Invalid CC parameters: {e}")
            self._render_error("INVALID\nPARAMS")
            return
        
        success = self.midi_manager.send_cc(control, value, channel, port_name)
        if not success:
            self.__logger.error(f"Failed to send CC message: control={control}, value={value}, channel={channel}")
            self._render_error("SEND\nFAILED")
    
    def _send_sysex(self, port_name):
        """Send a MIDI SysEx message"""
        # Check for raw_data first (includes 0xF0 and 0xF7)
        if 'raw_data' in self.settings:
            raw_data = self.settings['raw_data']
            if not isinstance(raw_data, list):
                self.__logger.error("SysEx 'raw_data' must be a list of integers")
                self._render_error("INVALID\nDATA")
                return
            
            try:
                raw_data = [int(b) for b in raw_data]
            except (ValueError, TypeError) as e:
                self.__logger.error(f"Invalid SysEx raw_data: {e}")
                self._render_error("INVALID\nDATA")
                return
            
            success = self.midi_manager.send_sysex_raw(raw_data, port_name)
        elif 'data' in self.settings:
            data = self.settings['data']
            if not isinstance(data, list):
                self.__logger.error("SysEx 'data' must be a list of integers")
                self._render_error("INVALID\nDATA")
                return
            
            try:
                data = [int(b) for b in data]
            except (ValueError, TypeError) as e:
                self.__logger.error(f"Invalid SysEx data: {e}")
                self._render_error("INVALID\nDATA")
                return
            
            success = self.midi_manager.send_sysex(data, port_name)
        else:
            self.__logger.error("SysEx message requires 'data' or 'raw_data' setting")
            self._render_error("MISSING\nDATA")
            return
        
        if not success:
            self.__logger.error("Failed to send SysEx message")
            self._render_error("SEND\nFAILED")
    
    def settings_schema(self):
        """Define the settings schema for MidiControl"""
        return {
            'type': {
                'type': 'string',
                'required': True,
                'allowed': ['cc', 'sysex']
            },
            'port': {
                'type': 'string',
                'required': False
            },
            'control': {
                'type': 'integer',
                'required': False,
                'min': 0,
                'max': 127
            },
            'value': {
                'type': 'integer',
                'required': False,
                'min': 0,
                'max': 127
            },
            'channel': {
                'type': 'integer',
                'required': False,
                'min': 0,
                'max': 15
            },
            'data': {
                'type': 'list',
                'required': False
            },
            'raw_data': {
                'type': 'list',
                'required': False
            },
            'icon': {
                'type': 'string',
                'required': False
            }
        }

