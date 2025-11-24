import logging
from typing import Optional, TYPE_CHECKING

from devdeck.deck_context import DeckContext

if TYPE_CHECKING:
    from devdeck_core.decks.deck_controller import DeckController


class DeckManager:
    def __init__(self, deck) -> None:
        self.__logger = logging.getLogger('devdeck')
        self.__deck = deck
        self.__deck.set_brightness(50)
        self.__deck.reset()
        self.__deck.set_key_callback(self.key_callback)
        self.decks: list['DeckController'] = []

    def set_active_deck(self, deck: 'DeckController') -> None:
        self.__logger.info("Setting active deck: %s", type(deck).__name__)
        for deck_itr in self.decks:
            deck_itr.clear_deck_context()
        self.decks.append(deck)
        self.get_active_deck().render(DeckContext(self, self.__deck))

    def get_active_deck(self) -> Optional['DeckController']:
        if not self.decks:
            return None
        return self.decks[-1]

    def pop_active_deck(self) -> None:
        if len(self.decks) == 1:
            return
        popped_deck = self.decks.pop()
        self.__logger.info("Exiting deck: %s", type(popped_deck).__name__)
        popped_deck.clear_deck_context()
        self.get_active_deck().render(DeckContext(self, self.__deck))

    def key_callback(self, deck, key: int, state: bool) -> None:
        if state:
            self.get_active_deck().pressed(key)
        else:
            self.get_active_deck().released(key)

    def close(self) -> None:
        keys = self.__deck.key_count()
        for deck in self.decks:
            deck.dispose()
        for key_no in range(keys):
            self.__deck.set_key_image(key_no, None)