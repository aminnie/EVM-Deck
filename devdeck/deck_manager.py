import logging
from typing import Optional, TYPE_CHECKING

from devdeck.deck_context import DeckContext

if TYPE_CHECKING:
    from devdeck_core.decks.deck_controller import DeckController

# Constants
DEFAULT_DECK_BRIGHTNESS = 50


class DeckManager:
    """
    Manages Stream Deck devices and their active deck controllers.
    
    Handles deck initialization, deck switching, key callbacks, and cleanup.
    """
    
    def __init__(self, deck) -> None:
        """
        Initialize the deck manager.
        
        Args:
            deck: Stream Deck device instance
        """
        self.__logger = logging.getLogger('devdeck')
        self.__deck = deck
        self.__deck.set_brightness(DEFAULT_DECK_BRIGHTNESS)
        self.__deck.reset()
        self.__deck.set_key_callback(self.key_callback)
        self.decks: list['DeckController'] = []

    def set_active_deck(self, deck: 'DeckController') -> None:
        """
        Set the active deck controller.
        
        Clears context for all existing decks and adds the new deck to the stack.
        
        Args:
            deck: Deck controller to activate
        """
        self.__logger.info("Setting active deck: %s", type(deck).__name__)
        for deck_itr in self.decks:
            deck_itr.clear_deck_context()
        self.decks.append(deck)
        self.get_active_deck().render(DeckContext(self, self.__deck))

    def get_active_deck(self) -> Optional['DeckController']:
        """
        Get the currently active deck controller.
        
        Returns:
            The active deck controller, or None if no decks are active
        """
        if not self.decks:
            return None
        return self.decks[-1]

    def pop_active_deck(self) -> None:
        """
        Pop the active deck from the stack and activate the previous one.
        
        Does nothing if only one deck is in the stack (root deck).
        """
        if len(self.decks) == 1:
            return
        popped_deck = self.decks.pop()
        self.__logger.info("Exiting deck: %s", type(popped_deck).__name__)
        popped_deck.clear_deck_context()
        self.get_active_deck().render(DeckContext(self, self.__deck))

    def key_callback(self, deck, key: int, state: bool) -> None:
        """
        Handle key press/release events from the Stream Deck.
        
        Args:
            deck: Stream Deck device instance
            key: Key number that was pressed/released
            state: True if key was pressed, False if released
        """
        if state:
            self.get_active_deck().pressed(key)
        else:
            self.get_active_deck().released(key)

    def close(self) -> None:
        """
        Close the deck manager and clean up resources.
        
        Disposes all deck controllers and clears all key images.
        """
        keys = self.__deck.key_count()
        for deck in self.decks:
            deck.dispose()
        for key_no in range(keys):
            self.__deck.set_key_image(key_no, None)