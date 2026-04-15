import random

import math
from collections import Counter
from datetime import timedelta
from typing import Protocol, Sequence, Optional, Callable
from dataclasses import dataclass
from random import randint

from domain.model import Element, Player, Level, WorldVector, ElementOrb, Wall
import domain.events as events
from interactors.scene import UserInput


@dataclass(frozen=True)
class World:
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
    def __init__(self, name: str, effect: Effect[World]):
        self._name = name
        self._effect = effect
        #cost

    def apply(self, context: World) -> None: # Just call apply and implement effect interface?...
        self._effect.apply(context)


class Target[T](Protocol): #Sort of the same as number?
    def resolve(self, context: World) -> T: ...

class CasterPlayerTarget:
    def resolve(self, context: World) -> Player:
        return context.caster

class CasterPositionTarget:
    def resolve(self, context: World) -> WorldVector:
        return context.caster.position

class CasterFacingDirectionTarget:
    def resolve(self, context: World) -> WorldVector:
        pass

a: Target[Player] = CasterPlayerTarget()

class Number[T: (int, float)](Protocol): # Value?
    def evaluate(self, context: World) -> T: ... # Context!?

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

    def apply(self, context: World) -> None:
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
    
    def apply(self, context: World) -> None:
        pass


class HealEffect:
    def __init__(self, target: Target[Player], amount: Number[int]) -> None:
        self._target = target
        self._amount = amount
    
    def apply(self, context: World) -> None:
        target = self._target.resolve(context)
        heal_amount = self._amount.evaluate()
        target.heal(heal_amount)


class DisplaceEffect: # Generic for walls, orbs and projectiles?
    def __init__(self, player: Target[Player], destination: Target[WorldVector]) -> None:
        self._player = player
        self._destination = destination
        # Speed Number[float]?

    def apply(self, context: World) -> None:
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
        
    def resolve(self, context: World) -> WorldVector:
        origin = self._origin.resolve(context)
        magnitude = math.hypot(*self._direction)
        distance = self._speed.evaluate(context) * self._duration.total_seconds()
        if not distance or not magnitude:
            return origin

        return WorldVector(
            origin.x + self._direction.x * distance / magnitude,
            origin.y + self._direction.y * distance / magnitude,
            origin.z
        )


class PlayerRunSpeed:
    def __init__(self, player: Target[Player]) -> None:
        self._player = player
    
    def evaluate(self, context: World) -> float:
        player = self._player.resolve(context)
        # Handle debuffs etc. here or inside player??
        return player.get_speed()



class RootedEffect:
    def __init__(self,
                 target: Target[Player],
                 ) -> None:
        self._target = target
        
    def apply(self, context: World) -> None:
        pass


class NoEffect[T]:
    def apply(self, context: T) -> None:
        pass

class EffectConditional[T]:
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
        

class PickupOrb:
    def __init__(self, player: Target[Player], orb: Target[Optional[ElementOrb]]):
        self._player = player
        self._orb = orb
    
    def apply(self, context: World) -> None:
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
    
    def resolve(self, context: World) -> Optional[T]:
        target = self._target.resolve(context)
        colliders = self._colliders.resolve(context)
        return next(
            (
                collider for collider in colliders
                if math.dist(collider.position[:2], target[:2]) < 1
            ),
            None
        )

class AllOrbs:
    def resolve(self, context: World) -> list[ElementOrb]:
        return context.level.orbs
class AllWalls:
    def resolve(self, context: World) -> list[Wall]:
        return context.level.walls
class AnyResult[T]:
    def __init__(self, result: Target[Optional[T]]) -> None:
        self._result = result
    def check(self, context: World) -> bool:
        return bool(self._result.resolve(context))


class ForEach[T]:
    def __init__(self, effect: Effect[T], targets: Target[Sequence[T]]):
        self._effect = effect
        self._targets = targets

    def apply(self, context: World) -> None:
        for target in self._targets.resolve(context):
            self._effect.apply(target)


class AllPlayers:
    def resolve(self, context: World) -> list[Player]:
        return context.players

test: Target[Sequence[Player]] = AllPlayers()
test2: ForEach[Player] = ForEach(NoEffect(), AllPlayers())

# Could they all be functions?
class InputHandler[T](Protocol):
    def resolve(self, user_input: UserInput) -> T: ...
#ih = Callable[T][[UserInput], T]

class InputDirection:
    def resolve(self, user_input: UserInput) -> WorldVector: ...

class IsStartButtonClicked:
    def resolve(self, user_input: UserInput) -> bool: ...

# direction + duration can be created from input
def create_run_command(direction: WorldVector, duration: timedelta) -> Effect[World]:
    destination = RunDestinationTarget(
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


# Effects inside domain and "Systems" outside? Take world vs userinput respectively? Systems return effects?
class RunEffect: #System
    def __init__(self):
        self._direction = InputDirection()
        self._duration = FrameDuration()

    def update(self, user_input: UserInput) -> Effect[World]:
        return create_run_command(
            self._direction.resolve(user_input),
            self._duration.resolve(user_input)
        )

def run_system(
        input_direction: Callable[[UserInput], WorldVector],
        frame_duration:  Callable[[UserInput], timedelta]
        ) -> Callable[[UserInput], Effect[World]]:
    def inner(user_input: UserInput) -> Effect[World]:
        return create_run_command(
            input_direction(user_input),
            frame_duration(user_input)
        )
    return inner

run_system(
    ...,
    lambda u: u.delta_time
)

def make_move_system() -> Callable[[UserInput], Effect[World]]:
    move_direction: Callable[[UserInput], WorldVector] = lambda i: WorldVector(i.right - i.left, i.down - i.up)
    frame_duration: Callable[[UserInput], timedelta] = lambda i: i.delta_time
    return lambda i: create_run_command(move_direction(i), frame_duration(i))



class SpawnOrb: # Better as function...
    def __init__(self, position_selector: Callable[[World], WorldVector], element_selector: Callable[[World], Element]) -> None:
        self._position_selector = position_selector
        self._element_selector = element_selector

    def apply(self, context: World) -> None:
        position = self._position_selector(context)
        element = self._element_selector(context)
        context.level.spawn_orb(1.0)


def repeatable_timer(frequency: float) -> Callable[[timedelta], bool]:
    time_counted = 0.0
    def inner(tick_time: timedelta) -> bool:
        nonlocal time_counted
        time_counted += tick_time.total_seconds()
        if time_counted > frequency:
            time_counted -= frequency
            return True
        return False
    return inner


def make_orb_system() -> Callable[[UserInput], Effect[World]]: #orb_timer: Callable[[UserInput], bool]
    orb_timer = repeatable_timer(10.0)
    def orb_system(user_input: UserInput) -> Effect[World]:
        #nonlocal orb_timer
        if not orb_timer(user_input.delta_time):
            return NoEffect()
        return SpawnOrb(
            position_selector=lambda _: WorldVector(random.randint(1,10), random.randint(1,10)),
            element_selector=lambda _: random.choice(list(Element))
        )
    return orb_system


class SpawnOrbSystem: # Generalize?
    def __init__(self):
        self._spawn_timer: Callable[[timedelta], bool] = repeatable_timer(10.0) # Inject or instantiate?
        self._position_selector = lambda _: WorldVector(random.randint(1, 10), random.randint(1, 10))
        self._element_selector = lambda _: random.choice(list(Element))
        
    def update(self, user_input: UserInput, context: World) -> None:
        if not self._spawn_timer(user_input.delta_time):
            return
        position = self._position_selector(context)
        element = self._element_selector(context)
        context.level.spawn_orb(1.0)
    


# def switch_state_from_start(state_switcher: Callable[[str], None]):
#     def system(user_input: UserInput) -> Effect[Context]:
#         def effect(context: Context) -> None:
#             pass
#         return effect
# 
#     return system



def create_fireball_spell(user_input: UserInput) -> Spell:#Callable[[UserInput], Spell]:
    return Spell(
        name="Fire Ball",
        effect=ProjectileEffect(
            element=Element.FIRE,
            origin=CasterPositionTarget(),
            direction=input_direction(user_input),#CasterFacingDirectionTarget(),
            velocity=ExactNumber(5.0),
            damage=ExactNumber(10)
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


spell_map: dict[Cost, Spell] = { # Order important? Make list of tuples?
    ElementCost(Element.FIRE, Element.FIRE,  Element.WIND): create_fireball_spell(),
    ElementCost(Element.WIND, Element.WATER, Element.WATER): create_heal_spell(),
}


# SpellFactory
def conjure_spell(context: World) -> Effect[World]:# Optional[Spell]:
    for cost, spell in spell_map.items():
        if not cost.check(context.player): continue
        # Potentially check other preconditions?
        cost.apply(context.player)
        return spell
    else:
        return NoEffect() #None # NoSpell?


class ConjureSpell:
    #def __init__(self, user_input: UserInput) -> None:
    def apply(self, context: World) -> None:  # Optional[Spell]:
        for cost, spell in spell_map.items():
            if not cost.check(context.player): continue
            # Potentially check other preconditions?
            cost.apply(context.player)
            spell.apply(context)
            return


def make_spell_system() -> Callable[[UserInput], Effect[World]]:
    cast_spell_input: Callable[[UserInput], bool] = lambda i: i.space
    def spell_system(user_input: UserInput) -> Effect[World]:
        if not cast_spell_input(user_input):
            return NoEffect()
        return ConjureSpell()
    return spell_system


spell_list: list[tuple[Cost, Callable[[UserInput], Spell]]] = [ # prio from top to bottom
    (ElementCost(Element.FIRE, Element.FIRE,  Element.WIND), create_fireball_spell),
    (ElementCost(Element.WIND, Element.WATER, Element.WATER), create_heal_spell)
]

class SpellSystem:
    def __init__(self):
        self._cast_spell_input: Callable[[UserInput], bool] = lambda i: i.space
    
    def update(self, user_input: UserInput, context: World) -> None:
        if not self._cast_spell_input(user_input):
            return
        spell = self._conjure_spell(user_input, context)
        spell.apply(context)

    def _conjure_spell(self, user_input: UserInput, context: World) -> Effect[World]:# Optional[Spell]:
        for cost, spell in spell_list:
            if not cost.check(context.player): continue
            # Potentially check other preconditions?
            cost.apply(context.player)
            return spell(user_input)
        else:
            return NoEffect()


# def make_fight_scene(context: Context) -> Callable[[UserInput], None]:
#     def inner(user_input: UserInput) -> None:
#         run_system(..., lambda u: u.delta_time)(user_input).apply(context)
#         orb_system(user_input).apply(context)
#         spell_system(user_input).apply(context)
#     return inner

