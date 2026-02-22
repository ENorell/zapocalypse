from domain.model import Player, WorldVector, Level, Wall
from interactors.scenes.start_menu import StartMenu
from interactors.scenes.fight_scene import FightScene
from interactors.scene import SceneChoice
from interface.state_machine import StateMachine
from interface.pixel.presenter import PixelPresenter
from interface.pixel.render_model import PixelVector
from interface.pixel.asset_config import load_asset_map
from interface.pixel.controller import PixelController
from view.pygame_view import PygameView


def main() -> None:
    presenter = PixelPresenter(
        screen_size=PixelVector(800, 600),
        assets=load_asset_map()
        # {
        #     Graphic.START_GAME_BUTTON: BoxAsset(size=PixelVector(100, 100), color=RGB(0,255,0), text=Text("START")),
        #     Graphic.QUIT_GAME_BUTTON: BoxAsset(size=PixelVector(100, 100), color=RGB(255,0,0)),
        #     Graphic.PLAYER: ImageAsset(file=Path("assets/wizard.png"), size=PixelVector(100, 100)),
        #     Graphic.WALL: BoxAsset(size=PixelVector(100, 100), color=RGB(150,150,0)),
        #     Graphic.ORB: BoxAsset(size=PixelVector(75, 75), color=RGB(0,0,255)),
        #     Graphic.FIRE_ORB_SLOT: CircleAsset(radius=25, color=RGB(255, 0, 0)),
        #     Graphic.WATER_ORB_SLOT: CircleAsset(radius=25, color=RGB(0, 0, 255)),
        #     Graphic.EMPTY_ORB_SLOT: CircleAsset(radius=25, color=RGB(0, 0, 0)),
        #     Graphic.ORB_SLOT_BACKGROUND: BoxAsset(size=PixelVector(250, 50), color=RGB(0, 100, 100)),
        # }
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