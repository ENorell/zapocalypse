from typing import NamedTuple, Protocol, Optional
from enum import Enum, auto
from dataclasses import dataclass
from collections import deque
from datetime import timedelta
import math
import random
from abc import ABC, abstractmethod

import domain.events as events
from domain.game_objects import ElementOrb, Wall, WorldVector, Element

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

class Level:
    def __init__(self) -> None:
        self.walls: list[Wall] = []
        self.orbs: list[ElementOrb] = []
        self.events: list[events.Event] = []

    # @property
    # def walls(self) -> list[Wall]:
    #     return self.walls

    # @property
    # def orbs(self) -> list[ElementOrb]:
    #     return self.orbs

    def collides_with_wall(self, target: WorldVector) -> bool:
        return any(
            math.dist((collide_entity.position.x, collide_entity.position.y),(target.x, target.y)) < 1
            for collide_entity in self.walls
        )

    def get_touching_orb(self, target: WorldVector) -> Optional[ElementOrb]:
        return next(
            (
                orb for orb in self.orbs
                if math.dist((orb.position.x, orb.position.y), (target.x, target.y)) < 1
            ),
            None
        )

    def remove_orb(self, orb: ElementOrb) -> None:
        self.orbs.remove(orb)