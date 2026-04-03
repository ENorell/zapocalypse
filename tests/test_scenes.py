# from datetime import timedelta
# from unittest import TestCase, mock, main

# from interactors.presenter_model import QuitButton, StartButton, PlayerModel, OrbSlots
# from interactors.scene import UserInput, StopGame, Presenter, SceneSwitch
# from domain.model import Player, Level
# from domain.game_objects import WorldVector
# from interactors.scenes.start_menu import StartMenu
# from interactors.scenes.fight_scene import FightScene


# class TestStartMenu(TestCase):
#     def test_quit_game(self) -> None:
#         presenter = mock.create_autospec(Presenter)
#         scene = StartMenu(presenter)
#         quit_input = UserInput(confirm=True, selected_ids=[id(QuitButton)])

#         with self.assertRaises(StopGame):
#             scene.update(quit_input)

#     def test_start_menu_hover_button(self) -> None:
#         presenter = mock.create_autospec(Presenter)
#         scene = StartMenu(presenter)
#         user_input = UserInput(confirm=False, selected_ids=[id(StartButton)])

#         scene.update(user_input)

#         presenter.draw.assert_called_with(
#             [
#             StartButton(id=id(StartButton), highlight=True),
#             QuitButton(id=id(QuitButton), highlight=False),
#             ]
#         )

#     def test_switch_scene(self) -> None:
#         presenter = mock.create_autospec(Presenter)
#         scene = StartMenu(presenter)
#         switch_input = UserInput(confirm=True, selected_ids=[id(StartButton)])

#         with self.assertRaises(SceneSwitch):
#             scene.update(switch_input)


# class TestFight(TestCase):
#     def _player_position_from_mock(self, draw_mock: mock.Mock) -> WorldVector:
#         match draw_mock.call_args:
#             case [[PlayerModel(_, position), OrbSlots(_)]], _:
#                 return position
#             case [args], _:
#                 self.fail(f"Couldn't extract position from {args}")
#             case catchall:
#                 self.fail(f"Unrecognized structure: {catchall}")

#     def test_player_moves_to_the_right_when_pressed(self) -> None:
#         player = Player(WorldVector(starting_x:=1, 0))
#         level = Level(walls=[], orbs=[])
#         presenter = mock.create_autospec(Presenter)
#         scene = FightScene(presenter, player, level)
#         user_input = UserInput(right=True, delta_time=timedelta(seconds=1))
        
#         scene.update(user_input)

#         self.assertGreater(new_x:=self._player_position_from_mock(presenter.draw).x, starting_x)

#         scene.update(user_input)

#         self.assertGreater(self._player_position_from_mock(presenter.draw).x, new_x)


# if __name__ == "__main__":
#     main()