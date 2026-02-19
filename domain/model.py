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


# spell_book = {
#     {Element.FIRE, Element.WIND, Element.THUNDER}: "fire storm",
#     (Element.FIRE, Element.FIRE, Element.WIND): "Fire Tornado"
# }

class Spell(ABC):
    @abstractmethod
    def execute(self) -> None: ...

class CreateWall(Spell):
    def __init__(self, caster, level):
        self._caster = caster
        self._level = level
    def execute(self) -> None:
        self._level.spawn_wall(self._caster.position)

class FireBall(Spell):
    def __init__(self, caster, level):
        self._caster = caster
        self._level = level
    def execute(self) -> None:
        self._level.spawn("fire", self._caster.position, self._caster.facing_direction)

class Element(Enum):
    FIRE = auto()
    WATER = auto()
    WIND = auto()
    ROOT = auto()
    THUNDER = auto()

@dataclass(frozen=True)
class ElementOrb:
    element: Element
    position: WorldVector


class Player:
    base_run_speed = 8
    max_no_elements = 3
    def __init__(self, position: WorldVector, elements: Optional[list[Element]] = None) -> None:
        #health
        self.position = position
        self._elements = deque(elements or [], self.max_no_elements)

    def get_speed(self) -> float:
        """Return speed after effects etc."""
        return self.base_run_speed

    def try_give_element(self, element: Element) -> bool:
        if len(self._elements) >= self.max_no_elements:
            return False
        self._elements.append(element)
        return True

    def give_element(self, element: Element):
        self._elements.appendleft(element)


class Command(ABC):
    was_successful = False
    @abstractmethod
    def execute(self): ...

class Move(Command):
    def __init__(self, player: Player, direction: WorldVector, duration: timedelta) -> None:
        self._player = player
        self._direction = direction
        self._duration = duration

        self.was_successful = False

    @property
    def target_position(self) -> WorldVector:
        distance = self._player.get_speed() * self._duration.total_seconds()
        magnitude = math.hypot(*self._direction)
        return magnitude and WorldVector(
            self._player.position.x + (self._direction.x / magnitude * distance),
            self._player.position.y + (self._direction.y / magnitude * distance),
        ) or WorldVector(0, 0)

    def __enter__(self):
        pass

    def __exit__(self):
        pass

    def execute(self) -> None:
        self._player.position = self.target_position
        self.was_successful = True

    def undo(self) -> None:
        pass

class PickupOrb(Command):
    def __init__(self, player: Player, orbs: list[ElementOrb]):
        self._player = player
        self._orbs = orbs
        
    def execute(self) -> None:
        touching_orb = next(
            (
                orb for orb in self._orbs
                if touches(orb.position, self._player)
            ),
            None
        )
        if not touching_orb: return
        self._orbs.remove(touching_orb)
        self._player.give_element(touching_orb)
        self.was_successful = True

class HasPosition(Protocol):
    position: WorldVector

def touches(target: WorldVector, *others: HasPosition) -> bool:
    return any(
        math.dist(other.position, target) < 1
        for other in others
    )

class Wall(Enum):
    WALL = auto()
    BUSH = auto()
    STONE = auto()

@dataclass(frozen=True)
class MaterializedWall:
    wall: Wall
    position: WorldVector

class Level:
    def __init__(self, player: Player, materialized_walls: list[MaterializedWall], orbs: list[ElementOrb]):
        self._player = player
        self._walls: list[MaterializedWall] = materialized_walls
        self._orbs: list[ElementOrb] = orbs

    @property
    def player(self) -> Player:
        return self._player

    def get_walls(self) -> list[MaterializedWall]:
        return list(self._walls)

    def get_orbs(self) -> list[ElementOrb]:
        return list(self._orbs)

    def _collides_with_wall(self, target: WorldVector) -> bool:
        return any(
            math.dist(collide_entity.position, target) < 1
            for collide_entity in self._walls
        )

    def push_player(self, direction: WorldVector, distance: float) -> None:
        current_x, current_y = self._player.position
        move_x, move_y = direction
        target_position = WorldVector(current_x + move_x * distance, current_y + move_y * distance)
        if not self._collides_with_wall(target_position):
            self._player.position = target_position

    def push(self, direction: WorldVector, duration: timedelta):
        current_x, current_y = self._player.position
        move_x, move_y = direction
        distance = self._player.get_current_speed() * duration.total_seconds() / math.hypot(*direction)
        target_position = WorldVector(current_x + move_x * distance, current_y + move_y * distance)
        if not self._collides_with_wall(target_position):
            self._player.position = target_position

    def spawn_orb(self, orb_position: WorldVector) -> None:
        self._orbs.append(
            ElementOrb(
                element=random.choice(list(Element)),
                position=orb_position,
            )
        )

    def spawn_orb_in_free_position(self, spawn_area_x, spawn_area_y) -> None:
        occupied_positions = {orb.position for orb in self._orbs}
        all_positions = {WorldVector(x, y) for x in range(spawn_area_x) for y in range(spawn_area_y)}

        all_free_positions = list(all_positions - occupied_positions)

        if not all_free_positions:
            raise ValueError("Cannot spawn orb, no free positions")

        position_new_orb = random.choice(all_free_positions)
        self.spawn_orb(position_new_orb)

    def get_touching_orb(self) -> Optional[ElementOrb]:
        return next(
            (
                orb for orb in self._orbs
                if math.dist(orb.position, self._player.position) < 1
            ),
            None
        )

    def can_pickup_orb(self) -> bool:
        return bool(self.get_touching_orb())

    def do_pickup_orb(self) -> None:
        assert (orb := self.get_touching_orb())
        self._player.give_element(orb.element)
        self._orbs.remove(orb)

    def try_pickup_orb(self) -> bool:
        """Attempts to pick up an orb, returns a boolean to signal success or not"""
        if orb:=self.get_touching_orb():
            if self._player.try_give_element(orb.element):
                self._orbs.remove(orb)
                return True
        return False

class Physics:
    def __init__(self, walls: list[MaterializedWall], player: Player) -> None:#entities: list[Wall | Player]):
        self._walls = walls #level?
        self._player = player

    def has_collision(self, target: WorldVector) -> bool:
        return any(
            math.dist(collide_entity.position, target) < 1
            for collide_entity in self._walls
        )
    

# def command_move(player, target, walls) -> None:
#     if touches(target, *walls):
#         return
#     player.position = target


# def pickup_orb(player, orbs: list[ElementOrb]) -> None:
#     touching_orb = next(
#             (
#                 orb for orb in orbs
#                 if touches(orb.position, player)
#             ),
#             None
#         )
#     if not touching_orb: return
#     orbs.remove(touching_orb)
#     player.give(touching_orb)