import logging

from devdeck_core.decks.deck_controller import DeckController
from devdeck.settings.control_settings import ControlSettings
from devdeck.controls.navigation_toggle_control import NavigationToggleControl


class SecondPageDeckController(DeckController):

    def __init__(self, key_no, **kwargs):
        self.__logger = logging.getLogger('devdeck')
        self.settings = kwargs
        super().__init__(key_no, **kwargs)

    def deck_controls(self):
        controls = [ControlSettings(control_settings) for control_settings in self.settings['controls']]
        for control in controls:
            control_class = control.control_class()
            control_settings = control.control_settings()
            self.register_control(control.key(), control_class, **control_settings)

    def released(self, key_no):
        """Override to prevent pop_active_deck() after NavigationToggleControl handles navigation"""
        if key_no not in self.controls:
            return
        if issubclass(type(self.controls[key_no]), DeckController):
            self.__deck_context.set_active_deck(self.controls[key_no])
            return
        self.__logger.info("Key %s released on %s", key_no, type(self).__name__)
        try:
            self.controls[key_no].released()
        except Exception as ex:
            self.__logger.error("Key %s (%s) released() raised an unhandled exception: %s",
                                key_no, type(self).__name__, str(ex))
        # Don't pop if the control is a NavigationToggleControl (it handles its own navigation)
        if not isinstance(self.controls[key_no], NavigationToggleControl):
            self.__deck_context.pop_active_deck()

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
                        }
                    }
                }
            }
        }

