"""
Base control class with common functionality for deck controls.

This module provides a base class that other controls can inherit from to
avoid code duplication, particularly for error rendering.
"""

import threading
import time
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
    
    def _flash_key(self, flash_color: str, flash_duration_ms: int = 100) -> None:
        """
        Flash the key with a specified background color for a duration.
        After the flash, the original render state is restored by calling _render().
        
        This method should be overridden by subclasses to provide custom flash behavior
        that preserves the control's content (icon/text) while changing the background.
        
        Args:
            flash_color: Color to flash (e.g., 'offwhite', 'red')
            flash_duration_ms: Duration of flash in milliseconds (default: 100)
        """
        # Default implementation: subclasses should override to provide proper flash
        # that preserves their content
        def _restore_after_flash():
            time.sleep(flash_duration_ms / 1000.0)
            # Restore original state by calling _render()
            if hasattr(self, '_render'):
                self._render()
        
        thread = threading.Thread(target=_restore_after_flash, daemon=True)
        thread.start()

