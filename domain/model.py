from __future__ import annotations
from typing import NamedTuple, Protocol, Optional, Sequence
from enum import Enum, auto
from dataclasses import dataclass
from collections import deque
from datetime import timedelta
import math
import random
from abc import ABC, abstractmethod

import domain.events as events

class WorldVector(NamedTuple):
    x: float
    y: float

class HasPosition(Protocol):
    position: WorldVector

class Element(Enum):
    FIRE = auto()
    WATER = auto()
    WIND = auto()
    ROOT = auto()
    THUNDER = auto()

class WallType(Enum):
    BUSH = auto()
    STONE = auto()

class TileType(Enum):
    MUD = auto()
    WATER = auto()
    FIRE = auto()

class Spawnable(Protocol):
    @property
    def position(self) -> WorldVector:
        ...

    def on_spawn(self):
        ...

# @dataclass(frozen=True) # Måste vara mutable om den ska kunna gå att flytta?
class ElementOrb:
    def __init__(self, element: Element, position: WorldVector):
        self.element = element
        self.position = position
        self.movable = True

    def move_entity(self, destination: WorldVector) -> None:
        self.position = destination

    def on_spawn(self):
        ...

class Wall:
    def __init__(self, wall_type: WallType, position: WorldVector):#, on_touching_effects: Sequence[Optional[Effect]]):
        self.wall_type = wall_type
        self.position = position
        self.movable = False

    def on_spawn(self):
        ...

class Tile:
    def __init__(self, tile_type: TileType, position: WorldVector):#, on_traverse_effects: Sequence[Optional[Effect]]):
        self.tile_type = tile_type
        self.position = position
        # self.on_traverse_effects = on_traverse_effects

    def on_spawn(self):
        ...

class Level:
    def __init__(self) -> None:
        self.walls: list[Wall] = []
        self.orbs: list[ElementOrb] = []
        self.tiles: list[Tile] = []
        self.events: list[events.Event] = []

    # @property
    # def walls(self) -> list[Wall]:
    #     return self.walls

    # @property
    # def orbs(self) -> list[ElementOrb]:
    #     return self.orbs

    def remove_orb(self, orb: ElementOrb) -> None:
        self.orbs.remove(orb)