from typing import NamedTuple, Protocol, Optional, Set
from enum import Enum, auto
from dataclasses import dataclass
from collections import deque
from datetime import timedelta
from .game_rules import WorldVector
import math
import random

from abc import ABC, abstractmethod

class WallType(Enum):
    BUSH = auto()
    STONE = auto()

@dataclass(frozen=True)
class Wall:
    wall_type: WallType
    position: WorldVector
    not_stackable: bool = True

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
    not_stackable: bool = True

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
