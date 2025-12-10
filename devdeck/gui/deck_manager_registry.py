"""
Registry for accessing the active DeckManager from the GUI.

This allows the GUI to clear the screen before stopping the application.
"""
import threading
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from devdeck.deck_manager import DeckManager

# Thread-safe registry for the active DeckManager
_active_deck_manager: Optional['DeckManager'] = None
_registry_lock = threading.Lock()


def register_deck_manager(deck_manager: 'DeckManager') -> None:
    """Register the active DeckManager instance."""
    global _active_deck_manager
    with _registry_lock:
        _active_deck_manager = deck_manager


def unregister_deck_manager() -> None:
    """Unregister the active DeckManager instance."""
    global _active_deck_manager
    with _registry_lock:
        _active_deck_manager = None


def get_deck_manager() -> Optional['DeckManager']:
    """Get the active DeckManager instance, if available."""
    with _registry_lock:
        return _active_deck_manager

