from typing import NamedTuple, Protocol, Optional, Set
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

# class Physics:
#     def __init__(self, walls: list[Wall], player: Player) -> None:#entities: list[Wall | Player]):
#         self._walls = walls #level?
#         self._player = player

#     def has_collision(self, target: WorldVector) -> bool:
#         return any(
#             math.dist(collide_entity.position, target) < 1
#             for collide_entity in self._walls
#         )