import json
import os
import yaml
from cerberus import Validator
from pathlib import Path

from devdeck.settings.deck_settings import DeckSettings
from devdeck.settings.validation_error import ValidationError


def wrap_text_to_lines(text, max_chars_per_line=6):
    """
    Wrap text into multiple lines with a maximum number of characters per line.
    
    Args:
        text (str): The text to wrap
        max_chars_per_line (int): Maximum characters per line (default: 6)
    
    Returns:
        str: Text with newlines inserted, with each line having at most max_chars_per_line characters
    """
    if not text:
        return text
    
    # Split by spaces to try to break at word boundaries when possible
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        word_length = len(word)
        
        # If a single word is longer than max_chars_per_line, break it
        if word_length > max_chars_per_line:
            # Add current line if it has content
            if current_line:
                lines.append(' '.join(current_line))
                current_line = []
                current_length = 0
            
            # Break the long word into chunks
            for i in range(0, word_length, max_chars_per_line):
                lines.append(word[i:i + max_chars_per_line])
        else:
            # Check if adding this word would exceed the limit
            potential_length = current_length + word_length + (1 if current_line else 0)
            
            if potential_length > max_chars_per_line and current_line:
                # Start a new line
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_length
            else:
                # Add to current line
                current_line.append(word)
                current_length = potential_length
    
    # Add the last line if it has content
    if current_line:
        lines.append(' '.join(current_line))
    
    # Join with \n escape sequence for better YAML readability
    # YAML will parse \n as a newline character
    return '\\n'.join(lines)

schema = {
    'decks': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'serial_number': {
                    'type': 'string',
                    'required': True
                },
                'name': {
                    'type': 'string',
                    'required': True
                },
                'settings': {
                    'type': 'dict',
                    'required': True
                    # Note: allow_unknown is configured in Validator, not schema
                }
            }
        }
    }
}


class DevDeckSettings:
    def __init__(self, settings):
        self.settings = settings

    def deck(self, serial_number):
        settings_for_deck = [deck_setting for deck_setting in self.decks() if
                             deck_setting.serial_number() == serial_number[0:12]]
        if settings_for_deck:
            return settings_for_deck[0]
        return None

    def decks(self):
        return [DeckSettings(deck_setting) for deck_setting in self.settings['decks']]

    @staticmethod
    def load(filename):
        with open(filename, 'r') as stream:
            settings = yaml.safe_load(stream)

            # Configure validator to allow unknown fields in nested structures
            validator = Validator(schema, allow_unknown=True)
            if validator.validate(settings, schema):
                return DevDeckSettings(settings)
            raise ValidationError(validator.errors)

    @staticmethod
    def generate_default(filename, serial_numbers):
        default_configs = []
        for serial_number in serial_numbers:
            deck_config = {
                'serial_number': serial_number[0:12],
                'name': 'devdeck.decks.single_page_deck_controller.SinglePageDeckController',
                'settings': {
                    'controls': [
                        {
                            'name': 'devdeck.controls.clock_control.ClockControl',
                            'key': 0
                        }
                    ]
                }
            }
            default_configs.append(deck_config)
        with open(filename, 'w') as f:
            yaml.dump({'decks': default_configs}, f)

    @staticmethod
    def _update_controls_from_mappings(controls, mappings_dict, key_offset=0):
        """
        Recursively update controls from key mappings
        
        Args:
            controls: List of control dictionaries
            mappings_dict: Dictionary mapping key_no to mapping data
            key_offset: Offset to add to key_no when looking up mappings (for nested decks)
        
        Returns:
            True if any updates were made
        """
        updated = False
        for control in controls:
            key_no = control.get('key')
            if key_no is not None:
                # Calculate the actual key number for lookup (accounting for offset)
                lookup_key = key_no + key_offset
                
                if lookup_key in mappings_dict:
                    mapping = mappings_dict[lookup_key]
                    # Skip if key_name is empty or only whitespace (these should remain as NavigationToggleControl or other controls)
                    key_name = mapping.get('key_name', '').strip()
                    if not key_name:
                        # Don't convert controls with empty key_name - they should remain as-is
                        import logging
                        logger = logging.getLogger('devdeck')
                        logger.debug(f"Skipping conversion for key {key_no} (lookup_key: {lookup_key}) - empty key_name")
                        continue
                    
                    # Never convert NavigationToggleControl - it's a special control type
                    if 'NavigationToggleControl' in control.get('name', ''):
                        import logging
                        logger = logging.getLogger('devdeck')
                        logger.debug(f"Skipping conversion for key {key_no} (lookup_key: {lookup_key}) - NavigationToggleControl")
                        continue
                    
                    # Ensure settings dict exists
                    if 'settings' not in control:
                        control['settings'] = {}
                    
                    # Change TextControl to KetronKeyMappingControl to enable MIDI sending
                    # KetronKeyMappingControl reads text/colors from key_mappings.json directly
                    if control.get('name', '').endswith('TextControl'):
                        import logging
                        logger = logging.getLogger('devdeck')
                        logger.info(f"Converting TextControl to KetronKeyMappingControl for key {key_no} (lookup_key: {lookup_key}, key_name: '{key_name}')")
                        # Change control type to KetronKeyMappingControl
                        control['name'] = 'devdeck.controls.ketron_key_mapping_control.KetronKeyMappingControl'
                        # Remove TextControl-specific settings since KetronKeyMappingControl
                        # reads text/colors from key_mappings.json directly
                        text_control_settings = ['text', 'color', 'background_color', 'font_size']
                        for setting in text_control_settings:
                            if setting in control['settings']:
                                del control['settings'][setting]
                        updated = True
                    # For other control types, update text/colors if they support it
                    elif 'text' in control.get('settings', {}):
                        # Wrap text to maximum 6 characters per line
                        wrapped_text = wrap_text_to_lines(mapping['key_name'], max_chars_per_line=6)
                        control['settings']['text'] = wrapped_text
                        # Update colors from key_mappings.json if provided
                        if 'text_color' in mapping:
                            control['settings']['color'] = mapping['text_color']
                        if 'background_color' in mapping:
                            control['settings']['background_color'] = mapping['background_color']
                        updated = True
                
                # Recursively check nested deck controllers (e.g., in NavigationToggleControl)
                control_settings = control.get('settings', {})
                target_deck_settings = control_settings.get('target_deck_settings', {})
                nested_controls = target_deck_settings.get('controls', [])
                if nested_controls:
                    # For second page controller, keys 0-14 map to mappings 15-29
                    nested_offset = 15 if key_offset == 0 else 0
                    import logging
                    logger = logging.getLogger('devdeck')
                    logger.debug(f"Processing {len(nested_controls)} nested controls with offset {nested_offset}")
                    if DevDeckSettings._update_controls_from_mappings(nested_controls, mappings_dict, nested_offset):
                        updated = True
                        logger.info(f"Updated {len(nested_controls)} nested controls with offset {nested_offset}")
        
        return updated

    @staticmethod
    def update_from_key_mappings(settings_filename, key_mappings_filename=None):
        """
        Update settings.yml with key mappings from key_mappings.json
        
        Args:
            settings_filename: Path to settings.yml file
            key_mappings_filename: Path to key_mappings.json file (defaults to key_mappings.json in project root)
        """
        if key_mappings_filename is None:
            # Try to find key_mappings.json in config directory (preferred location)
            project_root = Path(__file__).parent.parent.parent
            key_mappings_filename = project_root / 'config' / 'key_mappings.json'
            
            # If not found in config, try project root (backward compatibility)
            if not key_mappings_filename.exists() or key_mappings_filename.stat().st_size == 0:
                key_mappings_filename = project_root / 'key_mappings.json'
            
            # If still not found, try in the same directory as settings.yml
            if not key_mappings_filename.exists() or key_mappings_filename.stat().st_size == 0:
                settings_dir = Path(settings_filename).parent
                key_mappings_filename = settings_dir / 'key_mappings.json'
        
        # Check if key_mappings.json exists and is not empty
        if not os.path.exists(key_mappings_filename) or os.path.getsize(key_mappings_filename) == 0:
            return False
        
        try:
            # Load key mappings - try UTF-16 first (Windows default), then UTF-8
            try:
                with open(key_mappings_filename, 'r', encoding='utf-16') as f:
                    content = f.read().strip()
            except (UnicodeDecodeError, UnicodeError):
                with open(key_mappings_filename, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
            
            if not content:
                return False
            
            key_mappings_data = json.loads(content)
            
            # Handle both named structure {"key_mappings": [...]} and direct array [...]
            if isinstance(key_mappings_data, dict) and 'key_mappings' in key_mappings_data:
                key_mappings = key_mappings_data['key_mappings']
            elif isinstance(key_mappings_data, list):
                key_mappings = key_mappings_data
            else:
                import logging
                logger = logging.getLogger('devdeck')
                logger.warning(f"Invalid key mappings structure in {key_mappings_filename}")
                return False
            
            # Create a dictionary for quick lookup: key_no -> mapping
            mappings_dict = {mapping['key_no']: mapping for mapping in key_mappings}
            
            # Load settings
            with open(settings_filename, 'r') as f:
                settings = yaml.safe_load(f)
            
            # Save a readable template backup before conversion
            import shutil
            template_filename = str(Path(settings_filename).with_suffix('.yml.template'))
            try:
                shutil.copy2(settings_filename, template_filename)
                import logging
                logger = logging.getLogger('devdeck')
                logger.debug(f"Saved readable template to {template_filename}")
            except Exception as e:
                import logging
                logger = logging.getLogger('devdeck')
                logger.warning(f"Could not save template file: {e}")
            
            # Update each deck's controls
            updated = False
            import logging
            logger = logging.getLogger('devdeck')
            logger.info(f"Starting conversion of controls from key_mappings.json (found {len(mappings_dict)} mappings)")
            for deck in settings.get('decks', []):
                controls = deck.get('settings', {}).get('controls', [])
                logger.debug(f"Processing deck with {len(controls)} controls")
                if DevDeckSettings._update_controls_from_mappings(controls, mappings_dict, key_offset=0):
                    updated = True
                    logger.info("Deck controls updated")
            
            # Save updated settings if any changes were made
            # Note: This converts TextControl to KetronKeyMappingControl, which removes
            # the text/color settings since KetronKeyMappingControl reads from key_mappings.json
            if updated:
                with open(settings_filename, 'w') as f:
                    yaml.dump(settings, f, default_flow_style=False, sort_keys=False)
                import logging
                logger = logging.getLogger('devdeck')
                logger.info("Updated settings.yml from key_mappings.json - controls converted to KetronKeyMappingControl")
                return True
            
            return False
            
        except json.JSONDecodeError as e:
            # Log JSON parsing error with file path
            import logging
            logger = logging.getLogger('devdeck')
            logger.warning(f"Failed to parse key mappings JSON from {key_mappings_filename}: {e}")
            return False
        except Exception as e:
            # Log error but don't fail startup
            import logging
            logger = logging.getLogger('devdeck')
            logger.warning(f"Failed to update settings from key mappings ({key_mappings_filename}): {e}")
            return False
