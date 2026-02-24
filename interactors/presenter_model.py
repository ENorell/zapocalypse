from typing import Optional
from dataclasses import dataclass
from abc import ABC

from domain.model import Element, WorldVector


class PresenterModel(ABC): ...


@dataclass(frozen=True)
class ButtonPresenterModel(PresenterModel, ABC):
    id: int
    highlight: bool = False


@dataclass(frozen=True)
class WorldPresenterModel(PresenterModel, ABC):
    id: int
    position: WorldVector


## New models are added below ##

@dataclass(frozen=True)
class PlayerModel(WorldPresenterModel): ...

@dataclass(frozen=True)
class WallModel(WorldPresenterModel): ...

@dataclass(frozen=True)
class OrbModel(WorldPresenterModel):
    element: Element

@dataclass(frozen=True)
class OrbSlots(PresenterModel):
    elements: list[Optional[Element]]

@dataclass(frozen=True)
class StartButton(ButtonPresenterModel): ...

@dataclass(frozen=True)
class QuitButton(ButtonPresenterModel): ...

