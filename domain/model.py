from typing import NamedTuple, Protocol, Optional
from enum import Enum, auto
from dataclasses import dataclass
from collections import deque
from datetime import timedelta
import math
import random
from abc import ABC, abstractmethod
import domain.events as events
from domain.spell import DotEffect # Circle ref problem?

class WorldVector(NamedTuple):
    x: float
    y: float


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

class Event(ABC): ...

class MovableEntity(Protocol):
    movable: bool

    def move_entity(self, destination: WorldVector) -> None:
        ...


class OrbCollector(Protocol): # Börjar bli lite väl mycket protocols kanske?
    def collect_orb(self, element: Element):
        ...

    def call_event(self, element: events.Event):
        ...

class OrbHolder(Protocol): # Börjar bli lite väl mycket protocols kanske?
    def remove_orb(self, orb: ElementOrb):
        ...


class Player:
    base_speed = 8.0
    max_no_elements = 3
    max_health = 100
    def __init__(self, position: WorldVector, elements: Optional[list[Element]]) -> None:
        #health
        self.position = position
        self._elements = deque(elements or [], self.max_no_elements)
        self.events: list[events.Event] = []
        self.movable = True
        self._move_types: list[MoveType] = []
        self._speed_buffs: list[int] = []
        self._health = self.max_health
        self._speed = self.base_speed
        self._active_effects: list[DotEffect] = []

    @property
    def elements(self) -> list[Element]:
        return list(self._elements)

    @property
    def move_types(self) -> list[MoveType]:
        return list(self._move_types)
    
    @property
    def health(self) -> int:
        return self._health
    
    @property
    def speed(self) -> float:
        return self._speed
    
    def add_dot_effect(self, effect: DotEffect) -> None:
        # for active_effect in self._active_effects:
        #     if active_effect.effect == effect:
        #         active_effect._remaining_ticks # Ändringar i Tick gör att denna kanske blir mer komplicerad?
        self._active_effects.append(effect)

    def remove_dot_effect(self, effect: DotEffect) -> None:
        if effect in self._active_effects:
            self._active_effects.remove(effect)

    def apply_speed_change(self, delta_speed: float) -> None:
        self._speed = max(self._speed + delta_speed, 0)
    
    def get_base_speed(self) -> float:
        """Return speed after effects etc."""
        return self.base_speed

    def take_damage(self, damage_number: int):
        self._health = max(self._health - damage_number, 0)

    def heal(self, heal_number: int):
        self._health = min(self._health + heal_number, self.max_health)

    def collect_orb(self, element: Element) -> None:
        self._elements.appendleft(element)

    def apply_move_type(self, move_type: MoveType) -> None:
        self._move_types.append(move_type)

    def move_entity(self, destination: WorldVector) -> None:
        self.position = destination

    def call_event(self, event: events.Event):
        self.events.append(event)


class Component[T, S](Protocol):
    def update(self, arg1: T, arg2: S) -> None: ...

class Player2:
    def __init__(self) -> None:
        # State
        self.position
        self.velocity
        #present_component
        #
        ...
    def update(self, user_input, world) -> None:
        ...


class Projectile:
    def __init__(self, position: WorldVector, direction: WorldVector, velocity: float, effect) -> None: # dependent on effect...?
        self.position = position
        self._direction = direction
        self._velocity = velocity
        self._effect = effect
    
    def fly(self, duration: timedelta) -> None: # Here or in system?
        magnitude = math.hypot(*self._direction)
        distance = self._velocity * duration.total_seconds()
        if not distance or not magnitude:
            return
        self.position = WorldVector(
            self.position.x + self._direction.x * distance / magnitude,
            self.position.y + self._direction.y * distance / magnitude,
        )
        
    def collide(self): ...


class Level:
    def __init__(self) -> None:
        self.walls: list[Wall] = []
        self.orbs: list[ElementOrb] = []
        self.tiles: list[Tile] = []
        self.events: list[events.Event] = []

    def remove_orb(self, orb: ElementOrb) -> None:
        self.orbs.remove(orb)
