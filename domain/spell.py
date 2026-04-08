from __future__ import annotations
import math
from collections import Counter
from datetime import timedelta
from typing import Protocol, Sequence, Optional
from enum import Enum, auto
from dataclasses import dataclass
from random import randint
from collections import deque

from domain.model import Level, WorldVector, HasPosition, Element, ElementOrb, Wall, Tile #Player, MovableEntity, OrbCollector, OrbHolder
import domain.events as events



class MovableEntity(Protocol):
    movable: bool

    def move_entity(self, destination: WorldVector) -> None:
        ...

class MoveType(Enum):
    DEFAULT = auto()
    FLY = auto()
    SWIM = auto()

class OrbCollector(Protocol):
    def collect_orb(self, element: Element):
        ...

    def call_event(self, element: events.Event):
        ...

class OrbHolder(Protocol):
    def remove_orb(self, orb: ElementOrb):
        ...

class Player:
    base_speed = 8.0
    max_no_elements = 3
    max_health = 100
    def __init__(self, position: WorldVector, elements: Optional[list[Element]]) -> None:
        #health
        self.position = position
        self._elements = deque(elements or [], self.max_no_elements)
        self.events: list[events.Event] = []
        self.movable = True
        self._move_types: list[MoveType] = []
        self._speed_buffs: list[int] = []
        self._health = self.max_health
        self._speed = self.base_speed
        self._active_effects: list[DotEffect] = []

    @property
    def elements(self) -> list[Element]:
        return list(self._elements)

    @property
    def move_types(self) -> list[MoveType]:
        return list(self._move_types)
    
    @property
    def health(self) -> int:
        return self._health
    
    @property
    def speed(self) -> float:
        return self._speed
    
    def add_dot_effect(self, effect: DotEffect) -> None:
        # for active_effect in self._active_effects:
        #     if active_effect.effect == effect:
        #         active_effect._remaining_ticks # Ändringar i Tick gör att denna kanske blir mer komplicerad?
        self._active_effects.append(effect)

    def remove_dot_effect(self, effect: DotEffect) -> None:
        if effect in self._active_effects:
            self._active_effects.remove(effect)

    def apply_speed_change(self, delta_speed: float) -> None:
        self._speed = max(self._speed + delta_speed, 0)
    
    def get_base_speed(self) -> float:
        """Return speed after effects etc."""
        return self.base_speed

    def take_damage(self, damage_number: int):
        self._health = max(self._health - damage_number, 0)

    def heal(self, heal_number: int):
        self._health = min(self._health + heal_number, self.max_health)

    def collect_orb(self, element: Element) -> None:
        self._elements.appendleft(element)

    def apply_move_type(self, move_type: MoveType) -> None:
        self._move_types.append(move_type)

    def move_entity(self, destination: WorldVector) -> None:
        self.position = destination

    def call_event(self, event: events.Event):
        self.events.append(event)

@dataclass(frozen=True)
class Context:
    caster: Player
    level: Level
    players: list[Player]

## Targets

class Target[T](Protocol):
    def resolve(self, context: Context) -> T: ...

class CasterPlayerTarget:
    def resolve(self, context: Context) -> Player:
        return context.caster

class CasterPositionTarget:
    def resolve(self, context: Context) -> WorldVector:
        return context.caster.position

class CasterFacingDirectionTarget:
    def resolve(self, context: Context) -> WorldVector:
        return # TODO?

# class CircleAreaOfEffectTarget:
#     def __init__(self, position_center: Target[WorldVector], radius: float):
#         self._position_center = position_center
#         self._radius = radius

#     def resolve(self, context: Context) -> list[WorldVector]:
#         center = self._position_center.resolve(context)
#         area_of_effect = []

# class RectangleAreaOfEffectTarget:
#     def __init__(self, position_center: Target[WorldVector], width: float, height: float):
#         self._position_center = position_center
#         self.width = width
#         self.height = height

#     def resolve(self, context: Context) -> list[WorldVector]:
#         center = self._position_center.resolve(context)
#         area_of_effect = []
        
class ElementOrbTarget: # Orb in i context? 
    def __init__(self, position: WorldVector):
        self._position = position

    def resolve(self, context: Context) -> ElementOrb:
        orbs = AllOrbs().resolve(context)
        return next(orb for orb in orbs if orb.position == self._position)
    
class ElementOrbPositionTarget: # Orb in i context?
    def __init__(self, orb: ElementOrbTarget):
        self._orb = orb

    def resolve(self, context: Context) -> WorldVector:
        orb = self._orb.resolve(context)
        return orb.position
    
class TileTarget: # Alla objekt in i context? Känns som context blir allt?
    def __init__(self, position: WorldVector):
        self._position = position

    def resolve(self, context: Context) -> Tile:
        tiles = AllTiles().resolve(context)
        return next(tile for tile in tiles if tile.position == self._position)

class LevelTarget:
    def resolve(self, context: Context) -> Level:
        return context.level

## Numbers

class Number[T: (int, float)](Protocol):
    def evaluate(self, context: Optional[Context] = None) -> T: ... # Context!? Optional!? 
    # TH: Context måste finnas om vissa nummer ska vara nummer men ändå kunna manipuleras beroende av context?

class ExactNumber[T: (int, float)]:
    def __init__(self, value: T) -> None:
        self._value: T = value

    def evaluate(self, context: Optional[Context] = None) -> T:
        return self._value

b: Number[float] = ExactNumber(10)

class RandomNumber:
    def __init__(self, from_number: int, to_number: int):
        self._between = (from_number, to_number)

    def evaluate(self, context: Optional[Context] = None) -> int:
        return randint(*self._between)
    
class PlayerRunSpeed:
    def __init__(self, player: Target[Player]) -> None:
        self._player = player
    
    def evaluate(self, context: Optional[Context] = None) -> float:
        player = self._player.resolve(context)
        exact_number = ExactNumber(player.speed).evaluate(context)
        # Handle debuffs etc. here or inside player??
        return exact_number # ??

class MoveDestinationTarget:
    def __init__(self, origin: Target[WorldVector], direction: WorldVector, duration: timedelta, speed: Number) -> None:
        self._origin = origin
        self._direction = direction
        self._duration = duration
        self._speed = speed
        
    def resolve(self, context: Context) -> WorldVector:
        origin = self._origin.resolve(context)
        magnitude = math.hypot(self._direction.x, self._direction.y)
        distance = self._speed.evaluate(context) * self._duration.total_seconds()
        
        if not distance or not magnitude:
            return origin

        return WorldVector(
            origin.x + self._direction.x * distance / magnitude,
            origin.y + self._direction.y * distance / magnitude
        )
    
class Touching[T: HasPosition]:
    def __init__(self, target: Target[WorldVector], colliders: Target[Sequence[T]]) -> None:
        self._target = target
        self._colliders = colliders
    
    def resolve(self, context: Context) -> Optional[T]:
        target = self._target.resolve(context)
        colliders = self._colliders.resolve(context)
        return next(
            (
                collider for collider in colliders
                if math.dist(
                    (collider.position.x, collider.position.y), 
                    (target.x, target.y)
                ) < 1
            ),
            None
        )
    
class Traversing[T: HasPosition]:
    def __init__(self, target: Target[WorldVector], traversables: Target[Sequence[T]]):
        self._target = target
        self._traversables = traversables

    def resolve(self, context: Context) -> Optional[T]:
        target = self._target.resolve(context)
        traversables = self._traversables.resolve(context)
        
        traversed = [
            traversable for traversable in traversables
            if math.dist((traversable.position.x, traversable.position.y), (target.x, target.y)) < 1
        ]
        return traversed
    
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
    
class AllOrbs:
    def resolve(self, context: Context) -> list[ElementOrb]:
        return context.level.orbs
class AllWalls:
    def resolve(self, context: Context) -> list[Wall]:
        return context.level.walls
class AllTiles:
    def resolve(self, context: Context) -> list[Tile]:
        return context.level.tiles

#Tickers

class DotTicker(Protocol):
    def is_finished(self) -> bool:
        ...

    def tick(self, delta_time: timedelta):
        ...

class EqualDurationDotTicker():
    def __init__(self, interval: Number[float], ticks: Number[int]):
        self._interval = interval.evaluate() ## ??
        self._ticks_left = ticks.evaluate() ## ??
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

class Effect[T](Protocol): #T to handle any type?
    def apply(self, context: T) -> None: ...

class EffectWithPlayerTarget[T](Protocol):
    _target: Target[Player]

    def apply(self, context: Context) -> None: ...

class DotEffect: # Target? # En dot effect?
    def __init__(self, effect: EffectWithPlayerTarget, ticker: DotTicker): # Separera Dot och Active?
        self._effect = effect
        self._tick = ticker

    @property
    def effect(self) -> Effect:
        return self._effect

    def apply(self, context: Context) -> None:
        self._effect.apply(context)

    def update(self, delta_time: timedelta, context: Context) -> None:
        if self._tick.tick(delta_time):
            self.apply(context)
        
        if self._tick.is_finished():
            target = self._effect._target.resolve(context)
            target.remove_dot_effect(self)
        
        
class EffectSequence[T]:
    def __init__(self, *effects: Effect[T]) -> None:
        self._effects = effects

    def apply(self, context: T) -> None:
        for effect in self._effects:
            effect.apply(context)

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
        self._damage = damage
    
    def apply(self, context: Context) -> None:
        pass

class HealEffect:
    def __init__(self, target: Target[Player], amount: Number[int]) -> None: # Hur hantera target aoe?
        self._target = target
        self._amount = amount
    
    def apply(self, context: Context) -> None:
        target = self._target.resolve(context)
        heal_amount = self._amount.evaluate()
        target.heal(heal_amount)

# class SpeedEffect:
#     def __init__(self, target: Target[Player], amount: Number[int]) -> None: # Hur hantera target aoe?
#         self._target = target
#         self._amount = amount
    
#     def apply(self, context: Context) -> None:
#         target = self._target.resolve(context)
#         speed_amount = self._amount.evaluate()
#         target.apply_speed_debuff
        
class DisplaceEffect[T: MovableEntity]: # Generic for walls, orbs and projectiles?
    def __init__(self, target: Target[T], destination: Target[WorldVector]) -> None:
        self._target = target
        self._destination = destination
        # Speed Number[float]?

    def apply(self, context: Context) -> None:
        target = self._target.resolve(context)
        destination = self._destination.resolve(context)

        target.move_entity(destination)

# class TraversingEffect:
#     def __init__(self, target: Target[Player], traversing: Target[Tile]):
#         self._target = target
#         self._traversing = traversing

#     def apply(self, context: Context) -> None:
#         target = self._target.resolve(context)
#         traversing = self._traversing.resolve(context)
#         effects = traversing.on_traverse_effects
#         for effect in effects:
#             effect.apply(context)

class SlowedEffect:
    def __init__(self,
                 target: Target[Player],
                 ) -> None:
        self._target = target
        
    def apply(self, context: Context) -> None:
        pass

class RootedEffect:
    def __init__(self,
                 target: Target[Player],
                 ) -> None:
        self._target = target
        
    def apply(self, context: Context) -> None:
        pass

class CollectOrbOnGroundEffect: # Collect andra saker än Orb?
    def __init__(self, target: Target[OrbCollector], orb: Target[Optional[ElementOrb]]):
        self._target = target
        self._orb = orb

    def apply(self, context: Context) -> None:
        target = self._target.resolve(context)
        
        if orb := self._orb.resolve(context):
            context.level.remove_orb(orb)
            target.collect_orb(orb.element)
            target.call_event(events.OrbPickup())

class DestroyOrbEffect():
    def __init__(self, target: Target[OrbHolder], orb: Target[Optional[ElementOrb]]):
        self._orb = orb
        self._target = target
    
    def apply(self, context: Context) -> None:
        target = self._target.resolve(context)

        if orb := self._orb.resolve(context):
            target.remove_orb(orb)

class NoEffect[T]:
    def apply(self, context: T) -> None:
        pass

## Conditions

class Condition[T](Protocol):
    def check(self, arg: T) -> bool: ...

class AnyResult[T]:
    def __init__(self, result: Target[Optional[T]]) -> None:
        self._result = result
    def check(self, context: Context) -> bool:
        return bool(self._result.resolve(context))

class IsMovableCondition:
    def __init__(self, target: Target[MovableEntity]):
        self._target = target

    def check(self, context: Context) -> bool:
        entity = self._target.resolve(context)
        return entity.movable

class For[T]:
    def __init__(self, target: Target[Player], condition: Condition[Player]):#t: T, s: S) -> None:
        self._target = target
        self._condition = condition

    def check(self, arg: T) -> bool:
        target = self._target.resolve(arg)
        return self._condition.check(target)
    
# class Collide[T]:
#     def __init__(self, player: Target[Player], collider: Target[T]): # TargetS
#         self._player = player # Also generic?
#         self._collider = collider
#         # Different collision detection approaches?
#     
#     def check(self, context: Context) -> bool:
#         player = self._player.resolve(context)
#         collider = self._collider.resolve(context)

## Conditionals

class Conditional[T]:
    def __init__(self, condition: Condition[T], on_pass: Effect[T], on_fail: Effect[T]) -> None:
        self._condition = condition
        self._on_pass = on_pass
        self._on_fail = on_fail
        
    def apply(self, context: T) -> None:
        if self._condition.check(context):
            self._on_pass.apply(context)
        else:
            self._on_fail.apply(context)

class AndConditional[T]:
    def __init__(self, conditions: list[Condition[T]], on_pass: Effect[T], on_fail: Effect[T]) -> None:
        self._conditions = conditions
        self._on_pass = on_pass
        self._on_fail = on_fail
        
    def apply(self, context: T) -> None:
        if all(condition.check(context) for condition in self._conditions):
            self._on_pass.apply(context)
        else:
            self._on_fail.apply(context)

class OrConditional[T]:
    def __init__(self, conditions: list[Condition[T]], on_pass: Effect[T], on_fail: Effect[T]) -> None:
        self._conditions = conditions
        self._on_pass = on_pass
        self._on_fail = on_fail
        
    def apply(self, context: T) -> None:
        if any(condition.check(context) for condition in self._conditions):
            self._on_pass.apply(context)
        else:
            self._on_fail.apply(context)


# class ElementCondition:
#     def __init__(self, elements: list):
#         self._elements = elements
#
#     def check(self, arg: Player) -> bool:
#         return False
#
# has_elements: Condition[Player] = ElementCondition(["fire", "water"])


# class ICost(Protocol): #Condition?
#     def can_afford(self, player: Player) -> bool: ...
#     def pay_cost(self, player: Player) -> bool: ...
#
# class Cost:
#     def __init__(self, charge: Effect[Player], affords: Condition[Player]) -> None:
#         self._charge = charge
#         self._affords = affords
#
#     def affords(self) -> bool:
#         return self._affords.check()

class Cost(Condition[Player], Effect[Player], Protocol): #Any cleaner way?
    def check(self, player: Player) -> bool:
        return

class ElementCost:
    def __init__(self, *elements: Element) -> None:
        self.elements = elements

    def check(self, player: Player) -> bool:
        player_elements = Counter(player.elements)
        cost_elements = Counter(self.elements)
        return player_elements >= cost_elements

    def apply(self, context: Context) -> None:
        pass

class HealthCost:
    def __init__(self, amount: Number[int]) -> None:
        self._amount = amount

    def check(self, _: Player) -> bool:
        return True

    def apply(self, player: Player) -> None:
        health_cost = self._amount.evaluate()
        player.heal(health_cost)



## Spells

class Spell:
    def __init__(self, name: str, effect: Effect[Context]):
        self._name = name
        self._effect = effect
        #cost

    def cast(self, context: Context) -> None: # Just call apply and implement effect interface?...
        self._effect.apply(context)

def create_fireball_spell() -> Spell:
    return Spell(
        name="Fire Ball",
        effect=ProjectileEffect(
            element=Element.FIRE,
            origin=CasterPositionTarget(),
            direction=CasterFacingDirectionTarget(),
            velocity=ExactNumber(5.0),
            damage=ExactNumber(10)
        )
    )

def create_heal_spell() -> Spell:
    return Spell(
        name="Heal",
        effect=HealEffect(
            target=CasterPlayerTarget(),
            amount=RandomNumber(3,10)
        )
    )

# def create_heal_area_of_effect_spell() -> Spell: # Hur hantera aoe effects? Se HealEffect-kommentar
#     return Spell(
#         name="Heal",
#         effect=HealEffect(
#             target=CasterPlayerTarget(),
#             amount=RandomNumber(3,10)
#         )
#     )

# def create_push_orb_spell() -> Spell:
#     return Spell(
#         name="Push Orb",
#         effect=DisplaceEffect(
#         target=,
#         )
#     )

spell_map: dict[Cost, Spell] = {
    ElementCost(Element.FIRE, Element.FIRE, Element.WIND): create_fireball_spell(),
    ElementCost(Element.WIND, Element.WATER, Element.WATER): create_heal_spell(),
}

def conjure_spell(player: Player) -> Optional[Spell]:
    for cost, spell in spell_map.items():
        if not cost.check(player): continue
        # Potentially check other preconditions?
        cost.apply(player)
        return spell
    else:
        return None # NoSpell?

def create_run_command(direction: WorldVector, duration: timedelta) -> Effect[Context]:
    destination = MoveDestinationTarget(
        origin=CasterPositionTarget(),
        direction=direction,
        duration=duration,
        speed=PlayerRunSpeed(
            CasterPlayerTarget()
        )
    )
    return Conditional(
        condition=AnyResult(
            Touching(
                target=destination,
                colliders=AllWalls()
            )
        ),
        on_pass=NoEffect(),
        on_fail=Conditional(
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

def move_orb_command(orb_position: WorldVector, direction: WorldVector, duration: timedelta) -> Effect[Context]:
    orb_target = ElementOrbTarget(orb_position)
    destination_target = MoveDestinationTarget(
                    origin=ElementOrbPositionTarget(orb_target),
                    direction=direction,
                    duration=timedelta(seconds=1),
                    speed=ExactNumber(5.0)
                )
    return Conditional(
        AnyResult(orb_target),
        on_pass=
            Conditional(
                IsMovableCondition(orb_target), 
                on_pass=
                    DisplaceEffect(orb_target, destination_target),
                on_fail=
                    NoEffect()
            ),
        on_fail=NoEffect()  
    )
