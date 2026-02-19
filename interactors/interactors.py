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

class UiGraphic(Enum):
    START_GAME_BUTTON = auto()
    QUIT_GAME_BUTTON = auto()

@dataclass(frozen=True)
class UiPresenterModel:
    id: int #default to none?
    graphic: UiGraphic
    to_highlight: bool = False

class HUDGraphic(Enum):
    ORB_INVENTORY_BACKDROP = auto()
    ORB_INVENTORY_SLOT_ONE = auto()
    ORB_INVENTORY_SLOT_TWO = auto()
    ORB_INVENTORY_SLOT_THREE = auto()

@dataclass(frozen=True)
class HUDPresenterModel:
    id: int
    graphic: HUDGraphic

class WorldGraphic(Enum):
    PLAYER = auto()
    WALL = auto()
    WALL_STONE = auto()
    WALL_HEDGE = auto()
    ORB_ELEMENT = auto()
    ORB_ELEMENT_FIRE = auto()
    ORB_ELEMENT_WATER = auto()
    ORB_ELEMENT_WIND = auto()
    ORB_ELEMENT_ROOT = auto()
    ORB_ELEMENT_THUNDER = auto()

# class WorldGraphics():
#     variant_to_graphic: dict[str, WorldGraphic] = {
#         "WALL": WorldGraphic.WALL,
#         "WALL_STONE": WorldGraphic.WALL_STONE,
#         "WALL_HEDGE": WorldGraphic.WALL_HEDGE,
#         "ELEMENT": WorldGraphic.ORB_ELEMENT,
#         "FIRE": WorldGraphic.ORB_ELEMENT_FIRE,
#         "WATER": WorldGraphic.ORB_ELEMENT_WATER,
#         "WIND": WorldGraphic.ORB_ELEMENT_WIND,
#         "ROOT": WorldGraphic.ORB_ELEMENT_ROOT,
#         "THUNDER": WorldGraphic.ORB_ELEMENT_THUNDER
#     }

#     variant_to_graphic: dict[Enum, WorldGraphic] = {
#         Wall.WALL: WorldGraphic.WALL,
#         Element.FIRE: WorldGraphic.ORB_ELEMENT_FIRE,
#         Element.WATER: WorldGraphic.ORB_ELEMENT_WATER,
#         Element.WIND: WorldGraphic.ORB_ELEMENT_WIND,
#         Element.ROOT: WorldGraphic.ORB_ELEMENT_ROOT,
#         Element.THUNDER: WorldGraphic.ORB_ELEMENT_THUNDER
#     }

#     @classmethod
#     def resolve_world_graphic(cls, *, variant: Enum | None = None, fallback: WorldGraphic):
#         try:
#             return WorldGraphic[variant.name]
#         except KeyError:
#             return fallback

#     @classmethod
#     def resolve_world_graphic(cls, *, variant: str | None = None, fallback_world_graphic: WorldGraphic) -> WorldGraphic:
#         if variant is not None:
#             return cls.variant_to_graphic.get(variant, fallback_world_graphic)
#         else:
#             return fallback_world_graphic

@dataclass(frozen=True)
class WorldPresenterModel:
    id: int
    graphic: WorldGraphic
    position: WorldVector

PresenterModel = UiPresenterModel | WorldPresenterModel | HUDPresenterModel

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

