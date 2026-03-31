from typing import Protocol, Optional, Iterable
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

class SpawnPositions(Protocol):
    def resolve(self) -> Iterable[WorldVector]:
        ...

class AnySpawnPositions():
    def __init__(self, base_spawn_positions: Iterable[WorldVector]):
        self.base_spawn_positions = base_spawn_positions

    def resolve(self) -> Iterable[WorldVector]:
        yield from self.base_spawn_positions

# class NonOccupiedSpawnPositions():
#     def __init__(self, base_spawn_positions: SpawnPositions, occupying_objects: list[Spawnable]):
#         self.base_spawn_positions = base_spawn_positions
#         self.occupying_objects = occupying_objects

#     def resolve(self) -> Iterable[WorldVector]:
#         base_positions = set(self.base_spawn_positions.resolve())
#         for pos in base_positions:
#             if pos not any (obj.size.collides.occupied_positions:
#                 yield pos

class SpawnPositionsAroundPoint():
    def __init__(self, spawn_positions: SpawnPositions, point: WorldVector):
        self.spawn_positions = spawn_positions
        self.point = point

    def resolve(self) -> Iterable[WorldVector]:
        x, y = self.point.x, self.point.y

        offsets = [(0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1), (-1,0), (-1,1)]

        allowed_positions = {
            WorldVector(x + dx, y + dy)
            for dx, dy in offsets
        }

        for pos in self.spawn_positions.resolve():
            if pos in allowed_positions:
                yield pos 

class PositionSelector(Protocol):
    def __init__(self, spawn_positions: SpawnPositions):
        ...

    def select(self) -> WorldVector | None:
        ...

class RandomPositionSelector():
    def __init__(self, spawn_positions: SpawnPositions):
        self.spawn_positions = spawn_positions

    def select(self) -> WorldVector | None:
        new_base_positions = list(self.spawn_positions.resolve()) # Set sen list??
        if not new_base_positions:
            return None
        return random.choice(new_base_positions)
    
class IngestedPositionSelector():
    def __init__(self, spawn_position: WorldVector):
        self.spawn_position = spawn_position

    def select(self) -> WorldVector | None:
        return self.spawn_position

class OrbSpawner():
    def __init__(self, level: Level, event: Optional[Event] = None):
        self.level = level
        self.event = event

    def create_object(self, spawn_position: WorldVector, element: Element) -> ElementOrb:
        return ElementOrb(element, spawn_position)

    def _trigger_spawn_event(self) -> None:
        ...

    def spawn_object(self, position_selector: PositionSelector, element: Element) -> None:
        position = position_selector.select()
        if position is None:
            return
        orb = self.create_object(position, element)
        self.level.orbs.append(orb)

    def spawn_object_at(self, position: WorldVector, element: Element) -> None:
        orb = self.create_object(position, element)
        self.level.orbs.append(orb)

class WallSpawner():
    def __init__(self, level: Level, event: Optional[Event] = None):
        self.level = level
        self.event = event

    def create_object(self, spawn_position: WorldVector, wall_type: WallType) -> Wall:
        return Wall(wall_type, spawn_position)

    def _trigger_spawn_event(self) -> None:
        ...

    def spawn_object(self, position_selector: PositionSelector, wall_type: WallType) -> None:
        position = position_selector.select()
        if position is None:
            return
        wall = self.create_object(position, wall_type)  # orb is ElementOrb
        wall.on_spawn()
        self.level.walls.append(wall)

    def spawn_object_at(self, position: WorldVector, wall_type: WallType) -> None:
        wall = self.create_object(position, wall_type)
        self.level.walls.append(wall)
