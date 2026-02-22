from typing import NamedTuple
from dataclasses import dataclass, field

from interactors.scene import WorldGraphic, UiGraphic, PresenterModel, UiPresenterModel, WorldPresenterModel


class ConsoleVector(NamedTuple):
    x: int
    y: int


@dataclass
class RenderModel:
    frame: str
    ids: list[int]

@dataclass
class WorldAssetModel:
    character: str

@dataclass
class UiAssetModel:
    character: str
    position: ConsoleVector

@dataclass
class Assets:
    world: dict[WorldGraphic, WorldAssetModel] = field(default_factory=dict)
    ui: dict[UiGraphic, UiAssetModel] = field(default_factory=dict)


class AsciiPresenter:
    def __init__(self, console_size: ConsoleVector, assets: Assets) -> None:
        self._console_size = console_size
        self._assets = assets
        self.render_model = RenderModel("", [])

    def _make_base_frame(self) -> list[list[str]]:
        width, height = self._console_size
        return [['+' for _ in range(width)] for _ in range(height)]

    def _draw_ui_model(self, current_frame: list[PresenterModel], graphic: UiGraphic, to_highlight: bool) -> None:
        asset = self._assets.ui[graphic]
        x, y = asset.position
        current_frame[y - 1][x - 1] = asset.character
        if to_highlight:
            current_frame[y - 1][x - 2] = ">"

    def draw(self, models: list[PresenterModel]) -> None:
        current_frame = self._make_base_frame()

        for model in models:
            match model:
                case UiPresenterModel(_, graphic, to_highlight):
                    self._draw_ui_model(current_frame, graphic, to_highlight)

                case WorldPresenterModel(_, graphic, position):
                    asset = self._assets.world[graphic]
                    x, y = position
                    current_frame[round(y % (self._console_size.y - 1))][
                        round(x % (self._console_size.x - 1))] = asset.character

        self.render_model = RenderModel(
            '\n'.join([' '.join(row) for row in current_frame]),
            [model.id for model in models]
            )

