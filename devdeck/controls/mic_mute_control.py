import logging
import os
from pathlib import Path
from typing import Optional, Any

from pulsectl import pulsectl

from devdeck_core.controls.deck_control import DeckControl


class MicMuteControl(DeckControl):

    def __init__(self, key_no: int, **kwargs: Any) -> None:
        self.pulse: Optional[pulsectl.Pulse] = None
        self.__logger = logging.getLogger('devdeck')
        super().__init__(key_no, **kwargs)

    def initialize(self) -> None:
        if self.pulse is None:
            self.pulse = pulsectl.Pulse('MicMuteControl')
        self.__render_icon()

    def pressed(self) -> None:
        mic = self.__get_mic()
        if mic is None:
            return
        if self.pulse is not None:
            self.pulse.source_mute(mic.index, mute=(not mic.mute))
        self.__render_icon()

    def __get_mic(self) -> Optional[Any]:
        sources = self.pulse.source_list()

        selected_mic = [mic for mic in sources if mic.description == self.settings['microphone']]
        if len(selected_mic) == 0:
            possible_mics = [output.description for output in sources]
            self.__logger.warning("Microphone '%s' not found in list of possible inputs:\n%s",
                                  self.settings['microphone'],
                                  '\n'.join(possible_mics))
            return None
        return selected_mic[0]

    def __render_icon(self) -> None:
        with self.deck_context() as context:
            mic = self.__get_mic()
            if mic is None:
                with context.renderer() as r:
                    r \
                        .text('MIC \nNOT FOUND') \
                        .color('red') \
                        .center_vertically() \
                        .center_horizontally() \
                        .font_size(85) \
                        .text_align('center') \
                        .end()
                return
            # Use pathlib for path handling
            assets_dir = Path(__file__).parent.parent / 'assets' / 'font-awesome'
            if mic.mute == 0:
                with context.renderer() as r:
                    r.image(str(assets_dir / 'microphone.png')).end()
            else:
                with context.renderer() as r:
                    r.image(str(assets_dir / 'microphone-mute.png')).end()

    def settings_schema(self) -> dict:
        return {
            'microphone': {
                'type': 'string'
            }
        }