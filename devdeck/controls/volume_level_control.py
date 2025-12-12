import logging
import os
from pathlib import Path
from typing import Optional, Any

from pulsectl import pulsectl

from devdeck_core.controls.deck_control import DeckControl
from devdeck.path_utils import get_assets_dir


class VolumeLevelControl(DeckControl):

    def __init__(self, key_no: int, **kwargs: Any) -> None:
        self.pulse: Optional[pulsectl.Pulse] = None
        self.volume: Optional[float] = None
        self.__logger = logging.getLogger('devdeck')
        super().__init__(key_no, **kwargs)

    def initialize(self) -> None:
        if self.pulse is None:
            self.pulse = pulsectl.Pulse('VolumeLevelControl')
        self.volume = float(self.settings['volume']) / 100
        self.__render_icon()

    def pressed(self) -> None:
        output = self.__get_output()
        if output is None:
            return
        if self.pulse is not None and self.volume is not None:
            self.pulse.volume_set_all_chans(output, self.volume)
        self.__render_icon()

    def __get_output(self) -> Optional[Any]:
        sinks = self.pulse.sink_list()
        selected_output = [output for output in sinks if output.description == self.settings['output']]
        if len(selected_output) == 0:
            possible_ouputs = [output.description for output in sinks]
            self.__logger.warning("Output '%s' not found in list of possible outputs:\n%s", self.settings['output'], '\n'.join(possible_ouputs))
            return None
        return selected_output[0]

    def __render_icon(self) -> None:
        with self.deck_context() as context:
            sink = self.__get_output()
            if sink is None:
                with context.renderer() as r:
                    r\
                        .text('OUTPUT \nNOT FOUND')\
                        .color('red')\
                        .center_vertically()\
                        .center_horizontally()\
                        .font_size(85)\
                        .text_align('center')\
                        .end()
                return

            with context.renderer() as r:
                if self.volume is not None:
                    r.text("{:.0f}%".format(round(self.volume, 2) * 100)) \
                        .center_horizontally() \
                        .end()
                # Use pathlib for path handling
                assets_dir = get_assets_dir()
                icon_path = assets_dir / 'font-awesome' / 'volume-up-solid.png'
                r.image(str(icon_path))\
                    .width(380)\
                    .height(380) \
                    .center_horizontally() \
                    .y(132) \
                    .end()
                if self.volume is not None and round(self.volume, 2) == round(sink.volume.value_flat, 2):
                    r.colorize('red')

    def settings_schema(self) -> dict:
        return {
            'output': {
                'type': 'string'
            },
            'volume': {
                'type': 'integer'
            }
        }