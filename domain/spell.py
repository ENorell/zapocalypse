import math
from collections import Counter
from datetime import timedelta
from typing import Protocol, Sequence, Optional, Callable, Iterable
from dataclasses import dataclass
from random import randint
import random

from domain.model import Element, Player, Level, WorldVector, ElementOrb, Wall, Projectile, MovableEntity, OrbCollector, OrbHolder, Tile, TileType, WallType, Spawnable
import domain.events as events


@dataclass(frozen=True)
class World:
    player: Player
    level: Level
    projectiles: list[Projectile]

class AllOrbs:
    def resolve(self, world: World) -> list[ElementOrb]:
        return world.level.orbs
class AllWalls:
    def resolve(self, world: World) -> list[Wall]:
        return world.level.walls
class AllTiles:
    def resolve(self, world: World) -> list[Tile]:
        return world.level.tiles

## Spawn factories


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
    def create_object(self, spawn_position: WorldVector, element: Element) -> ElementOrb:
        return ElementOrb(element, spawn_position)

    def _trigger_spawn_event(self) -> None:
        ...

    def spawn_object(self, position_selector: PositionSelector, element: Element, world: World) -> None:
        position = position_selector.select()
        if position is None:
            return
        orb = self.create_object(position, element)
        world.level.orbs.append(orb)

    def spawn_object_at(self, position: WorldVector, element: Element, world: World) -> None:
        orb = self.create_object(position, element)
        world.level.orbs.append(orb)

class WallSpawner():
    def create_object(self, spawn_position: WorldVector, wall_type: WallType) -> Wall:
        return Wall(wall_type, spawn_position)

    def _trigger_spawn_event(self) -> None:
        ...

    def spawn_object(self, position_selector: PositionSelector, wall_type: WallType, world: World) -> None:
        position = position_selector.select()
        if position is None:
            return
        wall = self.create_object(position, wall_type)  # orb is ElementOrb
        wall.on_spawn()
        world.level.walls.append(wall)

    def spawn_object_at(self, position: WorldVector, wall_type: WallType, world: World) -> None:
        wall = self.create_object(position, wall_type)
        world.level.walls.append(wall)


class TileSpawner():
    def create_object(self, spawn_position: WorldVector, tile_type: TileType) -> Tile:#, on_traverse_effects: list[Effect]) -> Tile:
        return Tile(tile_type, spawn_position) #, on_traverse_effects)

    def _trigger_spawn_event(self) -> None:
        ...

    def spawn_object(self, position_selector: PositionSelector, tile_type: TileType, world: World) -> None: #, on_traverse_effects: list[Effect]) -> None:
        position = position_selector.select()
        if position is None:
            return
        tile = self.create_object(position, tile_type)
        tile.on_spawn()
        world.level.tiles.append(tile)

    def spawn_object_at(self, position: WorldVector, tile_type: TileType, world: World) -> None: #, on_traverse_effects: list[Effect]) -> None:
        tile = self.create_object(position, tile_type)
        world.level.tiles.append(tile)

## Numbers

class Number[T: (int, float)](Protocol): # Value? FutureValue? DeferredValue?
    def evaluate(self, world: World) -> T: ... # Context!?


class ExactValue[T]:
    def __init__(self, value: T) -> None:
        self._value: T = value
    def resolve(self, _) -> T:
        return self._value
    def evaluate(self, arg) -> T: # Target and Number could just be one generic?
        return self.resolve(arg)
    
class RandomNumber:
    def __init__(self, from_number: int, to_number: int):
        self._between = (from_number, to_number)
    def evaluate(self, _) -> int:
        return randint(*self._between)


class PlayerRunSpeed:
    def __init__(self, player: Target[Player]) -> None:
        self._player = player
    
    def evaluate(self, world: World) -> float:
        player = self._player.resolve(world)
        # Handle debuffs etc. here or inside player??
        return player.speed

## Targets

class Target[T](Protocol): #Sort of the same as number?
    def resolve(self, world: World) -> T: ...

class CasterPlayerTarget:
    @staticmethod
    def resolve(world: World) -> Player:
        return world.player

class CasterPositionTarget: # Just do casterplayertarget and take position attribute instead?
    def resolve(self, world: World) -> WorldVector:
        return world.player.position

# class CasterFacingDirectionTarget:
#     def resolve(self, world: World) -> WorldVector:
#         pass

class ElementOrbTarget: # Orb in i world? 
    def __init__(self, position: WorldVector):
        self._position = position

    def resolve(self, world: World) -> ElementOrb:
        orbs = AllOrbs().resolve(world)
        return next(orb for orb in orbs if orb.position == self._position)
    
class ElementOrbPositionTarget: # Orb in i world?
    def __init__(self, orb: ElementOrbTarget):
        self._orb = orb

    def resolve(self, world: World) -> WorldVector:
        orb = self._orb.resolve(world)
        return orb.position
    
class TileTarget: # Alla objekt in i world? Känns som world blir allt?
    def __init__(self, position: WorldVector):
        self._position = position

    def resolve(self, world: World) -> Tile:
        tiles = AllTiles().resolve(world)
        return next(tile for tile in tiles if tile.position == self._position)

class LevelTarget: # Whaaat? Ett steg för långt?
    def resolve(self, world: World) -> Level:
        return world.level
    
class MoveDestinationTarget:
    def __init__(self, origin: Target[WorldVector], direction: WorldVector, duration: timedelta, speed: Number[float]) -> None:
        self._origin = origin
        self._direction = direction
        self._duration = duration
        self._speed = speed
        
    def resolve(self, world: World) -> WorldVector:
        origin = self._origin.resolve(world)
        magnitude = math.hypot(self._direction.x, self._direction.y)
        distance = self._speed.evaluate(world) * self._duration.total_seconds()
        
        if not distance or not magnitude:
            return origin

        return WorldVector(
            origin.x + self._direction.x * distance / magnitude,
            origin.y + self._direction.y * distance / magnitude
        )

#Tickers

class DotTicker(Protocol):
    def is_finished(self) -> bool:
        ...

    def tick(self, delta_time: timedelta):
        ...

class EqualDurationDotTicker():
    def __init__(self, interval: Number[float], ticks: Number[int], world: World):
        self._interval = interval.evaluate(world) ## ??
        self._ticks_left = ticks.evaluate(world) ## ??
        self._timer = 0.0

    def is_finished(self) -> bool:
        return self._ticks_left <= 0
        
    def tick(self, delta_time: timedelta) -> bool: 
        if self.is_finished():
            return False
        
        self._timer += delta_time.total_seconds()
        
        if self._timer >= self._interval:
            self._ticks_left -= 1
            self._timer -= self._interval
            return True

        return False

## Effects

class Effect[T](Protocol):
    def apply(self, world: T) -> None: ...

class EffectWithPlayerTarget[T](Protocol):
    _target: Target[Player]

    def apply(self, world: T) -> None: ...

class NoEffect[T]:
    def apply(self, world: T) -> None:
        pass

class EffectSequence[T]:
    def __init__(self, *effects: Effect[T]) -> None:
        self._effects = effects

    def apply(self, world: T) -> None:
        for effect in self._effects:
            effect.apply(world)

class DotEffect: # Target? # En dot effect?
    def __init__(self, effect: EffectWithPlayerTarget, ticker: DotTicker): # Separera Dot och Active?
        self._effect = effect
        self._tick = ticker

    @property
    def effect(self) -> Effect:
        return self._effect

    def apply(self, world: World) -> None:
        self._effect.apply(world)

    def update(self, delta_time: timedelta, world: World) -> None:
        if self._tick.tick(delta_time):
            self.apply(world)
        
        if self._tick.is_finished():
            target = self._effect._target.resolve(world)
            target.remove_dot_effect(self)

class ProjectileEffect:
    def __init__(self,
                 element: Element,
                 origin: Target[WorldVector],
                 direction: Target[WorldVector],
                 velocity: Number[float],
                 damage: Number[int]
                 ) -> None:
        self._element = element
        self._origin = origin # needs injection really?
        self._direction = direction
        self._velocity = velocity
        self._damage = damage # Effect?
    
    def apply(self, world: World) -> None:
        world.projectiles.append(
            Projectile(
                position=self._origin.resolve(world),
                direction=self._direction.resolve(world),
                velocity=self._velocity.evaluate(world),
                effect=NoEffect(),
            )
        )

class HealEffect:
    def __init__(self, target: Target[Player], amount: Number[int]) -> None:
        self._target = target
        self._amount = amount
    
    def apply(self, world: World) -> None:
        target = self._target.resolve(world)
        heal_amount = self._amount.evaluate(world)
        target.heal(heal_amount)

class SlowedEffect:
    def __init__(self, target: Target[Player]) -> None:
        self._target = target
        
    def apply(self, world: World) -> None:
        pass

class RootedEffect:
    def __init__(self, target: Target[Player]) -> None:
        self._target = target
        
    def apply(self, world: World) -> None:
        pass

class DisplaceEffect[T: MovableEntity]: # Generic for walls, orbs and projectiles?
    def __init__(self, target: Target[T], destination: Target[WorldVector]) -> None:
        self._target = target
        self._destination = destination
        # Speed Number[float]?

    def apply(self, world: World) -> None:
        target = self._target.resolve(world)
        destination = self._destination.resolve(world)

        target.move_entity(destination)

class CollectOrbOnGroundEffect: # Collect andra saker än Orb?
    def __init__(self, target: Target[OrbCollector], orb: Target[Optional[ElementOrb]]):
        self._target = target
        self._orb = orb

    def apply(self, world: World) -> None:
        target = self._target.resolve(world)
        
        if orb := self._orb.resolve(world):
            world.level.remove_orb(orb)
            target.collect_orb(orb.element)
            target.call_event(events.OrbPickup()) # World events?

class DestroyOrbEffect():
    def __init__(self, target: Target[OrbHolder], orb: Target[Optional[ElementOrb]]):
        self._orb = orb
        self._target = target
    
    def apply(self, world: World) -> None:
        target = self._target.resolve(world)

        if orb := self._orb.resolve(world):
            target.remove_orb(orb)


# Conditions

class Condition[T](Protocol):
    def check(self, arg: T) -> bool: 
        ...

class Cost(Condition[Player], Effect[Player], Protocol): #Any cleaner way?
    def check(self, player: Player) -> bool:
        ...

    def apply(self, player: Player) -> None:
        ...

class NoCost:
    @staticmethod
    def check(_) -> bool: return True
    @staticmethod
    def apply(_) -> None: pass

class ElementCost:
    def __init__(self, *elements: Element) -> None:
        self.elements = elements

    def check(self, player: Player) -> bool:
        player_elements = Counter(player.elements)
        cost_elements = Counter(self.elements)
        return player_elements >= cost_elements

    def apply(self, player: Player) -> None:
        pass

class HealthCost:
    def __init__(self, amount: Number[int]) -> None:
        self._amount = amount

    def check(self, player: Player) -> bool:
        return True

    def apply(self, world: World) -> None:
        health_cost = self._amount.evaluate(world)
        world.player.heal(health_cost)

class CombinedCost:
    def __init__(self, *costs: Cost) -> None:
        self._costs = costs
    def check(self, player: Player) -> bool:
        return all(cost.check(player) for cost in self._costs)
    def apply(self, player: Player) -> None:
        for cost in self._costs:
            cost.apply(player)

class For[T]:
    def __init__(self, target: Target[Player], condition: Condition[Player]):
        self._target = target
        self._condition = condition

    def check(self, arg: T) -> bool:
        target = self._target.resolve(arg)
        return self._condition.check(target)

class IsMovableCondition:
    def __init__(self, target: Target[MovableEntity]):
        self._target = target

    def check(self, world: World) -> bool:
        entity = self._target.resolve(world)
        return entity.movable

## Conditionals

class EffectConditional[T]:
    def __init__(self, condition: Condition[T], on_pass: Effect[T], on_fail: Effect[T]) -> None:
        self._condition = condition
        self._on_pass = on_pass
        self._on_fail = on_fail
        
    def apply(self, world: T) -> None:
        if self._condition.check(world):
            self._on_pass.apply(world)
        else:
            self._on_fail.apply(world)

class AndConditional[T]:
    def __init__(self, conditions: list[Condition[T]], on_pass: Effect[T], on_fail: Effect[T]) -> None:
        self._conditions = conditions
        self._on_pass = on_pass
        self._on_fail = on_fail
        
    def apply(self, world: T) -> None:
        if all(condition.check(world) for condition in self._conditions):
            self._on_pass.apply(world)
        else:
            self._on_fail.apply(world)

class OrConditional[T]:
    def __init__(self, conditions: list[Condition[T]], on_pass: Effect[T], on_fail: Effect[T]) -> None:
        self._conditions = conditions
        self._on_pass = on_pass
        self._on_fail = on_fail
        
    def apply(self, world: T) -> None:
        if any(condition.check(world) for condition in self._conditions):
            self._on_pass.apply(world)
        else:
            self._on_fail.apply(world)

# Might just as well go all the way in generics?
# class Query[T, S](Protocol):
#     def evaluate(self, input_: T) -> S: ...
# class Command[T](Protocol):
#     def apply(self, input_: T) -> None: ...
#     #__call__?

class Spell:
    def __init__(self, name: str, effect: Effect[World]):
        self._name = name
        self._effect = effect
        #cost?
        #precondition?

    def apply(self, world: World) -> None: # Just call apply and implement effect interface?...
        self._effect.apply(world)




class HasPosition(Protocol):
    position: WorldVector

class Touching[T: HasPosition]:
    def __init__(self, target: Target[WorldVector], colliders: Target[Sequence[T]]) -> None:
        self._target = target
        self._colliders = colliders
    
    def resolve(self, world: World) -> Optional[T]:
        target = self._target.resolve(world)
        colliders = self._colliders.resolve(world)
        return next(
            (
                collider for collider in colliders
                if math.dist(collider.position[:2], target[:2]) < 1
            ),
            None
        )

# Samma som touching mer eller mindre? 
# class Traversing[T: HasPosition]:
#     def __init__(self, target: Target[WorldVector], traversables: Target[Sequence[T]]):
#         self._target = target
#         self._traversables = traversables

#     def resolve(self, world: World) -> Optional[T]:
#         target = self._target.resolve(world)
#         traversables = self._traversables.resolve(world)
        
#         traversed = [
#             traversable for traversable in traversables
#             if math.dist((traversable.position.x, traversable.position.y), (target.x, target.y)) < 1
#         ]
#         return traversed

# def traverse_something(direction, duration, PlayerRunSpeed):
#     Conditional(

#     )
#     destination = MoveDestinationTarget(
#         origin=CasterPositionTarget(),
#         direction=direction,
#         duration=duration,
#         speed=PlayerRunSpeed(
#             CasterPlayerTarget()
#         )
#     )
#     return Conditional(AnyResult(
#             Traversing(
#                 destination,
#                 AllTiles
#             )),
#             on_pass=EffectSequence(
                
#             )
#         )

class AnyResult[T]:
    def __init__(self, result: Target[Optional[T]]) -> None:
        self._result = result
    def check(self, world: World) -> bool:
        return bool(self._result.resolve(world))


class ForEach[T]:
    def __init__(self, effect: Effect[T], targets: Target[Sequence[T]]):
        self._effect = effect
        self._targets = targets

    def apply(self, world: World) -> None:
        for target in self._targets.resolve(world):
            self._effect.apply(target)



# Could they all be functions?
# class InputHandler[T](Protocol):
#     def resolve(self, user_input: UserInput) -> T: ...
# #ih = Callable[T][[UserInput], T]
# 
# class InputDirection:
#     def resolve(self, user_input: UserInput) -> WorldVector: ...
# 
# class IsStartButtonClicked:
#     def resolve(self, user_input: UserInput) -> bool: ...

# direction + duration can be created from input
def create_run_command(direction: WorldVector, duration: timedelta) -> Effect[World]:
    destination = MoveDestinationTarget(
        origin=CasterPositionTarget(),
        direction=direction,
        duration=duration,
        speed=PlayerRunSpeed(
            CasterPlayerTarget()
        )
    )
    return EffectConditional(
        condition=AnyResult(
            Touching(
                target=destination,
                colliders=AllWalls()
            )
        ),
        on_pass=NoEffect(),
        on_fail=EffectConditional(
            condition=IsMovableCondition(
                target=CasterPlayerTarget()
            ),
            on_pass=
                EffectSequence(
                    DisplaceEffect(
                        target=CasterPlayerTarget(),
                        destination=destination
                    ),
                    CollectOrbOnGroundEffect( # Ska Collect orb hantera touching såsom nedan?
                        target=CasterPlayerTarget(),
                        orb=Touching(
                            CasterPositionTarget(),
                            AllOrbs()
                        )
                    )
                ),
            on_fail=NoEffect()
            )
    )

def move_orb_command(orb_position: WorldVector, direction: WorldVector, duration: timedelta) -> Effect[World]:
    orb_target = ElementOrbTarget(orb_position)
    destination_target = MoveDestinationTarget(
                    origin=ElementOrbPositionTarget(orb_target),
                    direction=direction,
                    duration=timedelta(seconds=1),
                    speed=ExactValue(5.0)
                )
    return EffectConditional(
        AnyResult(orb_target),
        on_pass=
            EffectConditional(
                IsMovableCondition(orb_target), 
                on_pass=
                    DisplaceEffect(orb_target, destination_target),
                on_fail=
                    NoEffect()
            ),
        on_fail=NoEffect()  
    )

#
# # Effects inside domain and "Systems" outside? Take world vs userinput respectively? Systems return effects?
# class RunEffect: #System
#     def __init__(self):
#         self._direction = InputDirection()
#         self._duration = FrameDuration()
#
#     def update(self, user_input: UserInput) -> Effect[World]:
#         return create_run_command(
#             self._direction.resolve(user_input),
#             self._duration.resolve(user_input)
#         )
#
# def run_system(
#         input_direction: Callable[[UserInput], WorldVector],
#         frame_duration:  Callable[[UserInput], timedelta]
#         ) -> Callable[[UserInput], Effect[World]]:
#     def inner(user_input: UserInput) -> Effect[World]:
#         return create_run_command(
#             input_direction(user_input),
#             frame_duration(user_input)
#         )
#     return inner
#
# run_system(
#     ...,
#     lambda u: u.delta_time
# )
#
# def make_move_system() -> Callable[[UserInput], Effect[World]]:
#     move_direction: Callable[[UserInput], WorldVector] = lambda i: WorldVector(i.right - i.left, i.down - i.up)
#     frame_duration: Callable[[UserInput], timedelta] = lambda i: i.delta_time
#     return lambda i: create_run_command(move_direction(i), frame_duration(i))



# class SpawnOrb: # Better as function...
#     def __init__(self, position_selector: Callable[[World], WorldVector], element_selector: Callable[[World], Element]) -> None:
#         self._position_selector = position_selector
#         self._element_selector = element_selector
#
#     def apply(self, world: World) -> None:
#         position = self._position_selector(world)
#         element = self._element_selector(world)
#         world.level.spawn_orb(1.0)


# def make_orb_system() -> Callable[[UserInput], Effect[World]]: #orb_timer: Callable[[UserInput], bool]
#     orb_timer = repeatable_timer(10.0)
#     def orb_system(user_input: UserInput) -> Effect[World]:
#         #nonlocal orb_timer
#         if not orb_timer(user_input.delta_time):
#             return NoEffect()
#         return SpawnOrb(
#             position_selector=lambda _: WorldVector(random.randint(1,10), random.randint(1,10)),
#             element_selector=lambda _: random.choice(list(Element))
#         )
#     return orb_system


class RelativeDirection:
    def __init__(self, position_a: Target[WorldVector], position_b: Target[WorldVector]) -> None:
        self._position_a = position_a
        self._position_b = position_b
    def resolve(self, world: World) -> WorldVector:
        x_a, y_a = self._position_a.resolve(world)
        x_b, y_b = self._position_b.resolve(world)
        return WorldVector(x_a-x_b, y_a-y_b)


def create_fireball_spell(target: WorldVector) -> Spell:
    return Spell(
        name="Fire Ball",
        effect=ProjectileEffect(
            element=Element.FIRE,
            origin=CasterPositionTarget(),
            direction=RelativeDirection(
                ExactValue(target),
                CasterPositionTarget(),
            ),
            velocity=ExactValue(5.0),
            damage=ExactValue(10)
        )
    )


def create_heal_spell(_) -> Spell:
    return Spell(
        name="Heal",
        effect=HealEffect(
            target=CasterPlayerTarget(),
            amount=RandomNumber(3,10)
        )
    )


# def create_push_spell() -> Spell:
#     pass

#
# spell_map: dict[Cost, Spell] = { # Order important? Make list of tuples?
#     ElementCost(Element.FIRE, Element.FIRE,  Element.WIND): create_fireball_spell(),
#     ElementCost(Element.WIND, Element.WATER, Element.WATER): create_heal_spell(),
# }
#
#
# # SpellFactory
# def conjure_spell(world: World) -> Effect[World]:# Optional[Spell]:
#     for cost, spell in spell_map.items():
#         if not cost.check(world.player): continue
#         # Potentially check other preconditions?
#         cost.apply(world.player)
#         return spell
#     else:
#         return NoEffect() #None # NoSpell?
#
#
# class ConjureSpell:
#     #def __init__(self, user_input: UserInput) -> None:
#     def apply(self, world: World) -> None:  # Optional[Spell]:
#         for cost, spell in spell_map.items():
#             if not cost.check(world.player): continue
#             # Potentially check other preconditions?
#             cost.apply(world.player)
#             spell.apply(world)
#             return
#
#
# def make_spell_system() -> Callable[[UserInput], Effect[World]]:
#     cast_spell_input: Callable[[UserInput], bool] = lambda i: i.space
#     def spell_system(user_input: UserInput) -> Effect[World]:
#         if not cast_spell_input(user_input):
#             return NoEffect()
#         return ConjureSpell()
#     return spell_system


spell_list: list[tuple[Cost, Callable[[WorldVector], Spell]]] = [ # prio from top to bottom
    (ElementCost(Element.FIRE, Element.FIRE,  Element.WIND), create_fireball_spell), # fireball factory
    (ElementCost(Element.WIND, Element.WATER, Element.WATER), create_heal_spell)
]

