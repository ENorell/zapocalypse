from __future__ import annotations
from typing import NamedTuple, Protocol
from enum import Enum, auto
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class WorldVector():
    x: float
    y: float

    def __add__(self, other: WorldVector) -> WorldVector:
        return WorldVector((self.x + other.x), (self.y + other.y))
    
    def __sub__(self, other: WorldVector) -> WorldVector:
        return WorldVector((self.x - other.x), (self.y - other.y))

class GameObject:
    def __init__(self, position: WorldVector, radius: float):
        self.position = position
        self.radius = radius

class MovableEntity(Protocol):
    ...

class Effect(Protocol):
    ...

class Spawnable(Protocol):
    @property
    def position(self) -> WorldVector:
        ...

    def on_spawn(self):
        ...

class Element(Enum):
    FIRE = auto()
    WATER = auto()
    WIND = auto()
    ROOT = auto()
    THUNDER = auto()

    # def collides_with(self, other: Size, pos_self: WorldVector, pos_other: WorldVector) -> bool:
    #     if isinstance(other, CircleSize):
    #         return math.dist((pos_self.x, pos_self.y), (pos_other.x, pos_other.y)) < (self.radius + other.radius)
    #     else:
    #         return other.collides_with(self, pos_other, pos_self)

@dataclass(frozen=True)
class ElementOrb():
    element: Element
    position: WorldVector

    # def can_spawn(target_pos: WorldVector, target_size: Size, collidable_objects: list[Spawnable]) -> bool:
    #     if size.

class WallType(Enum):
    BUSH = auto()
    STONE = auto()

@dataclass(frozen=True)
class Wall():
    wall_type: WallType
    position: WorldVector

    def on_spawn(self):
        ...

class TileType(Enum):
    WATER = auto()
    FIRE = auto()
    WALL = auto()

class TraversalRule(Protocol):
    def can_traverse(self, movable_entity: MovableEntity) -> bool: ...

class DefaultTraversalRule:
    def can_traverse(self, movable_entity: MovableEntity) -> bool:
        return True
    
class NoTraverseTraversalRule: 
    def can_traverse(self, movable_entity: MovableEntity) -> bool:
        return False

class FlyTraversalRule:
    def can_traverse(self, movable_entity: MovableEntity) -> bool:
        # if MoveType.FLY in movable_entity.move_types:
        #     return True
        return False

# Ovan kanske ska implementeras på  

class Tile(Protocol):
    tile_name: str
    tile_type: TileType
    position: WorldVector
    traversal_rule: TraversalRule
    traversal_effect: Effect

    def on_enter(self) -> None: ...
    def on_traverse(self) -> None: ...
    def on_exit(self) -> None: ... 

    def on_spawn(self):
        ...