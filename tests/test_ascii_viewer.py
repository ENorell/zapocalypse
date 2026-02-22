import unittest
import unittest.mock as mock
from datetime import timedelta

from interface.ascii.controller import AsciiController, DeviceEvent
from interface.ascii.presenter import AsciiPresenter, ConsoleVector, Assets, UiAssetModel, UiGraphic, UiPresenterModel
from interactors.scenes.start_menu import StartMenu
from interactors.scene import UserInput


class TestStartMenu(unittest.TestCase):
    def test_ascii_render_start_menu(self):
        presenter = AsciiPresenter(
            console_size=ConsoleVector(5,5),
            assets=Assets(
                ui={
                    UiGraphic.START_GAME_BUTTON: UiAssetModel("S", ConsoleVector(3, 2)),
                    UiGraphic.QUIT_GAME_BUTTON: UiAssetModel("Q", ConsoleVector(3, 4)),
                }
            ),
        )
        scene = StartMenu(presenter)
        
        scene.update(UserInput(delta_time=timedelta()))

        self.assertEqual(
            presenter.render_model.frame,
            "+ + + + +\n"
            "+ + S + +\n"
            "+ + + + +\n"
            "+ + Q + +\n"
            "+ + + + +"
        )

    def test_controller_selection(self) -> None:
        scene = mock.Mock()
        controller = AsciiController(scene)
        
        controller.update(DeviceEvent(entity_ids=[1, 2], right_key=True, delta_time=timedelta()))
        scene.update.assert_called_with(UserInput(selected_ids=[1], right=True, delta_time=timedelta()))

        controller.update(DeviceEvent(entity_ids=[1, 2], right_key=True, delta_time=timedelta()))
        scene.update.assert_called_with(UserInput(selected_ids=[2], right=True, delta_time=timedelta()))

        controller.update(DeviceEvent(entity_ids=[1, 2], right_key=True, delta_time=timedelta()))
        scene.update.assert_called_with(UserInput(selected_ids=[1], right=True, delta_time=timedelta()))


    def test_render_selected(self) -> None:
        presenter = AsciiPresenter(
            console_size=ConsoleVector(5, 5),
            assets=Assets(
                ui={
                    UiGraphic.START_GAME_BUTTON: UiAssetModel("S", ConsoleVector(3, 2)),
                    UiGraphic.QUIT_GAME_BUTTON: UiAssetModel("Q", ConsoleVector(3, 4)),
                }
            ),
        )
        
        presenter.draw([
            UiPresenterModel(id=1, graphic=UiGraphic.START_GAME_BUTTON, to_highlight=True),
            UiPresenterModel(id=2, graphic=UiGraphic.QUIT_GAME_BUTTON)
        ])

        self.assertEqual(
            presenter.render_model.frame,
            "+ + + + +\n"
            "+ > S + +\n"
            "+ + + + +\n"
            "+ + Q + +\n"
            "+ + + + +"
        )


if __name__ == "__main__":
    unittest.main()
