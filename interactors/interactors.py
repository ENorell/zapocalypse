from typing import Protocol
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum, auto
from datetime import timedelta
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import NamedTuple


class WorldVector(NamedTuple):
    x: float
    y: float


class WorldGraphic(Enum):
    PLAYER = auto()
    WALL = auto()
    ORB = auto()

class UiGraphic(Enum):
    START_GAME_BUTTON = auto()
    QUIT_GAME_BUTTON = auto()

@dataclass(frozen=True)
class UiPresenterModel:
    id: int #default to none?
    graphic: UiGraphic
    to_highlight: bool = False

@dataclass(frozen=True)
class WorldPresenterModel:
    id: int
    graphic: WorldGraphic
    position: WorldVector

PresenterModel = UiPresenterModel | WorldPresenterModel

class Presenter(Protocol):
    def draw(self, models: list[PresenterModel]) -> None: ...


@dataclass(frozen=True)
class UserInput:
    delta_time: timedelta
    right: bool = False
    left: bool = False
    up: bool = False
    down: bool = False
    confirm: bool = False
    selected_ids: list[int] = field(default_factory=list) #Set?


class Scene(ABC):
    @abstractmethod
    def update(self, user_input: UserInput) -> None: ...

    def start(self) -> None: ...

    def cleanup(self) -> None: ...


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

