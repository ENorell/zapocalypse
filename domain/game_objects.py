from typing import NamedTuple, Protocol
from enum import Enum, auto
from dataclasses import dataclass

class WorldVector(NamedTuple):
    x: float
    y: float

class Spawnable(Protocol):
    def on_spawn(self):
        ...

class Element(Enum):
    FIRE = auto()
    WATER = auto()
    WIND = auto()
    ROOT = auto()
    THUNDER = auto()

@dataclass(frozen=True)
class ElementOrb():
    element: Element
    position: WorldVector

    def on_spawn(self):
        ...

class WallType(Enum):
    BUSH = auto()
    STONE = auto()

@dataclass(frozen=True)
class Wall():
    wall_type: WallType
    position: WorldVector

    def on_spawn(self):
        ...

class Tile():
    def on_spawn(self):
        ...