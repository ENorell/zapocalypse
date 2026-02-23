from typing import NamedTuple, Protocol, Optional, Set
from enum import Enum, auto
from dataclasses import dataclass
from collections import deque
from datetime import timedelta
from .game_objects import Element
import math
import random

from abc import ABC, abstractmethod


class Spell(ABC):
    @abstractmethod
    def execute(self) -> None: ...

class CreateWall(Spell):
    def __init__(self, caster, level):
        self._caster = caster
        self._level = level
        self._elements = (Element.ROOT, Element.ROOT, Element.WATER)
    
    def execute(self) -> None:
        self._level.spawn_wall(self._caster.position)

class FireBall(Spell):
    def __init__(self, caster, level):
        self._caster = caster
        self._level = level
    def execute(self) -> None:
        self._level.spawn("fire", self._caster.position, self._caster.facing_direction)
