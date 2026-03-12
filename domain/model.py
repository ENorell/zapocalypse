from typing import NamedTuple, Protocol, Optional
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
    z: float = 0.0

class MoveType(Enum):
    DEFAULT = auto()
    WALK = auto()
    FLY = auto()
    SWIM = auto()

class MovableEntity(Protocol):
    def get_move_speed(self) -> float:
        ...

    def add_move_type(self, move_type: MoveType):
        ...

    @property
    def move_types(self) -> set[MoveType]: ...

class TileType(Enum):
    WATER = auto()
    FIRE = auto()
    WALL = auto()
    GRASS = auto()

class TraversalRule(Protocol):
    def can_traverse(self, movable_entity: MovableEntity) -> bool: ...

class MoveTypeTraversalRule:
    def __init__(self, allowed_move_types: set[MoveType]):
        self.allowed_move_types = allowed_move_types
        
    def can_traverse(self, movable_entity: MovableEntity) -> bool: 
        if self.allowed_move_types & movable_entity.move_types:
            return True
        return False

class DefaultTraversalRule:
    def can_traverse(self, movable_entity: MovableEntity) -> bool:
        return True
    
class NoTraverseTraversalRule:
    def can_traverse(self, movable_entity: MovableEntity) -> bool:
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
    def on_enter(self) -> None: ...
    def on_traverse(self) -> None: ...
    def on_exit(self) -> None: ...

class Tile():
    def __init__(self, tile_type: TileType, position: WorldVector, traversal_rule: TraversalRule, traversal_effect: TraversalEffect):
        self.tile_type = tile_type
        self.position = position
        self.traversal_rule = traversal_rule
        self.traversal_effect = traversal_effect

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
class ElementOrb():
    element: Element
    position: WorldVector
    stackable = False

class WallType(Enum):
    BUSH = auto()
    STONE = auto()

@dataclass(frozen=True)
class Wall():
    wall_type: WallType
    position: WorldVector
    stackable = False



class Player:
    base_move_speed = 8
    max_no_elements = 3
    max_no_move_types = 2
    def __init__(self, position: WorldVector, elements: Optional[list[Element]] = None, move_types: Optional[list[MoveType]] = None) -> None:
        #health
        self.position = position
        self._elements = deque(elements or [], self.max_no_elements)
        self.events: list[events.Event] = []
        self._move_types = deque(move_types or [], self.max_no_move_types)

    @property
    def elements(self) -> list[Element]:
        return list(self._elements)

    @property
    def move_types(self) -> set[MoveType]:
        return set(self._move_types)

    def get_move_speed(self) -> float:
        """Return speed after effects etc."""
        return self.base_move_speed
    
    def add_move_type(self, move_type: MoveType):
        return self._move_types.appendleft(move_type)
    
    def remove_move_type(self, move_type: MoveType):
        return self._move_types.remove(move_type)

    def give_element(self, element: Element):
        self._elements.appendleft(element)

class Level:
    def __init__(self, walls: list[Wall], tiles: list[Tile], orbs: Optional[list[ElementOrb]] = None):
        self._tiles: list[Tile] = tiles or [] 
        self._walls: list[Wall] = walls or []
        self._orbs: list[ElementOrb] = orbs or []
        self.events: list[events.Event] = []

    @property
    def walls(self) -> list[Wall]:
        return list(self._walls)

    @property
    def orbs(self) -> list[ElementOrb]:
        return list(self._orbs)

    @property
    def tiles(self) -> list[Tile]:
        return list(self._tiles)

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

    def spawn_tile(self, tile: Tile) -> None:
        self._tiles.append(tile)

    def touches_tile(self, target: WorldVector, player: Player) -> bool:
        return any(
            math.dist(touching_tile.position, target) < 1
            for touching_tile in self._tiles if not touching_tile.traversal_rule.can_traverse(movable_entity = player)
        )

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

    # def get_free_positions(self, object_to_spawn: HasPosition, objects: list[HasPosition]) -> set[tuple]:
    #     z_position = object.position.z

    #     free_positions: set[WorldVector] = {object.position for object in self_} 

    #     for object in objects:
    #         if object.not_stackable:
                # free_positions.add(object.position)

    # def spawn_object_in_free_position(self, object: HasPosition) -> None:

    #     all_free_positions = self.free_spawn_positions(object.position.z)

    #     if not all_free_positions:
    #         return

    #     position_new_orb = random.choice(all_free_positions)
        
    #     self.spawn_orb(position_new_orb)


def move(player: Player, target: WorldVector, level: Level) -> None:
    if level.collides_with_wall(target):
        player.events.append(events.Collision())
        return
    
    if level.touches_tile(target, player):
        player.events.append(events.Collision())
        return

    if orb := level.get_touching_orb(target):
        level.remove_orb(orb)
        player.give_element(orb.element)
        player.events.append(events.OrbPickup())

    player.position = target

class Spell(ABC):
    #@abstractmethod
    def execute(self) -> None: ...

class FireStorm(Spell): ...

spell_book = {
    # (Element.FIRE, Element.WIND, Element.THUNDER): "fire storm",
    # (Element.FIRE, Element.FIRE, Element.WIND): "Fire Tornado"
    (Element.WIND, Element.WIND, Element.FIRE): FireStorm()
}

def conjure_spell(elements: list[Element]) -> Optional[Spell]:
    if len(elements) < 3:
        return None
    spell_ingredients: tuple[Element, Element, Element] = (elements[0], elements[1], elements[2])
    return spell_book.get(spell_ingredients)