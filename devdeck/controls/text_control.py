from devdeck_core.controls.deck_control import DeckControl


def wrap_text_to_lines(text, max_chars_per_line=6):
    """
    Wrap text into multiple lines with a maximum number of characters per line.
    
    Args:
        text (str): The text to wrap
        max_chars_per_line (int): Maximum characters per line (default: 6)
    
    Returns:
        str: Text with newlines inserted, with each line having at most max_chars_per_line characters
    """
    if not text:
        return text
    
    # Split by spaces to try to break at word boundaries when possible
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        word_length = len(word)
        
        # If a single word is longer than max_chars_per_line, break it
        if word_length > max_chars_per_line:
            # Add current line if it has content
            if current_line:
                lines.append(' '.join(current_line))
                current_line = []
                current_length = 0
            
            # Break the long word into chunks
            for i in range(0, word_length, max_chars_per_line):
                lines.append(word[i:i + max_chars_per_line])
        else:
            # Check if adding this word would exceed the limit
            potential_length = current_length + word_length + (1 if current_line else 0)
            
            if potential_length > max_chars_per_line and current_line:
                # Start a new line
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_length
            else:
                # Add to current line
                current_line.append(word)
                current_length = potential_length
    
    # Add the last line if it has content
    if current_line:
        lines.append(' '.join(current_line))
    
    # Join with \n escape sequence for better YAML readability
    # YAML will parse \n as a newline character
    return '\\n'.join(lines)


class TextControl(DeckControl):

    def __init__(self, key_no, **kwargs):
        super().__init__(key_no, **kwargs)

    def _render(self):
        """Helper method to render the text control"""
        with self.deck_context() as context:
            with context.renderer() as r:
                text = self.settings.get('text', '')
                # Convert \n escape sequences to actual newlines for rendering
                text = text.replace('\\n', '\n')
                font_size = self.settings.get('font_size', 80)
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

    def update_text(self, new_text):
        """
        Update the displayed text at runtime.
        
        Args:
            new_text (str): The new text to display on the key (will be wrapped to 6 chars per line)
        """
        # Wrap text to maximum 6 characters per line
        wrapped_text = wrap_text_to_lines(new_text, max_chars_per_line=6)
        self.settings['text'] = wrapped_text
        self._render()

    def settings_schema(self):
        """Define the settings schema for TextControl"""
        return {
            'text': {
                'type': 'string'
            },
            'font_size': {
                'type': 'integer'
            },
            'color': {
                'type': 'string'
            },
            'background_color': {
                'type': 'string'
            }
        }

