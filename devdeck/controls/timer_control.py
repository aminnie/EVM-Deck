import datetime
import logging
import os
import threading
from pathlib import Path
from time import sleep
from typing import Optional, Any

from devdeck_core.controls.deck_control import DeckControl


class TimerControl(DeckControl):

    def __init__(self, key_no: int, **kwargs: Any) -> None:
        self.start_time: Optional[datetime.datetime] = None
        self.end_time: Optional[datetime.datetime] = None
        self.thread: Optional[threading.Thread] = None
        super().__init__(key_no, **kwargs)

    def initialize(self) -> None:
        with self.deck_context() as context:
            with context.renderer() as r:
                # Use pathlib for path handling
                icon_path = Path(__file__).parent.parent / 'assets' / 'font-awesome' / 'stopwatch.png'
                r.image(str(icon_path)).end()

    def pressed(self) -> None:
        if self.start_time is None:
            self.start_time = datetime.datetime.now()
            self.thread = threading.Thread(target=self._update_display)
            self.thread.start()
        elif self.end_time is None:
            self.end_time = datetime.datetime.now()
            self.thread.join(timeout=5.0)
            if self.thread.is_alive():
                logger = logging.getLogger('devdeck')
                logger.warning("Timer thread did not terminate within timeout")
            with self.deck_context() as context:
                with context.renderer() as r:
                    r.text(TimerControl.time_diff_to_str(self.end_time - self.start_time))\
                        .font_size(120)\
                        .color('red')\
                        .center_vertically().center_horizontally().end()
        else:
            self.start_time = None
            self.end_time = None
            with self.deck_context() as context:
                with context.renderer() as r:
                    # Use pathlib for path handling
                    icon_path = Path(__file__).parent.parent / 'assets' / 'font-awesome' / 'stopwatch.png'
                    r.image(str(icon_path)).end()

    def _update_display(self) -> None:
        while self.end_time is None:
            if self.start_time is None:
                sleep(1)
                continue
            cutoff = datetime.datetime.now() if self.end_time is None else self.end_time
            with self.deck_context() as context:
                with context.renderer() as r:
                    r.text(TimerControl.time_diff_to_str(cutoff - self.start_time)) \
                        .font_size(120) \
                        .center_vertically().center_horizontally().end()
            sleep(1)

    @staticmethod
    def time_diff_to_str(diff: datetime.timedelta) -> str:
        seconds = diff.total_seconds()
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f'{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}'
