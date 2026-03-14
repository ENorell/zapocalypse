from collections import Counter
from typing import Protocol, Sequence, Optional
from dataclasses import dataclass
from random import randint

from domain.model import Element, Player


#from domain.model import Player

@dataclass(frozen=True)
class Context: ...

@dataclass(frozen=True)
class Player: ...
@dataclass(frozen=True)
class Position: ...


class Effect[T](Protocol): #T to handle any type?
    def apply(self, context: T) -> None: ...


class EffectSequence[T]:
    def __init__(self, effects: Sequence[Effect[T]]) -> None:
        self._effects = effects

    def apply(self, context: T) -> None:
        for effect in self._effects:
            effect.apply(context)


class Spell:
    def __init__(self, name: str, effect: Effect[Context]):
        self._name = name
        self._effect = effect
        #cost

    def cast(self, context: Context) -> None:
        self._effect.apply(context)


class Target[T](Protocol):
    def resolve(self, context: Context) -> T: ...

class CasterPlayerTarget:
    def resolve(self, context: Context) -> Player:
        pass

class CasterPositionTarget:
    def resolve(self, context: Context) -> Position:
        pass

class CasterFacingDirectionTarget:
    def resolve(self, context: Context) -> Position:
        pass

a: Target[Player] = CasterPlayerTarget()

class Number[T: (int, float)](Protocol):
    def evaluate(self) -> T: ...

class ExactNumber[T: (int, float)]:
    def __init__(self, value: T) -> None:
        self._value: T = value

    def evaluate(self) -> T:
        return self._value

b: Number[float] = ExactNumber(10)

class RandomNumber:
    def __init__(self, from_number: int, to_number: int):
        self._between = (from_number, to_number)

    def evaluate(self) -> int:
        return randint(*self._between)


class Condition[T](Protocol):
    def check(self, arg: T) -> bool: ...

class ElementCondition:
    def __init__(self, elements: list):
        self._elements = elements
        
    def check(self, arg: Player) -> bool:
        return False

has_elements: Condition[Player] = ElementCondition(["fire", "water"])


class ICost(Protocol): #Condition?
    def can_afford(self, player: Player) -> bool: ...
    def pay_cost(self, player: Player) -> bool: ...

class Cost:
    def __init__(self, charge: Effect[Player], affords: Condition[Player]) -> None:
        self._charge = charge
        self._affords = affords

    def affords(self) -> bool:
        return self._affords.check()

class Cost2(Condition[Player], Effect[Player], Protocol): #Any cleaner way?
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

    def apply(self, context: Context) -> None:
        health_cost = self._amount.evaluate()
        self.context.player.damage(health_cost)


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
                 origin: Target[Position],
                 direction: Target[Position],
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
        

class RootedEffect:
    def __init__(self,
                 target: Target[Player],
                 ) -> None:
        self._target = target
        
    def apply(self, context: Context) -> None:
        pass


class Precondition:
    def __init__(self, condition, on_pass, on_fail) -> None:
        pass




def create_fireball_spell() -> Spell:
    return Spell(
        name="Fire Ball",
        effect=ProjectileEffect(
            element=Element.FIRE,
            origin=CasterPositionTarget(),
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



spell_map: dict[Cost2, Spell] = {
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

