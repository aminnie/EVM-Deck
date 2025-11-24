"""
Base control class with common functionality for deck controls.

This module provides a base class that other controls can inherit from to
avoid code duplication, particularly for error rendering.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from devdeck_core.controls.deck_control import DeckControl
    Base = DeckControl
else:
    from devdeck_core.controls.deck_control import DeckControl
    Base = DeckControl


class BaseDeckControl(Base):
    """
    Base class for deck controls with common functionality.
    
    Provides shared methods like error rendering that are used across
    multiple control implementations.
    """
    
    def _render_error(self, error_text: str, font_size: int = 70) -> None:
        """
        Render an error message on the deck key.
        
        Args:
            error_text: The error message to display
            font_size: Font size for the error text (default: 70)
        """
        with self.deck_context() as context:
            with context.renderer() as r:
                r.text(error_text)\
                    .font_size(font_size)\
                    .color('red')\
                    .center_vertically()\
                    .center_horizontally()\
                    .end()

