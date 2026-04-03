from typing import NamedTuple, Protocol, Optional
from enum import Enum, auto
from dataclasses import dataclass
from collections import deque
from datetime import timedelta
import math
import random
from abc import ABC, abstractmethod
from __future__ import annotations

import domain.events as events
from spell import Number, ExactNumber, RandomNumber

@dataclass(frozen=True)
class WorldVector():
    x: float
    y: float

    def __add__(self, other: WorldVector) -> WorldVector:
        return WorldVector((self.x + other.x), (self.y + other.y))
    
    def __sub__(self, other: WorldVector) -> WorldVector:
        return WorldVector((self.x - other.x), (self.y - other.y))

class HasPosition(Protocol):
    position: WorldVector

class MovableEntity(Protocol):
    movable: bool

    def move_entity(self, destination: WorldVector) -> None:
        ...

class OrbCollector(Protocol):
    def collect_orb(self, element: Element):
        ...

    def call_event(self, element: events.Event):
        ...

class OrbHolder(Protocol):
    def remove_orb(self, orb: ElementOrb):
        ...

class Player:
    base_run_speed = 8
    max_no_elements = 3
    def __init__(self, position: WorldVector, elements: Optional[list[Element]], health: int) -> None:
        #health
        self.position = position
        self._elements = deque(elements or [], self.max_no_elements)
        self.events: list[events.Event] = []
        self.movable = True
        self._move_types: list[MoveType] = []
        self._health = health

    @property
    def elements(self) -> list[Element]:
        return list(self._elements)

    @property
    def move_types(self) -> list[MoveType]:
        return list(self._move_types)
    
    @property
    def health(self) -> int:
        return self._health
    
    def get_speed(self) -> float:
        """Return speed after effects etc."""
        return self.base_run_speed

    def collect_orb(self, element: Element) -> None:
        self._elements.appendleft(element)

    def apply_move_type(self, move_type: MoveType) -> None:
        self._move_types.append(move_type)

    def call_event(self, event: events.Event):
        self.events.append(event)

    def move_entity(self, destination: WorldVector) -> None:
        self.position = destination

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

class MoveType(Enum):
    DEFAULT = auto()
    FLY = auto()
    SWIM = auto()

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
    def __init__(self, wall_type: WallType, position: WorldVector):
        self.wall_type = wall_type
        self.position = position
        self.movable = False

    def on_spawn(self):
        ...

@dataclass(frozen=True)
class Tile():
    tile_type: TileType
    position: WorldVector

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

@dataclass(frozen=True)
class Context:
    caster: Player
    level: Level
    players: list[Player]

class AllOrbs:
    def resolve(self, context: Context) -> list[ElementOrb]:
        return context.level.orbs
class AllWalls:
    def resolve(self, context: Context) -> list[Wall]:
        return context.level.walls
    

    # traversal_rule: TraversalRule
    # traversal_effect: Effect

    # def on_enter(self) -> None: ...
    # def on_traverse(self) -> None: ...
    # def on_exit(self) -> None: ... 

    # def on_spawn(self):
    #     ...


# class TraversalRule(Protocol):
#     def can_traverse(self, movable_entity: MovableEntity) -> bool: ...

# class DefaultTraversalRule:
#     def can_traverse(self, movable_entity: MovableEntity) -> bool:
#         return True
    
# class NoTraverseTraversalRule: 
#     def can_traverse(self, movable_entity: MovableEntity) -> bool:
#         return False

# class FlyTraversalRule:
#     def can_traverse(self, movable_entity: MovableEntity) -> bool:
#         # if MoveType.FLY in movable_entity.move_types:
#         #     return True
#         return False