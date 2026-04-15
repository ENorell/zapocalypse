from typing import Protocol, Callable
from abc import ABC, abstractmethod
from datetime import timedelta
from enum import Enum, auto
from dataclasses import dataclass, field

from interactors.presenter_model import PresenterModel


class Presenter(Protocol):
    def draw(self, models: list[PresenterModel]) -> None: ...


@dataclass(frozen=True)
class UserInput:
    delta_time: timedelta = field(default_factory=timedelta)
    right: bool = False
    left: bool = False
    up: bool = False
    down: bool = False
    confirm: bool = False
    selected_ids: list[int] = field(default_factory=list) #Set?


# class Scene(ABC):
#     @abstractmethod
#     def update(self, user_input: UserInput) -> None: ...
# 
#     def start(self) -> None: ...
# 
#     def cleanup(self) -> None: ...


class SceneChoice(Enum):
    FIGHT = auto()
    START_MENU = auto()


class StopGame(Exception):
    """Exception raised in order to exit the game"""
    ...


class SceneSwitch(Exception):  # Counts as "control flow"? Bad idea?
    """Exception raised in order to switch states"""
    def __init__(self, scene: SceneChoice):
        super().__init__()
        self.scene = scene


from domain.spell import World

class System(Protocol):
    def update(self, user_input: UserInput, context: World): ...


class Scene:
    def __init__(self,
                 context: World,
                 *systems: System,  #Callable[[UserInput, Context], None], #Effect[Context]],
                 start: Callable[["Scene"], None] = lambda _: None,
                 cleanup: Callable[["Scene"], None] = lambda _: None,
                 ) -> None:
        self._context = context
        self._systems = systems
        self._start    = start
        self._cleanup  = cleanup

    def update(self, user_input: UserInput) -> None: # Should also take context/world?
        #map(lambda system: system(user_input).apply(self.context), self.systems)
        #map(lambda system: system(user_input, self.context), self.systems)
        #map(lambda system: system.update(user_input, self.context), self.systems)
        for system in self._systems:
            system.update(user_input, self._context)

    def start(self) -> None:
        self._start(self)

    def cleanup(self) -> None:
        self._cleanup(self)
