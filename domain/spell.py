import math
from collections import Counter
from datetime import timedelta
from typing import Protocol, Sequence, Optional, Callable
from dataclasses import dataclass
from random import randint

from domain.model import Element, Player, Level, WorldVector, ElementOrb, Wall, Projectile
import domain.events as events


@dataclass(frozen=True)
class World:
    player: Player
    level: Level
    projectiles: list[Projectile]


class Effect[T](Protocol):
    def apply(self, context: T) -> None: ...


class EffectSequence[T]:
    def __init__(self, *effects: Effect[T]) -> None:
        self._effects = effects

    def apply(self, context: T) -> None:
        for effect in self._effects:
            effect.apply(context)

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

    def apply(self, context: World) -> None: # Just call apply and implement effect interface?...
        self._effect.apply(context)


class Target[T](Protocol): #Sort of the same as number?
    def resolve(self, context: World) -> T: ...

class CasterPlayerTarget:
    @staticmethod
    def resolve(context: World) -> Player:
        return context.player

class CasterPositionTarget: # Just do casterplayertarget and take position attribute instead?
    def resolve(self, context: World) -> WorldVector:
        return context.player.position

class CasterFacingDirectionTarget:
    def resolve(self, context: World) -> WorldVector:
        pass


class Number[T: (int, float)](Protocol): # Value? FutureValue? DeferredValue?
    def evaluate(self, context: World) -> T: ... # Context!?

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


class Condition[T](Protocol):
    def check(self, arg: T) -> bool: ...


class Cost(Condition[Player], Effect[Player], Protocol): #Any cleaner way?
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

    def apply(self, context: World) -> None:
        pass

class HealthCost:
    def __init__(self, amount: Number[int]) -> None:
        self._amount = amount

    def check(self, _: Player) -> bool:
        return True

    def apply(self, player: Player) -> None:
        health_cost = self._amount.evaluate(player)
        player.damage(health_cost)

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


class PickupOrb:
    def __init__(self, player: Target[Player], orb: Target[Optional[ElementOrb]]):
        self._player = player
        self._orb = orb
    
    def apply(self, context: World) -> None:
        player = self._player.resolve(context)
        if orb := self._orb.resolve(context):
            context.level.remove_orb(orb)
            player.give_element(orb.element)
            player.events.append(events.OrbPickup()) # World events?

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
    destination = RunDestinationTarget(
        origin=CasterPositionTarget(),
        direction=direction,
        duration=duration,
        speed=PlayerRunSpeed(
            CasterPlayerTarget()
        )
    )
    return EffectConditional( # Probably a lot better to just set velocity here and make a physics system handle collisions...
        condition=AnyResult(
            Touching(
                target=destination,
                colliders=AllWalls()
            )
        ),
        on_pass=NoEffect(),
        on_fail=DisplaceEffect(
            player=CasterPlayerTarget(),
            destination=destination
            )
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
#     def apply(self, context: World) -> None:
#         position = self._position_selector(context)
#         element = self._element_selector(context)
#         context.level.spawn_orb(1.0)


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
        x_a, y_a, _ = self._position_a.resolve(world)
        x_b, y_b, _ = self._position_b.resolve(world)
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


def create_push_spell() -> Spell:
    pass

#
# spell_map: dict[Cost, Spell] = { # Order important? Make list of tuples?
#     ElementCost(Element.FIRE, Element.FIRE,  Element.WIND): create_fireball_spell(),
#     ElementCost(Element.WIND, Element.WATER, Element.WATER): create_heal_spell(),
# }
#
#
# # SpellFactory
# def conjure_spell(context: World) -> Effect[World]:# Optional[Spell]:
#     for cost, spell in spell_map.items():
#         if not cost.check(context.player): continue
#         # Potentially check other preconditions?
#         cost.apply(context.player)
#         return spell
#     else:
#         return NoEffect() #None # NoSpell?
#
#
# class ConjureSpell:
#     #def __init__(self, user_input: UserInput) -> None:
#     def apply(self, context: World) -> None:  # Optional[Spell]:
#         for cost, spell in spell_map.items():
#             if not cost.check(context.player): continue
#             # Potentially check other preconditions?
#             cost.apply(context.player)
#             spell.apply(context)
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

