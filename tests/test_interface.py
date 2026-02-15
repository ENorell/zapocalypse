from datetime import timedelta
from unittest import TestCase, mock, main
from pathlib import Path

from interactors.interactors import SceneChoice, Scene, SceneSwitch, UserInput
from interface.state_machine import StateMachine
from domain.model import WorldVector
from interface.pixel.presenter import PixelPresenter, PixelVector, Assets, UiGraphic, UiAssetModel, WorldGraphic, \
    WorldAssetModel, ImageAsset, RGB, BoxAsset, Text, UiPresenterModel, RenderModel, WorldPresenterModel



class TestPresenter(TestCase):
    def test_finds_correct_ui_asset(self) -> None:
        presenter = PixelPresenter(
            screen_size=PixelVector(800, 600),
            assets=Assets(
                world={WorldGraphic.PLAYER: WorldAssetModel(ImageAsset(file=Path("assets/wizard.png"), size=PixelVector(100, 100)))},
                ui={UiGraphic.START_GAME_BUTTON: UiAssetModel(BoxAsset(size=PixelVector(100, 20), color=RGB(0,255,0), text=Text("Start Game")), position=PixelVector(80,60))}
            ),
        )

        presenter.draw([UiPresenterModel(id=0, graphic=UiGraphic.START_GAME_BUTTON)])

        self.assertEqual(
            presenter.render_models,
            [RenderModel(
                id=0,
                position=PixelVector(80, 60),
                asset=BoxAsset(size=PixelVector(100, 20), color=RGB(0, 255, 0), text=Text("Start Game")),
                rotation=0
            )]
        )

    def test_finds_correct_world_asset(self) -> None:
        presenter = PixelPresenter(
            screen_size=PixelVector(800, 600),
            assets=Assets(world={
                WorldGraphic.PLAYER: WorldAssetModel(ImageAsset(file=Path("assets/wizard.png"), size=PixelVector(100, 100)))
            }),
        )

        presenter.draw([WorldPresenterModel(id=0, graphic=WorldGraphic.PLAYER, position=WorldVector(1, 0))])

        self.assertEqual(
            presenter.render_models,
            [RenderModel(
                id=0,
                position=PixelVector(100, 0),
                asset=ImageAsset(file=Path("assets/wizard.png"), size=PixelVector(100, 100)),
                rotation=0
            )]
        )


class TestStateMachine(TestCase):
    def test_can_switch_between_states(self) -> None:
        from_state = mock.Mock(update=mock.Mock(side_effect=SceneSwitch(SceneChoice.FIGHT)))
        to_state = mock.create_autospec(Scene)
        state_machine = StateMachine(
            {
                SceneChoice.START_MENU: from_state,
                SceneChoice.FIGHT: to_state,
            },
            SceneChoice.START_MENU
        )
        
        state_machine.update(UserInput(delta_time=timedelta()))

        from_state.cleanup.assert_called_once()
        self.assertEqual(state_machine.scene, to_state)
        to_state.start.assert_called_once()
        


if __name__ == "__main__":
    main()
