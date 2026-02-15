from interface.ascii.presenter import AsciiPresenter, ConsoleVector, Assets, UiGraphic, UiAssetModel, WorldGraphic, WorldAssetModel
from interface.ascii.controller import AsciiController
from interactors.interactors import SceneChoice
from interface.state_machine import StateMachine
from domain.model import Player, WorldVector, Level, Wall
from interactors.scenes.start_menu import StartMenu
from interactors.scenes.fight_scene import FightScene
from view.ascii_view import AsciiView


def main() -> None:
    presenter = AsciiPresenter(
        console_size=ConsoleVector(10, 10),
        assets=Assets(  # .from_file?
            ui={
                UiGraphic.START_GAME_BUTTON: UiAssetModel("S", ConsoleVector(3, 2)),
                UiGraphic.QUIT_GAME_BUTTON: UiAssetModel("Q", ConsoleVector(3, 4)),
            },
            world={
                WorldGraphic.PLAYER: WorldAssetModel("P"),
                WorldGraphic.WALL: WorldAssetModel("W"),
                WorldGraphic.ORB: WorldAssetModel("O"),
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
    controller = AsciiController(state_machine)
    
    view = AsciiView(controller, presenter, 10)
    view.run()
    

if __name__ == "__main__":
    main()