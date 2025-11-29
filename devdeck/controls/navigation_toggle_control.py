import logging
import os
import importlib

from devdeck_core.controls.deck_control import DeckControl


class NavigationToggleControl(DeckControl):

    def __init__(self, key_no, **kwargs):
        self.__logger = logging.getLogger('devdeck')
        super().__init__(key_no, **kwargs)
        self._second_layer_deck = None

    def _render_text(self):
        """Render the navigation text based on current deck"""
        with self.deck_context() as context:
            with context.renderer() as r:
                icon_path = self.settings.get('icon')
                if icon_path and icon_path.strip():
                    # Use custom icon if provided
                    r.image(os.path.expanduser(icon_path)).end()
                else:
                    # Determine which page text to show based on current deck
                    deck_count = context.deck_context.get_deck_count()
                    active_deck = context.deck_context.get_active_deck()
                    
                    # Check if we're on the main deck (stack depth = 1) or second deck (stack depth = 2)
                    if deck_count == 1:
                        # On main deck, show "Style Page" to indicate going to page 2
                        page_text = "Style\nPage"
                    else:
                        # On second deck or deeper, show "Arranger Page" to indicate going back to page 1
                        page_text = "Arranger\nPage"
                    
                    # Get background color from settings, default to black
                    background_color = self.settings.get('background_color', 'black')
                    # Get text color from settings, default to white
                    text_color = self.settings.get('text_color', self.settings.get('color', 'white'))
                    
                    r.background_color(background_color)
                    r.text(page_text)\
                        .font_size(100)\
                        .color(text_color)\
                        .center_vertically()\
                        .center_horizontally()\
                        .end()

    def initialize(self):
        """Display the navigation icon"""
        self._render_text()

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
        """Re-render on press to ensure text is up to date"""
        self._render_text()

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
                    # Re-render to update text to "Page Arranger"
                    self._render_text()
                else:
                    self.__logger.warning("Second layer deck not configured for navigation control")
            else:
                # On second deck or deeper, navigate back
                context.deck_context.pop_active_deck()
                # Re-render to update text to "Style Page"
                self._render_text()

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
            },
            'background_color': {
                'type': 'string'
            },
            'text_color': {
                'type': 'string'
            },
            'color': {
                'type': 'string'
            }
        }

