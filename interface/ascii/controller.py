from dataclasses import dataclass
from typing import Optional
from datetime import timedelta

from interactors.interactors import UserInput
from interface.state_machine import StateMachine

@dataclass
class DeviceEvent:
    entity_ids: list[int]
    delta_time: timedelta
    left_click: bool = False
    right_key: bool = False
    left_key: bool = False
    up_key: bool = False
    down_key: bool = False
    space_key: bool = False



class AsciiController:
    def __init__(self, state_machine: StateMachine):
        self._state_machine = state_machine
        self._current_selection: Optional[int] = None

    def update(self, device_events: DeviceEvent) -> None:
        if device_events.right_key:
            self._current_selection = next(
                (entity for entity in device_events.entity_ids if entity != self._current_selection),
                None
            )

        user_input = UserInput(
            confirm=device_events.space_key,
            delta_time=device_events.delta_time,
            selected_ids=[self._current_selection] if self._current_selection else [],
            right=device_events.right_key,
            left=device_events.left_key,
            up=device_events.up_key,
            down=device_events.down_key,
        )
        
        self._state_machine.update(user_input)
