from datetime import timedelta
import time

import keyboard
import mouse

from interface.ascii.controller import AsciiController, DeviceEvent
from interface.ascii.presenter import AsciiPresenter


class AsciiView:
    def __init__(self, controller: AsciiController, presenter: AsciiPresenter, fps: int) -> None:
        self._controller = controller
        self._presenter = presenter
        self._delta_time = timedelta(seconds=1/fps)
        self._is_running = True

    def run(self) -> None:
        print("\033[2J")

        while self._is_running:
            self._process_input()
            self._render()
            time.sleep(self._delta_time.total_seconds())

    def _render(self) -> None:
        print("\033[H")
        print(self._presenter.render_model.frame)
        
    def _process_input(self) -> None:
        self._is_running = not keyboard.is_pressed('esc')
        
        event = DeviceEvent(
            delta_time=self._delta_time,
            entity_ids=[id_ for id_ in self._presenter.render_model.ids],
            left_click=mouse.is_pressed(button='left'),
            space_key=keyboard.is_pressed('space'),
            right_key=keyboard.is_pressed('right'),
            left_key=keyboard.is_pressed('left'),
            up_key=keyboard.is_pressed('up'),
            down_key=keyboard.is_pressed('down'),
        )
        self._controller.update(event)
