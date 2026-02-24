from dataclasses import dataclass
from abc import ABC


class Event(ABC): ...


@dataclass(frozen=True)
class Collision(Event): ...

@dataclass(frozen=True)
class OrbPickup(Event): ...
