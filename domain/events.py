from dataclasses import dataclass

from domain.model import Event


@dataclass(frozen=True)
class Collision(Event): ...

@dataclass(frozen=True)
class OrbPickup(Event): ...