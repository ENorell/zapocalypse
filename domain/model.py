from typing import NamedTuple, Protocol, Optional
from enum import Enum, auto
from dataclasses import dataclass
from collections import deque
from datetime import timedelta
import math
import random
from abc import ABC, abstractmethod



class WorldVector(NamedTuple):
    x: float
    y: float
    z: float = 0.0


class Element(Enum):
    FIRE = auto()
    WATER = auto()
    WIND = auto()
    ROOT = auto()
    THUNDER = auto()

class PhysicalObject(Protocol):
    @property
    def stackable(self) -> bool: ...
    @property
    def position(self) -> WorldVector: ...

@dataclass(frozen=True)
class ElementOrb:
    element: Element
    position: WorldVector
    stackable = False

class WallType(Enum):
    BUSH = auto()
    STONE = auto()

@dataclass(frozen=True)
class Wall:
    wall_type: WallType
    position: WorldVector
    stackable = False

class Event(ABC): ...


class Player:
    base_run_speed = 8
    max_no_elements = 3
    def __init__(self, position: WorldVector, elements: Optional[list[Element]] = None) -> None:
        #health
        self.position = position
        self._elements = deque(elements or [], self.max_no_elements)
        self.events: list[Event] = []

    def get_speed(self) -> float:
        """Return speed after effects etc."""
        return self.base_run_speed

    @property
    def elements(self) -> list[Element]:
        return list(self._elements)

    def give_element(self, element: Element):
        self._elements.appendleft(element)


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
    def __init__(self, walls: list[Wall], orbs: Optional[list[ElementOrb]] = None):
        self._walls = walls
        self._orbs: list[ElementOrb] = orbs or []
        self.events: list[Event] = []

    @property
    def walls(self) -> list[Wall]:
        return list(self._walls)

    @property
    def orbs(self) -> list[ElementOrb]:
        return list(self._orbs)

    def free_spawn_positions(self, z_position: float) -> list[WorldVector]:

        physical_objects = self.orbs + self.walls
        occupied_positions = {(obj.position.x, obj.position.y) for obj in physical_objects if obj.position.z == z_position}

        free_positions = [
            WorldVector(x, y, z_position)
            for x in range(7)
            for y in range(8)
            if (x, y) not in occupied_positions
        ]

        return free_positions

    def collides_with_wall(self, target: WorldVector) -> bool:
        return any(
            math.dist(collide_entity.position, target) < 1
            for collide_entity in self._walls
        )

    def get_touching_orb(self, target: WorldVector) -> Optional[ElementOrb]:
        return next(
            (
                orb for orb in self._orbs
                if math.dist(orb.position[:2], target[:2]) < 1
            ),
            None
        )

    def remove_orb(self, orb: ElementOrb) -> None:
        self._orbs.remove(orb)

    def spawn_orb(self, orb_position_z: float) -> None:
        self._orbs.append(
            ElementOrb(
                element=random.choice(list(Element)),
                position=random.choice(self.free_spawn_positions(orb_position_z)),
            )
        )


def move(player: Player, target: WorldVector, level: Level) -> None:
    if level.collides_with_wall(target):
        player.events.append(events.Collision())
        return

    if orb := level.get_touching_orb(target):
        level.remove_orb(orb)
        player.give_element(orb.element)
        player.events.append(events.OrbPickup())

    player.position = target

