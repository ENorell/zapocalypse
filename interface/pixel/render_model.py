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

Asset = ImageAsset | BoxAsset


@dataclass
class RenderModel:
    position: PixelVector
    asset: Asset
    id: Optional[int] = None
    rotation: int = 0
