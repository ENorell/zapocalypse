from datetime import timedelta
from unittest import TestCase, mock, main

from interactors.interactors import UserInput, StopGame, Presenter
from domain.model import Player, WorldVector, Level
from interactors.scenes.start_menu import StartMenu
from interactors.scenes.fight_scene import FightScene
from interface.pixel.presenter import UiGraphic, WorldGraphic, UiPresenterModel,WorldPresenterModel


class TestStartMenu(TestCase):
    def test_quit_game(self) -> None:
        presenter = mock.create_autospec(Presenter)
        scene = StartMenu(presenter)
        quit_input = UserInput(confirm=True, selected_ids=[id(UiGraphic.QUIT_GAME_BUTTON)], delta_time=timedelta())

        with self.assertRaises(StopGame):
            scene.update(quit_input)

    def test_start_menu_hover_button(self) -> None:
        presenter = mock.create_autospec(Presenter)
        scene = StartMenu(presenter)
        user_input = UserInput(confirm=False, selected_ids=[id(UiGraphic.START_GAME_BUTTON)], delta_time=timedelta())

        scene.update(user_input)

        presenter.draw.assert_called_with(
            [
            UiPresenterModel(id=id(UiGraphic.START_GAME_BUTTON), graphic=UiGraphic.START_GAME_BUTTON, to_highlight=True),
            UiPresenterModel(id=id(UiGraphic.QUIT_GAME_BUTTON), graphic=UiGraphic.QUIT_GAME_BUTTON)
            ]
        )


class TestFight(TestCase):
    def test_walk_input(self) -> None:
        player = Player(WorldVector(1, 0))
        level = Level(player, walls=[], orbs=[])
        presenter = mock.create_autospec(Presenter)
        scene = FightScene(presenter, level)
        user_input = UserInput(right=True, delta_time=timedelta())
        
        scene.update(user_input)

        presenter.draw.assert_called_once_with([
            WorldPresenterModel(id=id(player), graphic=WorldGraphic.PLAYER, position=WorldVector(1 ,0))
        ])



if __name__ == "__main__":
    main()