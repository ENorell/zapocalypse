from typing import Protocol, Optional
from enum import Enum, auto
from dataclasses import dataclass
import random
from domain.game_objects import WorldVector, Spawnable, ElementOrb, Element, Wall, WallType
from domain.model import Level
from domain.events import Event, OrbSpawned

class Spawner(Protocol):
    def create_object(self) -> Spawnable:
        ...

    def spawn_object(self) -> None:
        spawnable = self.create_object()
        spawnable.on_spawn() # Tvingande? Inga argument i metoden..

class OrbSpawner():
    def __init__(self, level: Level, event: Optional[Event] = None):
        self.level = level
    
    def _free_spawn_positions(self) -> list[WorldVector]:

        physical_objects = self.level.orbs + self.level.walls
        occupied_positions = {(obj.position.x, obj.position.y) for obj in physical_objects}

        free_positions = [
            WorldVector(x, y)
            for x in range(7)
            for y in range(8)
            if (x, y) not in occupied_positions
        ]

        return free_positions

    def _spawn_position(self) -> WorldVector:
        position = random.choice(self._free_spawn_positions())

        return position

    def create_object(self) -> Spawnable:
        element = random.choice(list(Element))
        position = self._spawn_position()
        return ElementOrb(element, position)

    def _trigger_spawn_event(self) -> None:
        ...

    def spawn_object(self) -> None:
        spawnable = self.create_object()
        spawnable.on_spawn()
        self.level.orbs.append(spawnable)
        # self._trigger_spawn_event(spawnable) # Event?