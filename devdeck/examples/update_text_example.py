"""
Example: How to update text on Stream Deck keys at runtime

This example demonstrates different ways to update the text displayed on
TextControl keys after the application is running.
"""

# Example 1: Update text from within a control
# If you're inside a control or deck controller method:

class MyControl(DeckControl):
    def some_method(self):
        # Get the parent deck controller (if you have access to it)
        # For example, from within a control that has access to the deck:
        active_deck = self.get_active_deck()  # If such a method exists
        
        # Update text on key 0
        if active_deck:
            active_deck.update_text(0, "New Text")


# Example 2: Update text from a deck controller method
# If you're inside a deck controller:

class MyDeckController(DeckController):
    def some_method(self):
        # Direct update using the convenience method
        self.update_text(0, "Updated Text")
        
        # Or get the control and update it directly
        text_control = self.get_control(0, TextControl)
        if text_control:
            text_control.update_text("Another Update")


# Example 3: Update text from external code (if you have access to deck_manager)
# This would typically be from a separate thread, API endpoint, or event handler:

def update_key_text(deck_manager, key_no, new_text):
    """
    Update text on a key from external code.
    
    Args:
        deck_manager: The DeckManager instance
        key_no: The key number to update (0-14)
        new_text: The new text to display
    """
    active_deck = deck_manager.get_active_deck()
    if active_deck:
        success = active_deck.update_text(key_no, new_text)
        if success:
            print(f"Updated key {key_no} to '{new_text}'")
        else:
            print(f"Failed to update key {key_no}")


# Example 4: Update multiple keys at once
def update_multiple_keys(deck_manager, updates):
    """
    Update multiple keys at once.
    
    Args:
        deck_manager: The DeckManager instance
        updates: Dictionary mapping key_no to new_text
                 Example: {0: "Voice 1", 1: "Voice 2", 2: "Voice 3"}
    """
    active_deck = deck_manager.get_active_deck()
    if not active_deck:
        return
    
    for key_no, new_text in updates.items():
        active_deck.update_text(key_no, new_text)


# Example 5: Update text based on key mappings from key_mappings.json
def update_texts_from_mappings(deck_manager, key_mappings):
    """
    Update all text controls based on key mappings.
    
    Args:
        deck_manager: The DeckManager instance
        key_mappings: List of mapping dictionaries from key_mappings.json
    """
    active_deck = deck_manager.get_active_deck()
    if not active_deck:
        return
    
    for mapping in key_mappings:
        key_no = mapping['key_no']
        key_name = mapping['key_name']
        active_deck.update_text(key_no, key_name)

