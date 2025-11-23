# Manage Control Panel Volume Sliders via midi CC

# Ketron SysEx message format constants
KETRON_SYSEX_MANUFACTURER_ID = 0x43  # Common MIDI manufacturer ID (may need adjustment for Ketron)
KETRON_SYSEX_DEVICE_ID = 0x00  # Device ID (0 = all devices or specific device)
KETRON_SYSEX_ON_VALUE = 0x7F  # Value for ON state (127)
KETRON_SYSEX_OFF_VALUE = 0x00  # Value for OFF state (0)


class SliderCC:
    PLAYER_CC = 0x66   #CC 102
    STYLE_CC = 0x67
    DRUM_CC = 0x68
    BASS_CC = 0x69
    CHORD_CC = 0x6A
    REALCHORD_CC = 0x6B
    LOWERS_CC = 0x6C
    USER2_CC = 0x6D
    USER3_CC = 0x6E
    VOICE1_CC = 0x72     #CC 114
    VOICE2_CC = 0x73
    DRAWBARS_CC = 0x74
    MICRO1_CC = 0x75
    VOCAL_CC = 0x76

class Colors:
    WHITE = 0x606060
    BLUE = 0x000020
    KETRON_BLUE = 0x0066CC  # RGB(0, 102, 204) - Bright brand blue
    GREEN = 0x002000
    BRIGHT_GREEN = 0x00FF00  # RGB(0, 255, 0) - Bright green
    RED = 0x200000
    ORANGE = 0x701E02
    PURPLE = 0x800080
    YELLOW = 0x808000
    TEAL = 0x004040
    OFFWHITE = 0xA47474

# Color mapping dictionary
COLOR_MAP = {
    'red': Colors.RED,
    'green': Colors.GREEN,
    'bright_green': Colors.BRIGHT_GREEN,
    'blue': Colors.BLUE,
    'ketron_blue': Colors.KETRON_BLUE,
    'purple': Colors.PURPLE,
    'yellow': Colors.YELLOW,
    'orange': Colors.ORANGE,
    'white': Colors.WHITE,
    'teal': Colors.TEAL,
    'offwhite': Colors.OFFWHITE
}

class KetronMidi:
    def __init__(self):
        # Ketron Pedal and Tab MIDI lookup dictionaries
        self.pedal_midis = self._init_pedal_midis()
        self.tab_midis = self._init_tab_midis()
        self.cc_midis = self._init_cc_midis()

        self._build_cache()

    def _build_cache(self):
        """Build lookup cache - placeholder for compatibility"""
        # This method can be used for caching lookups if needed
        # For now, it's a no-op to maintain compatibility
        pass

    def _init_pedal_midis(self):
        """Initialize pedal MIDI dictionary"""
        
        return {
            "Sustain": 0x00, "Soft": 0x01, "Sostenuto": 0x02, "Arr.A": 0x03,
            "Arr.B": 0x04, "Arr.C": 0x05, "Arr.D": 0x06, "Fill1": 0x07,
            "Fill2": 0x08, "Fill3": 0x09, "Fill4": 0x0A, "Break1": 0x0B,
            "Break2": 0x0C, "Break3": 0x0D, "Break4": 0x0E, "Intro/End1": 0x0F,
            "Intro/End2": 0x10, "Intro/End3": 0x11, "Start/Stop": 0x12,
            "Tempo Up": 0x13, "Tempo Down": 0x14, "Fill": 0x15, "Break": 0x16,
            "To End": 0x17, "Bass to Lowest": 0x18, "Bass to Root": 0x19,
            "Live Bass": 0x1A, "Acc.BassToChord": 0x1B, "Manual Bass": 0x1C,
            "Voice Lock Bass": 0x1D, "Bass Mono/Poly": 0x1E, "Dial Down": 0x1F,
            "Dial Up": 0x20, "Auto Fill": 0x21, "Fill to Arr.": 0x22,
            "After Fill": 0x23, "Low. Hold Start": 0x24, "Low. Hold Stop": 0x25,
            "Low. Hold Break": 0x26, "Low. Stop Mute": 0x27, "Low. Mute": 0x28,
            "Low. and Bass": 0x29, "Low. Voice Lock": 0x2A, "Pianist": 0x2B,
            "Pianist Auto/Stand.": 0x2C, "Pianist Sustain": 0x2D, "Bassist": 0x2E,
            "Bassist Easy/Exp.": 0x2F, "Key Start": 0x30, "Key Stop": 0x31,
            "Enter": 0x32, "Exit": 0x33, "Registration": 0x34, "Fade": 0x35,
            "Harmony": 0x36, "Octave Up": 0x37, "Octave Down": 0x38,
            "RestartCount In": 0x39, "Micro1 On/Off": 0x3A, "Micro1 Down": 0x3B,
            "Micro1 Up": 0x3C, "Voicetr.On/Off": 0x3D, "Voicetr.Down": 0x3E,
            "Voicetr.Up": 0x3F, "Micro2 On/Off": 0x40, "EFX1 On/Off": 0x41,
            "EFX2 On/Off": 0x42, "Arabic.Set1": 0x43, "Arabic.Set2": 0x44,
            "Arabic.Set3": 0x45, "Arabic.Set4": 0x46, "Dry On Stop": 0x47,
            "Pdf Page Down": 0x48, "Pdf Page Up": 0x49, "Pdf Scroll Down": 0x4A,
            "Pdf Scroll Up": 0x4B, "Glide Down": 0x4C, "Lead Mute": 0x4D,
            "Expr. Left/Style": 0x4E, "Arabic Reset": 0x4F, "Hold": 0x50,
            "2nd On/Off": 0x51, "Pause": 0x52, "Talk On/Off": 0x53,
            "Manual Drum": 0x54, "Kick Off": 0x55, "Snare Off": 0x56,
            "Rimshot Off": 0x57, "Hit-Hat Off": 0x58, "Cymbal Off": 0x59,
            "Tom Off": 0x5A, "Latin1 Off": 0x5B, "Latin2 Off": 0x5C,
            "Latin3/Tamb Off": 0x5D, "Clap/fx Off": 0x5E, "Voice Down": 0x5F,
            "Voice Up": 0x60, "Regis Down": 0x61, "Regis Up": 0x62,
            "Style Voice Down": 0x63, "Style Voice Up": 0x64, "EFX1 Preset Down": 0x65,
            "EFX1 Preset Up": 0x66, "Multi": 0x67, "Page<<": 0x68, "Page>>": 0x69,
            "RegisVoice<<": 0x6A, "RegisVoice>>": 0x6B, "Text Page": 0x6E,
            "Text Page+": 0x6F, "Style Voice 1": 0x70, "Style Voice 2": 0x71,
            "Style Voice 3": 0x72, "Style Voice 4": 0x73, "VIEW & MODELING": 0x74,
            "Lock Bass": 0x75, "LockChord": 0x76, "Lyrics": 0x77,
            "VoiceToABCD": 0x87, "TAP": 0x88, "Autocrash": 0x89,
            "Transp Down": 0x8A, "Transp Up": 0x8B, "Text Record": 0x8C,
            "Bass & Drum": 0x8D, "Pdf Clear": 0x8E, "Record": 0x90, "Play": 0x91,
            "DoubleDown": 0x92, "DoubleUp": 0x93, "Arr.Off": 0x94,
            "FILL & DRUM IN": 0x95, "Wah to Pedal": 0x96, "Overdrive to Pedal": 0x98,
            "Drum Mute": 0x99, "Bass Mute": 0x9A, "Chords Mute": 0x9B,
            "Real Chords Mute": 0x9C, "Voice2 to Pedal": 0x9D, "Micro Edit": 0x9E,
            "Micro2 Edit": 0x9F, "HALF BAR": 0xA0, "Bs Sust Pedal": 0xA1,
            "Scale": 0xA2, "End Swap": 0xA3, "Set Down": 0xA4, "Set Up": 0xA5,
            "FswChDelay": 0xA6, "IntroOnArr.": 0xA7, "EndingOnArr.": 0xA8,
            "Arr. Down": 0xA9, "Arr. Up": 0xAA, "Ending1": 0xAB, "Ending2": 0xAC,
            "Ending3": 0xAD, "Bass Lock": 0xAE, "Intro Loop": 0xB0,
            "Scene Down": 0xB1, "Scene Up": 0xB2, "STEM Scene A": 0xB3,
            "STEM Scene B": 0xB4, "STEM Scene C": 0xB5, "STEM Scene D": 0xB6,
            "STEM Solo": 0xB7, "STEM Autoplay": 0xB8, "STEM A On/Off": 0xB9,
            "STEM B On/Off": 0xBA, "STEM C On/Off": 0xBB, "STEM D On/Off": 0xBC,
            "STEM Lead On/Off": 0xBD, "Art. Toggle": 0xBE, "Key Tune On/Off": 0xBF,
            "Txt Clear": 0xC0, "Voicetr. Edit": 0xC1, "Clear Image": 0xC2
        }

    def _init_tab_midis(self):
        """Initialize tab MIDI dictionary"""
        
        return {
            "DIAL_DOWN": 0x0, "DIAL_UP": 0x1, "PLAYER_A": 0x2, "PLAYER_B": 0x3,
            "ENTER": 0x4, "MENU": 0x6, "LYRIC": 0x7, "LEAD": 0x8, "VARIATION": 0x9,
            "DRAWBARS_VIEW": 0x0a, "DRAWBARS": 0x10, "DRUMSET": 0x11, "TALK": 0x12,
            "VOICETRON": 0x13, "STYLE_BOX": 0x14, "VOICE1": 0x19, "VOICE2": 0x1a,
            "USER_VOICE": 0x1b, "XFADE": 0x1c, "INTRO1": 0x1d, "INTRO2": 0x1e,
            "INTRO3": 0x1f, "BASSIST": 0x20, "DRUM_MIXER": 0x22, "OCTAVE_UP": 0x24,
            "OCTAVE_DOWN": 0x25, "USER_STYLE": 0x26, "DSP": 0x27, "ADSR_FILTER": 0x28,
            "MICRO": 0x29, "ARRA": 0x2c, "ARRB": 0x2d, "ARRC": 0x2e, "ARRD": 0x2f,
            "FILL": 0x30, "BREAK": 0x31, "JUKE_BOX": 0x32, "STEM": 0x33,
            "PIANIST": 0x34, "BASS_TO_LOWEST": 0x40, "MANUAL_BASS": 0x41,
            "PORTAMENTO": 0x48, "HARMONY": 0x49, "PAUSE": 0x4a, "TEMPO_SLOW": 0x4b,
            "TEMPO_FAST": 0x4c, "START_STOP": 0x4d, "TRANSP_DOWN": 0x59,
            "TRANSP_UP": 0x5a, "AFTERTOUCH": 0x5e, "EXIT": 0x5f, "ROTOR_SLOW": 0x60,
            "ROTOR_FAST": 0x61, "PIANO_FAM": 0x62, "ETHNIC_FAM": 0x63,
            "ORGAN_FAM": 0x64, "GUITAR_FAM": 0x65, "BASS_FAM": 0x66,
            "STRING_FAM": 0x67, "BRASS_FAM": 0x68, "SAX_FAM": 0x69, "HOLD": 0x6f,
            "PAD_FAM": 0x70, "SYNTH_FAM": 0x71, "FADEOUT": 0x73, "BASS_TO_ROOT": 0x74,
            "GM": 0x77
        }

    def _init_cc_midis(self):
        """Initialize MIDI CC dictionary"""
        
        return {
            "PLAYER": SliderCC.PLAYER_CC, "STYLE": SliderCC.STYLE_CC, "DRUM": SliderCC.DRUM_CC, 
            "CHORD": SliderCC.CHORD_CC, "REALCHORD": SliderCC.REALCHORD_CC, 
            "BASS": SliderCC.BASS_CC, "LOWERS": SliderCC.LOWERS_CC, "USER2": SliderCC.USER2_CC, "USER3": SliderCC.USER3_CC, 
            "VOICE1": SliderCC.VOICE1_CC, "VOICE2": SliderCC.VOICE2_CC, "DRAWBARS": SliderCC.DRAWBARS_CC,
            "MICRO1": SliderCC.MICRO1_CC, "VOCAL": SliderCC.VOCAL_CC
        }
    
    def format_pedal_sysex(self, pedal_name: str, on_state: bool = True) -> list:
        """
        Format a pedal command as a SysEx message.
        
        Args:
            pedal_name: Name of the pedal command (e.g., "Start/Stop")
            on_state: True for ON message, False for OFF message
        
        Returns:
            List of bytes for the SysEx message (excluding 0xF0 and 0xF7)
        
        Raises:
            KeyError: If pedal_name is not found in pedal_midis
        """
        if pedal_name not in self.pedal_midis:
            raise KeyError(f"Pedal '{pedal_name}' not found in pedal_midis")
        
        pedal_value = self.pedal_midis[pedal_name]
        state_value = KETRON_SYSEX_ON_VALUE if on_state else KETRON_SYSEX_OFF_VALUE
        
        # Ketron SysEx format for pedal commands:
        # For values < 128: F0 43 [device_id] [command_byte] [state_value] F7
        # For values >= 128: F0 43 [device_id] [high_byte] [low_byte] [state_value] F7
        # state_value: 0x7F (127) for ON, 0x00 (0) for OFF
        # Values >= 128 are split into two 7-bit bytes (high byte and low byte)
        
        sysex_data = [
            KETRON_SYSEX_MANUFACTURER_ID,
            KETRON_SYSEX_DEVICE_ID
        ]
        
        if pedal_value < 128:
            # Standard 3-byte format: manufacturer, device_id, command, state
            sysex_data.append(pedal_value)
            sysex_data.append(state_value)
        else:
            # Extended 4-byte format: manufacturer, device_id, high_byte, low_byte, state
            # Split value into two 7-bit bytes
            high_byte = (pedal_value >> 7) & 0x7F
            low_byte = pedal_value & 0x7F
            sysex_data.append(high_byte)
            sysex_data.append(low_byte)
            sysex_data.append(state_value)
        
        return sysex_data
    
    def format_tab_sysex(self, tab_name: str, on_state: bool = True) -> list:
        """
        Format a tab command as a SysEx message.
        
        Args:
            tab_name: Name of the tab command (e.g., "START_STOP")
            on_state: True for ON message, False for OFF message
        
        Returns:
            List of bytes for the SysEx message (excluding 0xF0 and 0xF7)
        
        Raises:
            KeyError: If tab_name is not found in tab_midis
        """
        if tab_name not in self.tab_midis:
            raise KeyError(f"Tab '{tab_name}' not found in tab_midis")
        
        tab_value = self.tab_midis[tab_name]
        state_value = KETRON_SYSEX_ON_VALUE if on_state else KETRON_SYSEX_OFF_VALUE
        
        # Ketron SysEx format for tab commands:
        # F0 43 [device_id] [command_byte] [state_value] F7
        # state_value: 0x7F (127) for ON, 0x00 (0) for OFF
        sysex_data = [
            KETRON_SYSEX_MANUFACTURER_ID,
            KETRON_SYSEX_DEVICE_ID,
            tab_value,
            state_value
        ]
        
        return sysex_data
    
    def send_pedal_command(self, pedal_name: str, port_name: str = None, delay: float = 0.01) -> bool:
        """
        Send a pedal command as SysEx ON and OFF messages via MidiManager.
        Simulates a key press and release by sending ON followed by OFF.
        
        Args:
            pedal_name: Name of the pedal command (e.g., "Start/Stop")
            port_name: MIDI port name (optional, uses default if None)
            delay: Delay in seconds between ON and OFF messages (default: 0.01s)
        
        Returns:
            True if both messages were sent successfully, False otherwise
        """
        try:
            import time
            from devdeck.midi_manager import MidiManager
            
            midi = MidiManager()
            
            # Ensure port is open
            if not midi.is_port_open(port_name):
                if not midi.open_port(port_name):
                    return False
            
            # Send ON message
            sysex_on = self.format_pedal_sysex(pedal_name, on_state=True)
            if not midi.send_sysex(sysex_on, port_name):
                return False
            
            # Small delay to simulate key press duration
            time.sleep(delay)
            
            # Send OFF message
            sysex_off = self.format_pedal_sysex(pedal_name, on_state=False)
            if not midi.send_sysex(sysex_off, port_name):
                return False
            
            return True
        except Exception as e:
            import logging
            logger = logging.getLogger('devdeck')
            logger.error(f"Error sending pedal command '{pedal_name}': {e}")
            return False
    
    def send_tab_command(self, tab_name: str, port_name: str = None, delay: float = 0.01) -> bool:
        """
        Send a tab command as SysEx ON and OFF messages via MidiManager.
        Simulates a key press and release by sending ON followed by OFF.
        
        Args:
            tab_name: Name of the tab command (e.g., "START_STOP")
            port_name: MIDI port name (optional, uses default if None)
            delay: Delay in seconds between ON and OFF messages (default: 0.01s)
        
        Returns:
            True if both messages were sent successfully, False otherwise
        """
        try:
            import time
            from devdeck.midi_manager import MidiManager
            
            midi = MidiManager()
            
            # Ensure port is open
            if not midi.is_port_open(port_name):
                if not midi.open_port(port_name):
                    return False
            
            # Send ON message
            sysex_on = self.format_tab_sysex(tab_name, on_state=True)
            if not midi.send_sysex(sysex_on, port_name):
                return False
            
            # Small delay to simulate key press duration
            time.sleep(delay)
            
            # Send OFF message
            sysex_off = self.format_tab_sysex(tab_name, on_state=False)
            if not midi.send_sysex(sysex_off, port_name):
                return False
            
            return True
        except Exception as e:
            import logging
            logger = logging.getLogger('devdeck')
            logger.error(f"Error sending tab command '{tab_name}': {e}")
            return False
    
    def test_start_stop(self, port_name: str = None) -> bool:
        """
        Test function to send "Start/Stop" pedal command.
        Sends both ON and OFF messages to simulate a key press and release.
        
        Args:
            port_name: MIDI port name (optional, uses default if None)
        
        Returns:
            True if both messages were sent successfully, False otherwise
        """
        print("Testing Ketron 'Start/Stop' pedal command...")
        print(f"Port: {port_name if port_name else 'default'}")
        
        # Format both ON and OFF messages for display
        sysex_on = self.format_pedal_sysex("Start/Stop", on_state=True)
        sysex_off = self.format_pedal_sysex("Start/Stop", on_state=False)
        
        print(f"  ON message:  F0 {' '.join([hex(b) for b in sysex_on])} F7")
        print(f"  OFF message: F0 {' '.join([hex(b) for b in sysex_off])} F7")
        
        success = self.send_pedal_command("Start/Stop", port_name)
        
        if success:
            print("[OK] 'Start/Stop' SysEx ON and OFF messages sent successfully!")
        else:
            print("[ERROR] Failed to send 'Start/Stop' SysEx messages")
        
        return success


class KeyMapping:
    """Represents a mapping for a single deck key with reference to its source list"""
    def __init__(self, key_name, midi_value, source_list_name, source_list):
        """
        Args:
            key_name: The key name from the source dictionary (e.g., "Sustain", "VOICE1")
            midi_value: The MIDI value associated with this key
            source_list_name: Name of the source list ("pedal_midis", "tab_midis", or "cc_midis")
            source_list: Reference to the actual source list dictionary
        """
        self.key_name = key_name
        self.midi_value = midi_value
        self.source_list_name = source_list_name
        self.source_list = source_list
    
    def get_midi_type(self):
        """Returns the MIDI message type based on source list"""
        if self.source_list_name == "cc_midis":
            return "CC"
        else:  # pedal_midis or tab_midis
            return "SysEx"
    
    def __repr__(self):
        return f"KeyMapping(key_name='{self.key_name}', midi_value=0x{self.midi_value:02X}, source='{self.source_list_name}', type='{self.get_midi_type()}')"


class DeckKeyMappings:
    """Manages mappings for all 15 keys (0-14) in the deck controllers"""
    
    def __init__(self, ketron_midi):
        """
        Args:
            ketron_midi: Instance of KetronMidi containing pedal_midis, tab_midis, and cc_midis
        """
        self.ketron_midi = ketron_midi
        self.mappings = {}  # key_no -> KeyMapping
        
    def set_mapping(self, key_no, key_name, source_list_name):
        """
        Set a mapping for a deck key
        
        Args:
            key_no: Deck key number (0-14)
            key_name: Key name from the source dictionary
            source_list_name: "pedal_midis", "tab_midis", or "cc_midis"
        
        Raises:
            ValueError: If key_no is not 0-14 or source_list_name is invalid
            KeyError: If key_name is not found in the specified source list
        """
        if key_no < 0 or key_no > 14:
            raise ValueError(f"key_no must be between 0 and 14, got {key_no}")
        
        # Get the source list
        if source_list_name == "pedal_midis":
            source_list = self.ketron_midi.pedal_midis
        elif source_list_name == "tab_midis":
            source_list = self.ketron_midi.tab_midis
        elif source_list_name == "cc_midis":
            source_list = self.ketron_midi.cc_midis
        else:
            raise ValueError(f"Invalid source_list_name: {source_list_name}. Must be 'pedal_midis', 'tab_midis', or 'cc_midis'")
        
        # Get the MIDI value
        if key_name not in source_list:
            raise KeyError(f"Key '{key_name}' not found in {source_list_name}")
        
        midi_value = source_list[key_name]
        
        # Create and store the mapping
        self.mappings[key_no] = KeyMapping(key_name, midi_value, source_list_name, source_list)
    
    def get_mapping(self, key_no):
        """
        Get the mapping for a deck key
        
        Args:
            key_no: Deck key number (0-14)
        
        Returns:
            KeyMapping object or None if not set
        """
        return self.mappings.get(key_no)
    
    def get_midi_message(self, key_no):
        """
        Get MIDI message information for a key
        
        Args:
            key_no: Deck key number (0-14)
        
        Returns:
            dict with keys: 'type' (CC or SysEx), 'key_name', 'midi_value', 'source_list_name'
            or None if mapping not set
        """
        mapping = self.get_mapping(key_no)
        if mapping is None:
            return None
        
        return {
            'type': mapping.get_midi_type(),
            'key_name': mapping.key_name,
            'midi_value': mapping.midi_value,
            'source_list_name': mapping.source_list_name
        }
    
    def get_all_mappings(self):
        """Get all mappings as a dictionary"""
        return self.mappings.copy()
    
    def clear_mapping(self, key_no):
        """Clear the mapping for a key"""
        if key_no in self.mappings:
            del self.mappings[key_no]
    
    def clear_all(self):
        """Clear all mappings"""
        self.mappings.clear()


