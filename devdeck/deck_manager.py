import logging
import threading
import time
from typing import Optional, TYPE_CHECKING

from devdeck.deck_context import DeckContext

# Try to import key press queue for GUI integration
try:
    from devdeck.gui.key_press_queue import put_key_press
    _GUI_AVAILABLE = True
except ImportError:
    _GUI_AVAILABLE = False
    put_key_press = None

if TYPE_CHECKING:
    from devdeck_core.decks.deck_controller import DeckController

# Constants
DEFAULT_DECK_BRIGHTNESS = 50
DEFAULT_SCREEN_SAVER_TIMEOUT_SECONDS = 1800  # 30 minutes (30 * 60 seconds)
SCREEN_SAVER_BRIGHTNESS = 5  # Very low brightness when in screen saver mode
IDLE_CHECK_INTERVAL = 1.0  # Check idle time every second


class DeckManager:
    """
    Manages Stream Deck devices and their active deck controllers.
    
    Handles deck initialization, deck switching, key callbacks, and cleanup.
    """
    
    def __init__(self, deck, screen_saver_timeout: Optional[int] = None) -> None:
        """
        Initialize the deck manager.
        
        Args:
            deck: Stream Deck device instance
            screen_saver_timeout: Timeout in seconds before screen saver activates (default: 1800 = 30 minutes)
        """
        self.__logger = logging.getLogger('devdeck')
        self.__deck = deck
        self.__deck.set_brightness(DEFAULT_DECK_BRIGHTNESS)
        self.__deck.reset()
        self.__deck.set_key_callback(self.key_callback)
        self.decks: list['DeckController'] = []
        
        # Screen saver state
        self._screen_saver_timeout = screen_saver_timeout if screen_saver_timeout is not None else DEFAULT_SCREEN_SAVER_TIMEOUT_SECONDS
        self._last_activity_time = time.time()
        self._screen_saver_active = False
        self._original_brightness = DEFAULT_DECK_BRIGHTNESS
        self._screen_saver_lock = threading.Lock()
        self._idle_check_thread: Optional[threading.Thread] = None
        self._stop_threads = False
        self._device_unavailable = False  # Flag to track if device is unavailable (e.g., power saving mode)
        
        # Start idle check thread
        self._idle_check_thread = threading.Thread(target=self._check_idle_time, daemon=True)
        self._idle_check_thread.start()

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
        
        # Ensure deck is ready before rendering
        try:
            # Reset deck to clear any previous state
            self.__deck.reset()
            self.__logger.debug("Deck reset completed")
            
            # Render the active deck
            active_deck = self.get_active_deck()
            if active_deck:
                self.__logger.info("Rendering active deck...")
                active_deck.render(DeckContext(self, self.__deck))
                self.__logger.info("Deck rendering completed")
            else:
                self.__logger.error("No active deck to render")
        except Exception as e:
            self.__logger.error(f"Error setting active deck: {e}", exc_info=True)
            raise

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
        # Update activity time on any key press
        if state:
            with self._screen_saver_lock:
                self._last_activity_time = time.time()
                # Reset device unavailable flag on successful key press (device is available)
                self._device_unavailable = False
                
                # Wake from screen saver if active
                if self._screen_saver_active:
                    self._wake_from_screen_saver()
            
            # Note: Key press notifications with MIDI hex are handled by the controls themselves
            # (e.g., KetronKeyMappingControl.pressed() will call put_key_press with MIDI hex)
            # We don't send a notification here to avoid duplicate messages
            
            # Proceed with normal key handling
            self.get_active_deck().pressed(key)
        else:
            self.get_active_deck().released(key)

    def _check_idle_time(self) -> None:
        """
        Background thread function to check idle time and activate screen saver.
        """
        while not self._stop_threads:
            try:
                time.sleep(IDLE_CHECK_INTERVAL)
                
                with self._screen_saver_lock:
                    if self._stop_threads:
                        break
                    
                    # Skip screen saver activation if device is unavailable
                    if self._device_unavailable:
                        continue
                    
                    if not self._screen_saver_active:
                        idle_time = time.time() - self._last_activity_time
                        if idle_time >= self._screen_saver_timeout:
                            self._activate_screen_saver()
            except Exception as ex:
                self.__logger.error("Error in idle check thread: %s", ex, exc_info=True)
    
    def _activate_screen_saver(self) -> None:
        """
        Activate screen saver: dim brightness.
        """
        if self._screen_saver_active:
            return
        
        self.__logger.info("Activating screen saver (idle timeout: %d seconds)", self._screen_saver_timeout)
        
        # Save current brightness
        self._original_brightness = DEFAULT_DECK_BRIGHTNESS  # Could get current brightness if API supports it
        
        # Dim brightness - handle device unavailable errors
        try:
            self.__deck.set_brightness(SCREEN_SAVER_BRIGHTNESS)
            # Set screen saver active flag only if brightness was set successfully
            self._screen_saver_active = True
        except Exception as ex:
            error_msg = str(ex).lower()
            error_type = type(ex).__name__
            
            # Check for TransportError or "No HID Device" errors
            is_transport_error = (
                "TransportError" in error_type or
                "transport" in error_type.lower() or
                "no hid device" in error_msg or
                "hid device" in error_msg or
                "could not open" in error_msg
            )
            
            if is_transport_error:
                # Device is unavailable (e.g., Mac power saving mode)
                self.__logger.warning(
                    "Cannot activate screen saver: Device unavailable (likely due to power saving mode). "
                    "Error: %s", ex
                )
                # Mark device as unavailable to skip future screen saver attempts
                self._device_unavailable = True
                # Don't set screen saver active flag - abort activation
                return
            else:
                # Unexpected error - re-raise it
                self.__logger.error("Unexpected error activating screen saver: %s", ex, exc_info=True)
                raise
    
    def _wake_from_screen_saver(self) -> None:
        """
        Wake from screen saver: restore brightness and re-render active deck.
        """
        if not self._screen_saver_active:
            return
        
        self.__logger.info("Waking from screen saver")
        
        # Set screen saver inactive
        self._screen_saver_active = False
        
        # Restore brightness - handle device unavailable errors
        try:
            self.__deck.set_brightness(self._original_brightness)
            # Reset device unavailable flag on successful brightness change
            self._device_unavailable = False
        except Exception as ex:
            error_msg = str(ex).lower()
            error_type = type(ex).__name__
            
            # Check for TransportError or "No HID Device" errors
            is_transport_error = (
                "TransportError" in error_type or
                "transport" in error_type.lower() or
                "no hid device" in error_msg or
                "hid device" in error_msg or
                "could not open" in error_msg
            )
            
            if is_transport_error:
                # Device is unavailable
                self.__logger.warning(
                    "Cannot restore brightness: Device unavailable. Error: %s", ex
                )
                # Mark device as unavailable
                self._device_unavailable = True
            else:
                # Unexpected error - log but continue
                self.__logger.error("Unexpected error restoring brightness: %s", ex, exc_info=True)
        
        # Re-render active deck (even if brightness restore failed)
        try:
            active_deck = self.get_active_deck()
            if active_deck is not None:
                active_deck.render(DeckContext(self, self.__deck))
        except Exception as ex:
            self.__logger.warning("Error re-rendering deck after wake: %s", ex)
    
    def clear_screen(self) -> None:
        """
        Clear the screen by setting all keys to black background and black text.
        
        Similar to screen saver but uses black colors instead of dimming brightness.
        """
        try:
            self.__logger.info("Clearing Stream Deck screen (setting all keys to black)")
            
            keys = self.__deck.key_count()
            context = DeckContext(self, self.__deck)
            
            # Set each key to black background and black text
            for key_no in range(keys):
                with context.renderer(key_no) as r:
                    r.background_color('black')
                    r.text('')\
                        .font_size(100)\
                        .color('black')\
                        .center_vertically()\
                        .center_horizontally()\
                        .end()
            
            self.__logger.info("Stream Deck screen cleared")
        except Exception as ex:
            self.__logger.error("Error clearing Stream Deck screen: %s", ex, exc_info=True)
    
    def close(self) -> None:
        """
        Close the deck manager and clean up resources.
        
        Disposes all deck controllers and clears all key images.
        """
        # Check if screen saver is active before stopping threads
        was_screen_saver_active = False
        with self._screen_saver_lock:
            was_screen_saver_active = self._screen_saver_active
            self._stop_threads = True
            self._screen_saver_active = False
        
        # Wait for threads to stop
        if self._idle_check_thread is not None and self._idle_check_thread.is_alive():
            self._idle_check_thread.join(timeout=2.0)
            if self._idle_check_thread.is_alive():
                self.__logger.warning("Idle check thread did not stop within timeout")
        
        # Restore brightness if screen saver was active
        if was_screen_saver_active:
            self.__deck.set_brightness(self._original_brightness)
        
        # Clear the screen to black before closing (for clean shutdown)
        try:
            self.clear_screen()
        except Exception as ex:
            self.__logger.warning("Error clearing screen during close: %s", ex)
        
        # Clean up decks
        keys = self.__deck.key_count()
        for deck in self.decks:
            deck.dispose()
        for key_no in range(keys):
            self.__deck.set_key_image(key_no, None)