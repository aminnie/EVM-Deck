import logging
import os
import subprocess
from pathlib import Path
from subprocess import Popen, DEVNULL
from typing import Any

from devdeck_core.controls.deck_control import DeckControl


class CommandControl(DeckControl):
    def __init__(self, key_no: int, **kwargs: Any) -> None:
        self.__logger = logging.getLogger('devdeck')
        super().__init__(key_no, **kwargs)

    def initialize(self) -> None:
        with self.deck_context() as context:
            with context.renderer() as r:
                icon_path = Path(self.settings['icon']).expanduser()
                r.image(str(icon_path)).end()

    def pressed(self) -> None:
        try:
            Popen(self.settings['command'], stdout=DEVNULL, stderr=DEVNULL)
        except (FileNotFoundError, PermissionError) as ex:
            self.__logger.error("Error executing command %s: %s", self.settings['command'], str(ex))
        except subprocess.SubprocessError as ex:
            self.__logger.error("Subprocess error executing command %s: %s", self.settings['command'], str(ex))
        except (ValueError, TypeError) as ex:
            self.__logger.error("Invalid command format %s: %s", self.settings['command'], str(ex))