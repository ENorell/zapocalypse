from typing import Optional

from domain.model import WorldVector, Element  # Red flag?
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

    def _get_render_models(self, presenter_model: PresenterModel) -> list[RenderModel]:
        match presenter_model:
            case PlayerModel(id_, position):
                return [self._draw_world_entity(id_, position, Graphic.PLAYER)]
            case OrbModel(id_, position, element):
                return [self._draw_world_entity(id_, position, _get_element_graphic(element))]
            case WallModel(id_, position):
                return [self._draw_world_entity(id_, position, Graphic.WALL)]
            case OrbSlots(orbs):
                return _draw_orb_ui(self._assets, orbs)
            case StartButton(id_):
                return [_draw_start_button(self._assets, id_)]
            case QuitButton(id_):
                return [_draw_quit_button(self._assets, id_)]
            case _:
                raise UnknownModelType(f"Cannot recognize model {type(presenter_model)}")
    
    def _get_asset(self, graphic: Graphic) -> Asset:
        try:
            return self._assets[graphic]
        except KeyError:
            raise MissingAssetError(f"No asset found for graphic {graphic}")

    def _draw_world_entity(self, id_: int, position: WorldVector, graphic: Graphic) -> RenderModel:
        pixel_position = transform_world_to_pixel(position)
        asset = self._get_asset(graphic)

        return RenderModel(
            id=id_,
            position=pixel_position,
            asset=asset
        )


def _draw_start_button(assets: dict[Graphic, Asset], id_: int) -> RenderModel:
    start_button_top_left_position = PixelVector(100,200)
    return RenderModel(
        id=id_,
        position=start_button_top_left_position,
        asset=assets[Graphic.START_GAME_BUTTON]
    )


def _draw_quit_button(assets: dict[Graphic, Asset], id_: int) -> RenderModel:
    quit_button_top_left_position = PixelVector(100,400)
    return RenderModel(
        id=id_,
        position=quit_button_top_left_position,
        asset=assets[Graphic.QUIT_GAME_BUTTON]
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


def _draw_orb_ui(assets: dict[Graphic, Asset], elements: list[Optional[Element]]) -> list[RenderModel]:
    result = []

    slot_background_asset = assets[Graphic.ORB_SLOT_BACKGROUND]
    result.append(RenderModel(position=PixelVector(500, 0), asset=slot_background_asset))

    for element, position in zip(elements, [(550, 25), (600, 25), (650, 25)]): # TODO dynamic scaling to any resolution
        graphic = _get_element_graphic(element)

        result.append(RenderModel(
            position=PixelVector(*position),
            asset=assets[graphic],
            #SIZE?
        ))
    return result