from dataclasses import dataclass
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



class PixelController:
    def __init__(self, state_machine: StateMachine):
        self._state_machine = state_machine

    def update(self, device_events: DeviceEvent) -> None:
        user_input = UserInput(
            confirm=device_events.space_key or device_events.left_click,
            delta_time=device_events.delta_time,
            selected_ids=device_events.entity_ids,
            right=device_events.right_key,
            left=device_events.left_key,
            up=device_events.up_key,
            down=device_events.down_key,
        )

        self._state_machine.update(user_input)
