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
        self.events: list[events.Event] = []

    def get_speed(self) -> float:
        """Return speed after effects etc."""
        return self.base_run_speed

    @property
    def elements(self) -> list[Element]:
        return list(self._elements)

    def give_element(self, element: Element):
        self._elements.appendleft(element)


@dataclass(frozen=True)
class Wall:
    position: WorldVector


class Level:
    def __init__(self, walls: list[Wall], orbs: Optional[list[ElementOrb]] = None):
        self._walls = walls
        self._orbs: list[ElementOrb] = orbs or []
        self.events: list[events.Event] = []

    @property
    def walls(self) -> list[Wall]:
        return list(self._walls)

    @property
    def orbs(self) -> list[ElementOrb]:
        return list(self._orbs)

    def collides_with_wall(self, target: WorldVector) -> bool:
        return any(
            math.dist(collide_entity.position, target) < 1
            for collide_entity in self._walls
        )

    def get_touching_orb(self, target: WorldVector) -> Optional[ElementOrb]:
        return next(
            (
                orb for orb in self._orbs
                if math.dist(orb.position, target) < 1
            ),
            None
        )

    def remove_orb(self, orb: ElementOrb) -> None:
        self._orbs.remove(orb)

    def spawn_orb(self) -> None:
        self._orbs.append(
            ElementOrb(
                element=random.choice(list(Element)),
                position=WorldVector(2, 3),
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




class Spell(ABC):
    #@abstractmethod
    def execute(self) -> None: ...

class FireStorm(Spell): ...


spell_book = {
    (Element.FIRE, Element.WIND, Element.THUNDER): "fire storm",
    (Element.FIRE, Element.FIRE, Element.WIND): "Fire Tornado",
    (Element.WIND, Element.WIND, Element.FIRE): FireStorm()
}

def conjure_spell(elements: list[Element]) -> Optional[Spell]:
    spell_ingredients: tuple[Element, Element, Element] = tuple(elements[:3])
    return spell_book.get(spell_ingredients)


