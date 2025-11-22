import logging
import os
import importlib

from devdeck_core.controls.deck_control import DeckControl


class NavigationToggleControl(DeckControl):

    def __init__(self, key_no, **kwargs):
        self.__logger = logging.getLogger('devdeck')
        super().__init__(key_no, **kwargs)
        self._second_layer_deck = None

    def initialize(self):
        """Display the navigation icon"""
        with self.deck_context() as context:
            with context.renderer() as r:
                icon_path = self.settings.get('icon')
                if icon_path:
                    r.image(os.path.expanduser(icon_path)).end()
                else:
                    # Default: render text if no icon
                    r.text("Page 2")\
                        .font_size(100)\
                        .color('white')\
                        .center_vertically()\
                        .center_horizontally()\
                        .end()

    def _get_second_layer_deck(self):
        """Lazy instantiation of the second layer deck"""
        if self._second_layer_deck is None:
            deck_class_name = self.settings.get('target_deck_class')
            deck_settings = self.settings.get('target_deck_settings', {})
            
            if deck_class_name:
                # Instantiate the second layer deck
                module_name, class_name = deck_class_name.rsplit(".", 1)
                deck_class = getattr(importlib.import_module(module_name), class_name)
                self._second_layer_deck = deck_class(None, **deck_settings)
        
        return self._second_layer_deck

    def pressed(self):
        """No action on press"""
        pass

    def released(self):
        """Toggle between main layer and second layer"""
        with self.deck_context() as context:
            deck_count = context.deck_context.get_deck_count()
            active_deck = context.deck_context.get_active_deck()
            
            # Check if we're on the main deck (stack depth = 1) or second deck (stack depth = 2)
            if deck_count == 1:
                # On main deck, navigate to second layer
                second_layer_deck = self._get_second_layer_deck()
                if second_layer_deck:
                    context.deck_context.set_active_deck(second_layer_deck)
                else:
                    self.__logger.warning("Second layer deck not configured for navigation control")
            else:
                # On second deck or deeper, navigate back
                context.deck_context.pop_active_deck()

    def settings_schema(self):
        return {
            'icon': {
                'type': 'string'
            },
            'target_deck_class': {
                'type': 'string'
            },
            'target_deck_settings': {
                'type': 'dict'
            }
        }

