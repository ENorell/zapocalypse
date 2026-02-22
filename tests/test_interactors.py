from unittest import TestCase, mock, main

from interactors.presenter_model import QuitButton, StartButton, PlayerModel, OrbSlots
from interactors.scene import UserInput, StopGame, Presenter, SceneSwitch
from domain.model import Player, WorldVector, Level
from interactors.scenes.start_menu import StartMenu
from interactors.scenes.fight_scene import FightScene


class TestStartMenu(TestCase):
    def test_quit_game(self) -> None:
        presenter = mock.create_autospec(Presenter)
        scene = StartMenu(presenter)
        quit_input = UserInput(confirm=True, selected_ids=[id(QuitButton)])

        with self.assertRaises(StopGame):
            scene.update(quit_input)

    def test_start_menu_hover_button(self) -> None:
        presenter = mock.create_autospec(Presenter)
        scene = StartMenu(presenter)
        user_input = UserInput(confirm=False, selected_ids=[id(StartButton)])

        scene.update(user_input)

        presenter.draw.assert_called_with(
            [
            StartButton(id=id(StartButton), highlight=True),
            QuitButton(id=id(QuitButton), highlight=False),
            ]
        )

    def test_switch_scene(self) -> None:
        presenter = mock.create_autospec(Presenter)
        scene = StartMenu(presenter)
        switch_input = UserInput(confirm=True, selected_ids=[id(StartButton)])

        with self.assertRaises(SceneSwitch):
            scene.update(switch_input)


class TestFight(TestCase):
    def test_walk_input(self) -> None:
        player = Player(WorldVector(1, 0))
        level = Level(player, walls=[], orbs=[])
        presenter = mock.create_autospec(Presenter)
        scene = FightScene(presenter, level)
        user_input = UserInput(right=True)
        
        scene.update(user_input)

        presenter.draw.assert_called_once_with([
            PlayerModel(id=id(player), position=WorldVector(1.0, 0.0)),
            OrbSlots(elements=[])
        ])



if __name__ == "__main__":
    main()