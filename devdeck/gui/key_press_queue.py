"""
Shared queue for Stream Deck key press events between DeckManager and GUI.

This module provides a thread-safe queue that allows the DeckManager to send
key press events to the GUI for display.
"""

import queue
import threading

# Global queue for Stream Deck key press events
_key_press_queue: queue.Queue = queue.Queue()
_queue_lock = threading.Lock()


def get_queue() -> queue.Queue:
    """Get the global key press queue"""
    return _key_press_queue


def put_key_press(key_no: int, key_name: str = None):
    """
    Put a key press event in the queue.
    
    Args:
        key_no: Stream Deck key number (0-14 or higher)
        key_name: Optional key name (e.g., "Fill", "Break")
    """
    try:
        _key_press_queue.put_nowait((key_no, key_name))
    except queue.Full:
        # Queue is full, skip this event
        pass

