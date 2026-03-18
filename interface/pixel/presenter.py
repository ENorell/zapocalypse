from typing import Optional, Sequence

from domain.game_objects import WorldVector, Element, WallType  # Red flag?
from interactors.presenter_model import PresenterModel, OrbSlots, PlayerModel, OrbModel, StartButton, QuitButton, \
    WallModel
from interface.pixel.render_model import PixelVector, RenderModel, Asset
from interface.pixel.asset_config import Graphic


class PresenterError(Exception): ...

class MissingAssetError(PresenterError): pass

class UnknownModelType(PresenterError): pass


def transform_world_to_pixel(world_coordinate: WorldVector) -> PixelVector:
    x, y = world_coordinate
    return PixelVector(round(100*x), round(100*y))


class PixelPresenter:
    def __init__(self,
                 screen_size: PixelVector,
                 assets: dict[Graphic, Asset]
                 ):
        self.screen_size = screen_size
        self._assets = assets
        self.render_models: list[RenderModel] = []

    def draw(self, presenter_models: list[PresenterModel]) -> None:
        self.render_models.clear()
        for presenter_model in presenter_models:
            render_models = self._get_render_models(presenter_model)
            self.render_models.extend(render_models)
        
        self.render_models.sort(key=lambda x: x.z_position)

    def _get_render_models(self, presenter_model: PresenterModel) -> list[RenderModel]:
        match presenter_model:
            case PlayerModel(id_, position):
                return [self._draw_world_entity(id_, position, Graphic.PLAYER, 1.0)]
            case OrbModel(id_, position, element):
                return [self._draw_world_entity(id_, position, _get_element_graphic(element), 1.0)]
            case WallModel(id_, position, wall_type):
                return [self._draw_world_entity(id_, position, _get_wall_graphic(wall_type), 1.0)]
            case OrbSlots(orbs):
                return _draw_orb_ui(self._assets, orbs, 100.0)
            case StartButton(id_):
                return [_draw_start_button(self._assets, id_, 100.0)]
            case QuitButton(id_):
                return [_draw_quit_button(self._assets, id_, 100.0)]
            case _:
                raise UnknownModelType(f"Cannot recognize model {type(presenter_model)}")
    
    def _get_asset(self, graphic: Graphic) -> Asset:
        try:
            return self._assets[graphic]
        except KeyError:
            raise MissingAssetError(f"No asset found for graphic {graphic}")

    def _draw_world_entity(self, id_: int, position: WorldVector, graphic: Graphic, z_position: float) -> RenderModel:
        pixel_position = transform_world_to_pixel(position)
        asset = self._get_asset(graphic)

        return RenderModel(
            id=id_,
            position=pixel_position,
            asset=asset,
            z_position=z_position
        )


def _draw_start_button(assets: dict[Graphic, Asset], id_: int, z_position: float) -> RenderModel:
    start_button_top_left_position = PixelVector(100,200)
    return RenderModel(
        id=id_,
        position=start_button_top_left_position,
        asset=assets[Graphic.START_GAME_BUTTON],
        z_position=z_position
    )


def _draw_quit_button(assets: dict[Graphic, Asset], id_: int, z_position: float) -> RenderModel:
    quit_button_top_left_position = PixelVector(100,400)
    return RenderModel(
        id=id_,
        position=quit_button_top_left_position,
        asset=assets[Graphic.QUIT_GAME_BUTTON],
        z_position=z_position
    )

def _get_element_graphic(element: Optional[Element]) -> Graphic:
    match element:
        case Element.WATER:   return Graphic.WATER_ORB_SLOT
        case Element.FIRE:    return Graphic.FIRE_ORB_SLOT
        case Element.WIND:    return Graphic.WIND_ORB_SLOT
        case Element.THUNDER: return Graphic.THUNDER_ORB_SLOT
        case Element.ROOT:    return Graphic.ROOT_ORB_SLOT
        # Etc.
        case None:          return Graphic.EMPTY_ORB_SLOT
        case _: raise ValueError(f"Unknown Element {element}")

def _get_wall_graphic(wall_type: Optional[WallType]) -> Graphic:
    match wall_type:
        case WallType.STONE:   return Graphic.STONE_WALL
        case WallType.BUSH:    return Graphic.BUSH_WALL
        # Etc.
        case None:          return Graphic.EMPTY_ORB_SLOT
        case _: raise ValueError(f"Unknown Wall {wall_type}")

def _draw_orb_ui(assets: dict[Graphic, Asset], elements: Sequence[Optional[Element]], z_position: float) -> list[RenderModel]:
    result = []

    slot_background_asset = assets[Graphic.ORB_SLOT_BACKGROUND]
    result.append(RenderModel(
        position=PixelVector(500, 0), 
        asset=slot_background_asset, 
        z_position=99
    ))

    for element, position in zip(elements, [(550, 25), (600, 25), (650, 25)]): # TODO dynamic scaling to any resolution
        graphic = _get_element_graphic(element)

        result.append(RenderModel(
            position=PixelVector(*position),
            asset=assets[graphic],
            z_position=z_position
            #SIZE?
        ))
    return result