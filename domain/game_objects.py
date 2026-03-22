from typing import NamedTuple, Protocol
from enum import Enum, auto
from dataclasses import dataclass

class WorldVector(NamedTuple):
    x: float
    y: float

class MovableEntity(Protocol):
    ...

class Effect(Protocol):
    ...

class Spawnable(Protocol):
    position: WorldVector

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