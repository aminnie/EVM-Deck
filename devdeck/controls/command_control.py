import logging
import os
import subprocess
from pathlib import Path
from subprocess import Popen, DEVNULL
from typing import Any, List, Optional

from devdeck_core.controls.deck_control import DeckControl


class CommandControl(DeckControl):
    """
    Control that executes system commands when a key is pressed.
    
    For security, commands can be restricted via the 'allowed_commands' setting.
    If provided, only commands in the allowlist will be executed.
    """
    
    def __init__(self, key_no: int, **kwargs: Any) -> None:
        self.__logger = logging.getLogger('devdeck')
        super().__init__(key_no, **kwargs)

    def initialize(self) -> None:
        with self.deck_context() as context:
            with context.renderer() as r:
                icon_path = Path(self.settings['icon']).expanduser()
                r.image(str(icon_path)).end()

    def pressed(self) -> None:
        """Execute the configured command when key is pressed."""
        command = self.settings.get('command')
        if not command:
            self.__logger.error("No command specified in settings")
            return
        
        # Security: Check if command is in allowlist if allowlist is configured
        allowed_commands: Optional[List[str]] = self.settings.get('allowed_commands')
        if allowed_commands is not None:
            # Extract command name (first part before space)
            command_name = str(command).split()[0] if isinstance(command, (str, list)) else str(command)
            if command_name not in allowed_commands:
                self.__logger.error("Command '%s' is not in allowed_commands list", command_name)
                return
        
        try:
            Popen(command, stdout=DEVNULL, stderr=DEVNULL)
        except (FileNotFoundError, PermissionError) as ex:
            self.__logger.error("Error executing command %s: %s", command, str(ex))
        except subprocess.SubprocessError as ex:
            self.__logger.error("Subprocess error executing command %s: %s", command, str(ex))
        except (ValueError, TypeError) as ex:
            self.__logger.error("Invalid command format %s: %s", command, str(ex))
    
    def settings_schema(self) -> dict:
        """
        Define the settings schema for CommandControl.
        
        Returns:
            Dictionary defining the settings schema
        """
        return {
            'command': {
                'type': ['string', 'list'],
                'required': True,
                'description': 'Command to execute (string or list of arguments)'
            },
            'icon': {
                'type': 'string',
                'required': True,
                'description': 'Path to icon file'
            },
            'allowed_commands': {
                'type': 'list',
                'required': False,
                'description': 'Optional list of allowed command names for security. If provided, only commands in this list will be executed.'
            }
        }