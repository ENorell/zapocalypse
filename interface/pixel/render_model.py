from typing import NamedTuple, Optional
from dataclasses import dataclass
from pathlib import Path
from enum import Enum, auto


class PixelVector(NamedTuple):
    x: int
    y: int


@dataclass
class ImageAsset:
    file: Path
    size: PixelVector


class RGB(NamedTuple):
    red: int
    green: int
    blue: int


class Alignment(Enum):
    TOP_LEFT = auto()
    CENTER = auto()


class Text(NamedTuple):
    content: str
    size: int = 15
    alignment: Alignment = Alignment.CENTER


@dataclass(frozen=True)
class BoxAsset:
    size: PixelVector
    color: RGB
    text: Optional[Text] = None


@dataclass(frozen=True)
class CircleAsset:
    radius: int
    color: RGB

Asset = ImageAsset | BoxAsset | CircleAsset 


@dataclass
class RenderModel:
    position: PixelVector
    asset: Asset
    id: int = 0 # Om denna är optional och kan vara None måste DeviceEvent event_ids också kunna ta None samt kan inte get_hovered_ids i pygame_view endast returna list -- Att diskutera?
    rotation: int = 0
    layer: int = 0
