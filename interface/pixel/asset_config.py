from enum import StrEnum, auto
from pathlib import Path

from interface.pixel.render_model import Asset, BoxAsset, PixelVector, RGB, Text, ImageAsset, CircleAsset

## New graphics need to be added below when introduced ##

class Graphic(StrEnum):
    PLAYER = auto()
    WALL = auto()
    ORB = auto()
    START_GAME_BUTTON = auto()
    QUIT_GAME_BUTTON = auto()
    FIRE_ORB_SLOT = auto()
    WATER_ORB_SLOT = auto()
    WIND_ORB_SLOT = auto()
    THUNDER_ORB_SLOT = auto()
    ROOT_ORB_SLOT = auto()
    EMPTY_ORB_SLOT = auto()
    ORB_SLOT_BACKGROUND = auto()


def load_asset_map() -> dict[Graphic, Asset]:
    return {
        Graphic.START_GAME_BUTTON: BoxAsset(size=PixelVector(100, 100), color=RGB(0, 255, 0), text=Text("START")),
        Graphic.QUIT_GAME_BUTTON: BoxAsset(size=PixelVector(100, 100), color=RGB(255, 0, 0)),
        Graphic.PLAYER: ImageAsset(file=Path("assets/wizard.png"), size=PixelVector(100, 100)),
        Graphic.WALL: BoxAsset(size=PixelVector(100, 100), color=RGB(150, 150, 0)),
        Graphic.ORB: BoxAsset(size=PixelVector(75, 75), color=RGB(0, 0, 255)),
        Graphic.FIRE_ORB_SLOT: CircleAsset(radius=25, color=RGB(255, 0, 0)),
        Graphic.WATER_ORB_SLOT: CircleAsset(radius=25, color=RGB(0, 0, 255)),
        Graphic.ROOT_ORB_SLOT: CircleAsset(radius=25, color=RGB(255, 0, 255)),
        Graphic.THUNDER_ORB_SLOT: CircleAsset(radius=25, color=RGB(255, 250, 100)),
        Graphic.EMPTY_ORB_SLOT: CircleAsset(radius=25, color=RGB(0, 0, 0)),
        Graphic.ORB_SLOT_BACKGROUND: BoxAsset(size=PixelVector(250, 50), color=RGB(0, 100, 100)),
    }