from domain.model import Player, WorldVector, Level, Wall, WallType, ElementOrb, Element
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
    )

    player = Player(position=WorldVector(0, 0))
    level = Level(
        [Wall(WallType.STONE, WorldVector(5, 5))],
        [ElementOrb(Element.FIRE, WorldVector(3, 3))]
    )

    state_machine = StateMachine(
        scenes={
            SceneChoice.START_MENU: StartMenu(presenter),
            SceneChoice.FIGHT: FightScene(presenter, player, level)
        },
        start_scene=SceneChoice.START_MENU
    )
    controller = PixelController(state_machine)

    view = PygameView(controller, presenter, 30, "Zapocalypse")
    view.run()


if __name__ == "__main__":
    main()