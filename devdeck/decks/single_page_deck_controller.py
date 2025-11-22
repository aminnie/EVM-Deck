import logging
import os

from devdeck_core.decks.deck_controller import DeckController
from devdeck.settings.control_settings import ControlSettings
from devdeck.controls.navigation_toggle_control import NavigationToggleControl
from devdeck.controls.text_control import TextControl


class SinglePageDeckController(DeckController):

    def __init__(self, key_no, **kwargs):
        self.__logger = logging.getLogger('devdeck')
        self.settings = kwargs
        super().__init__(key_no, **kwargs)

    def initialize(self):
        with self.deck_context() as context:
            with context.renderer() as r:
                r.image(os.path.expanduser(self.settings['icon'])).end()

    def deck_controls(self):
        controls = [ControlSettings(control_settings) for control_settings in self.settings['controls']]
        for control in controls:
            control_class = control.control_class()
            control_settings = control.control_settings()
            self.register_control(control.key(), control_class, **control_settings)

    def pressed(self, key_no):
        """Override to match base class behavior"""
        if key_no not in self.controls:
            return
        if issubclass(type(self.controls[key_no]), DeckController):
            return
        self.__logger.info("Key %s pressed on %s", key_no, type(self).__name__)
        try:
            self.controls[key_no].pressed()
        except Exception as ex:
            self.__logger.error("Key %s (%s) pressed() raised an unhandled exception: %s",
                                key_no, type(self).__name__, str(ex))

    def released(self, key_no):
        """Override to prevent pop_active_deck() after NavigationToggleControl handles navigation"""
        if key_no not in self.controls:
            return
        if issubclass(type(self.controls[key_no]), DeckController):
            if hasattr(self, '_DeckController__deck_context'):
                self.__deck_context.set_active_deck(self.controls[key_no])
            return
        self.__logger.info("Key %s released on %s", key_no, type(self).__name__)
        try:
            self.controls[key_no].released()
        except Exception as ex:
            self.__logger.error("Key %s (%s) released() raised an unhandled exception: %s",
                                key_no, type(self).__name__, str(ex), exc_info=True)
        # Don't pop for regular controls - they shouldn't trigger navigation
        # NavigationToggleControl handles its own navigation
        # Only DeckController subclasses should trigger navigation

    def get_control(self, key_no, control_type=None):
        """
        Get a control by key number, optionally checking its type.
        
        Args:
            key_no (int): The key number (0-14)
            control_type (type, optional): If provided, only return the control if it's an instance of this type
        
        Returns:
            The control instance, or None if not found or type doesn't match
        """
        if key_no not in self.controls:
            return None
        
        control = self.controls[key_no]
        if control_type is not None and not isinstance(control, control_type):
            return None
        
        return control

    def update_text(self, key_no, new_text):
        """
        Update the text displayed on a TextControl at runtime.
        
        Args:
            key_no (int): The key number (0-14) to update
            new_text (str): The new text to display
        
        Returns:
            bool: True if the text was updated, False if the key doesn't exist or isn't a TextControl
        """
        text_control = self.get_control(key_no, TextControl)
        if text_control is None:
            self.__logger.warning("Key %s is not a TextControl or doesn't exist", key_no)
            return False
        
        text_control.update_text(new_text)
        return True

    def settings_schema(self):
        return {
            'controls': {
                'type': 'list',
                'required': True,
                'schema': {
                    'type': 'dict',
                    'schema': {
                        'name': {
                            'type': 'string',
                            'required': True
                        },
                        'key': {
                            'type': 'integer',
                            'required': True
                        },
                        'settings': {
                            'type': 'dict'
                            # Note: allow_unknown is handled by Validator configuration, not schema
                        }
                    }
                }
            },
            'icon': {
                'type': 'string',
            },
        }
