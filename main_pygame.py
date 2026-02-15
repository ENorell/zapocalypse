from pathlib import Path

from interactors.interactors import SceneChoice
from interface.state_machine import StateMachine
from domain.model import Player, WorldVector, Level, Wall
from interactors.scenes.start_menu import StartMenu
from interactors.scenes.fight_scene import FightScene
from interface.pixel.presenter import PixelPresenter, PixelVector, Assets, UiGraphic, UiAssetModel, WorldGraphic, \
    WorldAssetModel, ImageAsset, RGB, BoxAsset, Text
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
            world={
                WorldGraphic.PLAYER: WorldAssetModel(ImageAsset(file=Path("assets/wizard.png"), size=PixelVector(100, 100))),
                WorldGraphic.WALL: WorldAssetModel(BoxAsset(size=PixelVector(100, 100), color=RGB(150,150,0))),
                WorldGraphic.ORB: WorldAssetModel(BoxAsset(size=PixelVector(75, 75), color=RGB(0,0,255))),
            }
        )
    )

    world_repository = Level(
        Player(position=WorldVector(0, 0)),
        [Wall(WorldVector(5, 5))],
        []
    )
    world_repository.spawn_orb()

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