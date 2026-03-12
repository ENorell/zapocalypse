from typing import NamedTuple, Protocol, Optional
from enum import Enum, auto
from dataclasses import dataclass
from collections import deque
from datetime import timedelta
import math
import random
from abc import ABC, abstractmethod
from domain.model import WorldVector, MovableEntity, MoveType

import domain.events as events


class Object(Protocol):
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
        if MoveType.FLY in movable_entity.move_types:
            return True
        return False

class TraversalEffect(Protocol):
    def on_enter(self) -> None: ...
    def on_traverse(self) -> None: ...
    def on_exit(self) -> None: ...

class NoTraversalEffect:
    def on_enter(self) -> None: ...
    def on_traverse(self) -> None: ...
    def on_exit(self) -> None: ...
        
class SpeedTraversalEffect:
    def on_enter(self) -> None: ...
    def on_traverse(self) -> None: ...
    def on_exit(self) -> None: ...

class DamageTraversalEffect:
    def __init__(self): ...

class Tile(Protocol):
    tile_name: str
    tile_type: TileType
    position: WorldVector
    traversal_rule: TraversalRule
    traversal_effect: TraversalEffect

class WallTile:
    def __init__(self, tile_name: str, position: WorldVector, traversal_rule: TraversalRule, traversal_effect: TraversalEffect):
        self.tile_name = tile_name
        self.tile_type = TileType.WALL
        self.position = position
        self.traversal_rule = traversal_rule
        self.traversal_effect = traversal_effect

class WaterTile:
    def __init__(self, tile_name: str, position: WorldVector, traversal_rule: TraversalRule, traversal_effect: TraversalEffect):
        self.tile_name = tile_name
        self.tile_type = TileType.WATER
        self.position = position
        self.traversal_rule = traversal_rule
        self.traversal_effect = traversal_effect