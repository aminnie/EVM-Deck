from devdeck_core.controls.deck_control import DeckControl


class TextControl(DeckControl):

    def __init__(self, key_no, **kwargs):
        super().__init__(key_no, **kwargs)

    def _render(self):
        """Helper method to render the text control"""
        with self.deck_context() as context:
            with context.renderer() as r:
                text = self.settings.get('text', '')
                font_size = self.settings.get('font_size', 120)
                color = self.settings.get('color', 'white')
                background_color = self.settings.get('background_color', 'lightblue')
                
                r.background_color(background_color)
                r.text(text)\
                    .font_size(font_size)\
                    .color(color)\
                    .center_vertically()\
                    .center_horizontally()\
                    .end()

    def initialize(self):
        """Initial render when control is set up"""
        self._render()

    def pressed(self):
        """Re-render on key press to prevent default images from appearing"""
        self._render()

    def released(self):
        """Re-render on key release to ensure image stays visible"""
        self._render()

