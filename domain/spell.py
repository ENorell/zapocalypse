import math
from collections import Counter
from datetime import timedelta
from typing import Protocol, Sequence, Optional
from dataclasses import dataclass
from random import randint

from domain.model import Element, Player, Level, WorldVector, ElementOrb, Wall
import domain.events as events

@dataclass(frozen=True)
class Context:
    caster: Player
    level: Level
    players: list[Player]



class Effect[T](Protocol): #T to handle any type?
    def apply(self, context: T) -> None: ...


class EffectSequence[T]:
    def __init__(self, *effects: Effect[T]) -> None:
        self._effects = effects

    def apply(self, context: T) -> None:
        for effect in self._effects:
            effect.apply(context)


class Spell:
    def __init__(self, name: str, effect: Effect[Context]):
        self._name = name
        self._effect = effect
        #cost

    def cast(self, context: Context) -> None: # Just call apply and implement effect interface?...
        self._effect.apply(context)


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
        pass

a: Target[Player] = CasterPlayerTarget()

class Number[T: (int, float)](Protocol):
    def evaluate(self) -> T: ... # Context!?

class ExactNumber[T: (int, float)]:
    def __init__(self, value: T) -> None:
        self._value: T = value

    def evaluate(self, _) -> T:
        return self._value

b: Number[float] = ExactNumber(10)

class RandomNumber:
    def __init__(self, from_number: int, to_number: int):
        self._between = (from_number, to_number)

    def evaluate(self, _) -> int:
        return randint(*self._between)


class Condition[T](Protocol):
    def check(self, arg: T) -> bool: ...

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
    ...

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
        player.damage(health_cost)


class For[T]:
    def __init__(self, target: Target[Player], condition: Condition[Player]):#t: T, s: S) -> None:
        self._target = target
        self._condition = condition

    def check(self, arg: T) -> bool:
        target = self._target.resolve(arg)
        return self._condition.check(target)


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
    def __init__(self, target: Target[Player], amount: Number[int]) -> None:
        self._target = target
        self._amount = amount
    
    def apply(self, context: Context) -> None:
        target = self._target.resolve(context)
        heal_amount = self._amount.evaluate()
        target.heal(heal_amount)
        


class PickupOrbEffect:
    def __init__(self, element: Element):
        pass

    def apply(self, context: Context) -> None:
        pass

class DisplaceEffect: # Generic for walls, orbs and projectiles?
    def __init__(self, player: Target[Player], destination: Target[WorldVector]) -> None:
        self._player = player
        self._destination = destination
        # Speed Number[float]?

    def apply(self, context: Context) -> None:
        player = self._player.resolve(context)
        destination = self._destination.resolve(context)

        if context.level.collides_with_wall(destination): # Extract into Conditional?
            player.events.append(events.Collision())
            return
        
        if orb := context.level.get_touching_orb(destination): # Extract into Sequence?
            context.level.remove_orb(orb)
            player.give_element(orb.element)
            player.events.append(events.OrbPickup())

        player.position = destination


class RunDestinationTarget:
    def __init__(self, origin: Target[WorldVector], direction: WorldVector, duration: timedelta, speed: Number[float]) -> None:
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


class PlayerRunSpeed:
    def __init__(self, player: Target[Player]) -> None:
        self._player = player
    
    def evaluate(self, context: Context) -> float:
        player = self._player.resolve(context)
        # Handle debuffs etc. here or inside player??
        return player.get_speed()



class RootedEffect:
    def __init__(self,
                 target: Target[Player],
                 ) -> None:
        self._target = target
        
    def apply(self, context: Context) -> None:
        pass


class NoEffect[T]:
    def apply(self, context: T) -> None:
        pass

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


# class Collide[T]:
#     def __init__(self, player: Target[Player], collider: Target[T]): # TargetS
#         self._player = player # Also generic?
#         self._collider = collider
#         # Different collision detection approaches?
#     
#     def check(self, context: Context) -> bool:
#         player = self._player.resolve(context)
#         collider = self._collider.resolve(context)
        

class Collector(Protocol):
    def give_object(self, object: HasPosition)

class PickupOrb(T: OrbCollector):
    def __init__(self, player: Target[T], orb: Target[Optional[ElementOrb]]):
        self._player = player
        self._orb = orb
    
    def apply(self, context: Context) -> None:
        player = self._player.resolve(context)
        
        if orb := self._orb.resolve(context):
            context.level.remove_orb(orb)
            player.give_element(orb.element)
            player.events.append(events.OrbPickup())

class HasPosition(Protocol):
    position: WorldVector

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

class AllOrbs:
    def resolve(self, context: Context) -> list[ElementOrb]:
        return context.level.orbs
class AllWalls:
    def resolve(self, context: Context) -> list[Wall]:
        return context.level.walls
class AnyResult[T]:
    def __init__(self, result: Target[Optional[T]]) -> None:
        self._result = result
    def check(self, context: Context) -> bool:
        return bool(self._result.resolve(context))

def create_run_command(direction: WorldVector, duration: timedelta) -> Effect[Context]:
    destination = RunDestinationTarget(
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
        on_fail=EffectSequence(
            DisplaceEffect(
                player=CasterPlayerTarget(),
                destination=destination
            ),
            PickupOrb(
                player=CasterPlayerTarget(),
                orb=Touching(
                    CasterPositionTarget(),
                    AllOrbs()
                )
            )
        )
    )




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

def create_push_spell() -> Spell:
    pass


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

