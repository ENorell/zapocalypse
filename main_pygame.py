from pathlib import Path

from interactors.interactors import SceneChoice
from interface.state_machine import StateMachine
from domain.model import Player, WorldVector, Level, Wall, WallType
from interactors.scenes.start_menu import StartMenu
from interactors.scenes.fight_scene import FightScene
from interface.pixel.presenter import PixelPresenter, PixelVector, Assets, HUDGraphic, HUDAssetModel, UiGraphic, UiAssetModel, \
    WorldGraphic, WorldAssetModel, ImageAsset, RGB, BoxAsset, Text
from interface.pixel.controller import PixelController
from view.pygame_view import PygameView


def main() -> None:
    presenter = PixelPresenter(
        screen_size=PixelVector(800, 600),
        assets=Assets(  # .from_file?
            ui={
                UiGraphic.START_GAME_BUTTON: UiAssetModel(BoxAsset(size=PixelVector(100, 100), color=RGB(0,255,0), text=Text("START")), position=PixelVector(100,100)),
                UiGraphic.QUIT_GAME_BUTTON: UiAssetModel(BoxAsset(size=PixelVector(100, 100), color=RGB(255,0,0)), position=PixelVector(100,300)),
            },
            hud={
                HUDGraphic.ORB_INVENTORY_BACKDROP: HUDAssetModel(BoxAsset(size=PixelVector(500, 60), color=RGB(0,0,139)), position=PixelVector(800 - 260, 10)),
                HUDGraphic.ORB_INVENTORY_SLOT_ONE: HUDAssetModel(BoxAsset(size=PixelVector(70, 40), color=RGB(0,200,139)), position=PixelVector(800 - 250, 20)),
                HUDGraphic.ORB_INVENTORY_SLOT_TWO: HUDAssetModel(BoxAsset(size=PixelVector(70, 40), color=RGB(0,200,139)), position=PixelVector(800 - 170, 20)),
                HUDGraphic.ORB_INVENTORY_SLOT_THREE: HUDAssetModel(BoxAsset(size=PixelVector(70, 40), color=RGB(0,200,139)), position=PixelVector(800 - 90, 20)),
            },
            world={
                WorldGraphic.PLAYER: WorldAssetModel(ImageAsset(file=Path("assets/wizard.png"), size=PixelVector(100, 100))),
                WorldGraphic.WALL: WorldAssetModel(BoxAsset(size=PixelVector(100, 100), color=RGB(150,150,0))),
                WorldGraphic.WALL_STONE: WorldAssetModel(ImageAsset(file=Path("assets/wall_stone.png"), size=PixelVector(100, 100))),
                WorldGraphic.ORB_ELEMENT_WATER: WorldAssetModel(ImageAsset(file=Path("assets/water_element.png"), size=PixelVector(100, 100))),
                WorldGraphic.ORB_ELEMENT_FIRE: WorldAssetModel(ImageAsset(file=Path("assets/fire_element.png"), size=PixelVector(100, 100))),
                WorldGraphic.ORB_ELEMENT_ROOT: WorldAssetModel(BoxAsset(size=PixelVector(75, 75), color=RGB(0,0,255))),
                WorldGraphic.ORB_ELEMENT_THUNDER: WorldAssetModel(BoxAsset(size=PixelVector(75, 75), color=RGB(0,0,255))),
                WorldGraphic.ORB_ELEMENT_WIND: WorldAssetModel(BoxAsset(size=PixelVector(75, 75), color=RGB(0,0,255))),
            }
        )
    )
    
    world_repository = Level(
        Player(position=WorldVector(0, 0)),
        [Wall(WallType.STONE, WorldVector(5, 5)),
         Wall(WallType.STONE, WorldVector(5, 4)),
         Wall(WallType.STONE, WorldVector(5, 3)),], []
    )

    state_machine = StateMachine(
        scenes={
            SceneChoice.START_MENU: StartMenu(presenter),
            SceneChoice.FIGHT: FightScene(presenter, world_repository)
        },
        start_scene=SceneChoice.START_MENU
    )
    controller = PixelController(state_machine)

    view = PygameView(controller, presenter, 30, "Zapocalypse")
    view.run()


if __name__ == "__main__":
    main()