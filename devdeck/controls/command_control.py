import logging
import os
import subprocess
from subprocess import Popen, DEVNULL

from devdeck_core.controls.deck_control import DeckControl


class CommandControl(DeckControl):
    def __init__(self, key_no, **kwargs):
        self.__logger = logging.getLogger('devdeck')
        super().__init__(key_no, **kwargs)

    def initialize(self):
        with self.deck_context() as context:
            with context.renderer() as r:
                r.image(os.path.expanduser(self.settings['icon'])).end()

    def pressed(self):
        try:
            Popen(self.settings['command'], stdout=DEVNULL, stderr=DEVNULL)
        except (FileNotFoundError, PermissionError) as ex:
            self.__logger.error("Error executing command %s: %s", self.settings['command'], str(ex))
        except subprocess.SubprocessError as ex:
            self.__logger.error("Subprocess error executing command %s: %s", self.settings['command'], str(ex))
        except (ValueError, TypeError) as ex:
            self.__logger.error("Invalid command format %s: %s", self.settings['command'], str(ex))