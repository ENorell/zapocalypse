from typing import NamedTuple, Protocol, Optional
from enum import Enum, auto
from dataclasses import dataclass
from collections import deque
from datetime import timedelta
import math
import random
from abc import ABC, abstractmethod
from domain.model import WorldVector, Player

import domain.events as events

class Object(Protocol):
    ...

class TileType(Enum):
    WATER = auto()
    FIRE = auto()
    WALL = auto()

class TraversalRule(Protocol):
    def try_traverse(self, player: Player) -> bool: ...

class DefaultTraversalRule:
    def try_traverse(self, player: Player) -> bool:
        return True
    
class NoTraverseTraversalRule: 
    def try_traverse(self, player: Player) -> bool:
        return False

class FlyTraversalRule:
    def try_traverse(self, player: Player) -> bool:
        return False

class TraversalEffect(Protocol):
    def on_enter(self): ...
    def on_traverse(self): ...
    def on_exit(self): ...
        
class SpeedTraversalEffect:
    def __init__(self):
        ...
        
    def on_enter(self): ...
    def on_traverse(self): ...
    def on_exit(self): ...

class DamageTraversalEffect:
    def __init__(self): ...

class Tile(Protocol):
    tile_name: TileType
    position: WorldVector

    def traversing_object(self, object: Object):
        ...

class WaterTile:
    def __init__(self, position: WorldVector, traversal_rule = TraversalRule, traversal_effect = TraversalEffect):
        self.tile_name = TileType.WATER
        self.position = position

    def traversing_object(self, object: Object): ...