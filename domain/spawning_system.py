from typing import Protocol, Optional
from enum import Enum, auto
from dataclasses import dataclass
import random
from domain.game_objects import WorldVector, Spawnable, ElementOrb, Element, Wall, WallType
from domain.model import Level
from domain.events import Event, OrbSpawned
from domain.spell import AllOrbs, AllWalls, Context, Target

class Spawner(Protocol):
    def create_object(self) -> Spawnable:
        ...

    def spawn_object(self) -> None:
        spawnable = self.create_object()
        spawnable.on_spawn() # Tvingande? Inga argument i metoden..

class SpawnPositions(Protocol):
    def resolve(self) -> list[WorldVector]: ... # Context överflödigt? Används inte alltid?

class LevelSpawnPositions():
    def __init__(self, level: Level):
        self.level = level

    def resolve(self) -> list[WorldVector]: 
        # return [WorldVector(x, y)
        #             for x in range(self.level.width)
        #             for y in range(self.level.height)] # ??

        return [WorldVector(x, y)
            for x in range(8)
            for y in range(8)
            ]

class SpawnPositionsAroundPlayer():
    def __init__(self, base_spawn_positions: SpawnPositions, target: Target, context: Context):
        self.base_spawn_positions = base_spawn_positions
        self.target = target
        self.context = context

    def resolve(self) -> list[WorldVector]:
        target_position = self.target.resolve(self.context.caster)

        x = target_position.x
        y = target_position.y

        offsets = [(0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1), (-1,0), (-1,1)]

        return [WorldVector(x + dx, y + dy) for dx, dy in offsets if WorldVector(x + dx, y + dy) in self.base_spawn_positions]

class OccupiedSpawnPositions():
    def __init__(self, base_spawn_positions: SpawnPositions, occupying_objects: list[Spawnable]):
        self.base_spawn_positions = base_spawn_positions
        self.occupying_objects = occupying_objects

    def resolve(self) -> list[WorldVector]: 
        positions = self.base_spawn_positions.resolve(self)
        objecter = [obj for obj in self.occupying_objects if obj.position in positions]

        return [o.position for o in objecter]

class FreeSpawnPositions():
    def __init__(self, base_spawn_positions: SpawnPositions, occupied_positions: SpawnPositions):
        self.base_spawn_positions = base_spawn_positions
        self.occupied_positions = occupied_positions

    def resolve(self) -> list[WorldVector]:
        base = self.base_spawn_positions.resolve()

        occupied = {(p.x, p.y) for p in self.occupied_positions.resolve()}

        return [p for p in base if (p.x, p.y) not in occupied]

class PositionSelector(Protocol):
    def __init__(self, spawn_positions: SpawnPositions):
        ...

    def select(self) -> WorldVector | None:
        ...

class RandomPositionSelector():
    def __init__(self, spawn_positions: SpawnPositions):
        self.spawn_positions = spawn_positions

    def select(self) -> WorldVector | None:

        positions = self.spawn_positions.resolve()
        if not positions:
            return None
        return random.choice(positions)

# class OrbSpawner():
#     def __init__(self, context: Context, spawn_position: PositionSelector, event: Optional[Event] = None):
#         self.spawn_position = spawn_position
#         self.event = event
#         self.context = context

#     def create_object(self, element: Element) -> Spawnable:
#         element = element
#         position = self.spawn_position.select(self.context, self.spawn_position)
#         return ElementOrb(element, position)

#     def _trigger_spawn_event(self) -> None:
#         ...

#     def spawn_object(self) -> None:
#         spawnable = self.create_object()
#         spawnable.on_spawn()
#         self.context.level.orbs.append(spawnable)
#         # self._trigger_spawn_event(spawnable) # Event?


class OrbSpawner():
    def __init__(self, level: Level, event: Optional[Event] = None):
        self.level = level
        self.event = event

    def create_object(self, spawn_position: PositionSelector, element: Element) -> Spawnable:
        position = spawn_position.select()
        return ElementOrb(element, position)

    def _trigger_spawn_event(self) -> None:
        ...

    def spawn_object(self, spawn_position: PositionSelector, element: Element) -> None:
        spawnable = self.create_object(spawn_position, element)
        spawnable.on_spawn()
        self.level.orbs.append(spawnable)

level = Level()
spawner = OrbSpawner(level)
level_spawn_positions = LevelSpawnPositions(level)
spawn_positions = FreeSpawnPositions(level_spawn_positions, OccupiedSpawnPositions(LevelSpawnPositions, level.orbs + level.walls))
random_selector = RandomPositionSelector(spawn_positions)
spawner.spawn_object(random_selector, Element.FIRE)
