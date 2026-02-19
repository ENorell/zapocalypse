from typing import NamedTuple, Optional
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum, auto

from domain.model import WorldVector # Red flag?
from interactors.interactors import WorldGraphic, UiGraphic, HUDGraphic, PresenterModel, UiPresenterModel, WorldPresenterModel, HUDPresenterModel


class PixelVector(NamedTuple):
    x: int
    y: int


class RGB(NamedTuple):
    red: int
    green: int
    blue: int

@dataclass
class ImageAsset:
    file: Path
    size: PixelVector


class Alignment(Enum):
    TOP_LEFT = auto()
    CENTER = auto()

class Text(NamedTuple):
    content: str
    size: int = 15
    alignment: Alignment = Alignment.CENTER


@dataclass
class BoxAsset:
    size: PixelVector
    color: RGB
    text: Optional[Text] = None

GraphicAsset = ImageAsset | BoxAsset # TextAsset?


Asset = ImageAsset | BoxAsset
@dataclass
class WorldAssetModel:
    asset: Asset
@dataclass
class UiAssetModel:
    asset: Asset
    position: PixelVector
@dataclass
class HUDAssetModel:
    asset: Asset
    position: PixelVector
@dataclass
class Assets:
    world: dict[WorldGraphic, WorldAssetModel] = field(default_factory=dict)
    ui: dict[UiGraphic, UiAssetModel] = field(default_factory=dict)
    hud: dict[HUDGraphic, HUDAssetModel] = field(default_factory=dict)


@dataclass
class InterfaceAsset:
    asset: GraphicAsset
    position: PixelVector

@dataclass
class WorldAsset:
    asset: GraphicAsset

@dataclass
class AssetData:
    path: Path
    size: tuple[int, int]

class PresenterError(Exception): ...

class MissingAssetError(PresenterError): pass

class UnknownModelType(PresenterError): pass


@dataclass
class RenderModel:
    id: int
    position: PixelVector
    asset: GraphicAsset
    rotation: int = 0


def transform_world_to_pixel(world_coordinate: WorldVector) -> PixelVector:
    x, y = world_coordinate
    return PixelVector(round(100*x), round(100*y))


class PixelPresenter:
    def __init__(self,
                 screen_size: PixelVector,
                 assets: Assets,
                 ):
        self.screen_size = screen_size
        self._assets = assets
        self.render_models: list[RenderModel] = []

    def _draw_world_entity(self, id_: int, position: WorldVector, graphic: WorldGraphic):
        pixel_position = transform_world_to_pixel(position)
        try:
            asset_data = self._assets.world[graphic]
        except KeyError:
            raise MissingAssetError(f"No asset found for graphic {graphic}")

        render_model = RenderModel(
            id=id_,
            position=pixel_position,
            asset=asset_data.asset
        )
        self.render_models.append(render_model)

    def _draw_interface_entity(self, id_: int, graphic: UiGraphic):
        asset_data = self._assets.ui.get(graphic)
        if not asset_data: raise MissingAssetError(f"No asset found for graphic {graphic}")

        render_model = RenderModel(
            id=id_,
            position=asset_data.position,
            asset=asset_data.asset
        )
        self.render_models.append(render_model)

    def _draw_hud_entity(self, id_: int, graphic: HUDGraphic):
        asset_data = self._assets.hud.get(graphic)
        if not asset_data: raise MissingAssetError(f"No asset found for graphic {graphic}")

        render_model = RenderModel(
                id=id_,
                position=asset_data.position,
                asset=asset_data.asset
            )
        self.render_models.append(render_model)

    def draw(self, presenter_models: list[PresenterModel]) -> None:
        self.render_models.clear()

        for entity in presenter_models:
            match entity:
                case UiPresenterModel(id_, graphic): self._draw_interface_entity(id_, graphic)
                case WorldPresenterModel(id_, graphic, position): self._draw_world_entity(id_, position, graphic)
                case HUDPresenterModel(id_, graphic): self._draw_hud_entity(id_, graphic)
                case _: raise UnknownModelType(f"Cannot recognize model {type(entity)}")
