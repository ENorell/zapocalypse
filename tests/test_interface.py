from datetime import timedelta
from unittest import TestCase, mock, main
from pathlib import Path

from domain.model import WorldVector, Element
from interactors.scene import SceneChoice, Scene, SceneSwitch, UserInput
from interactors.presenter_model import OrbSlots, StartButton, QuitButton, PlayerModel
from interface.state_machine import StateMachine
from interface.pixel.presenter import PixelPresenter, PixelVector
from interface.pixel.render_model import ImageAsset, RGB, BoxAsset, CircleAsset, Text, RenderModel
from interface.pixel.asset_config import Graphic


class TestPresenter(TestCase):
    def test_finds_correct_ui_asset(self) -> None:
        presenter = PixelPresenter(
            screen_size=PixelVector(800, 600),
            assets={
                Graphic.PLAYER:ImageAsset(file=Path("assets/wizard.png"), size=PixelVector(100, 100)),
                Graphic.START_GAME_BUTTON: BoxAsset(size=PixelVector(100, 20), color=RGB(0,255,0), text=Text("Start Game")),
            }
        )

        presenter.draw([StartButton(id=0)])

        self.assertEqual(
            presenter.render_models,
            [RenderModel(
                id=0,
                position=PixelVector(100, 200),
                asset=BoxAsset(size=PixelVector(100, 20), color=RGB(0, 255, 0), text=Text("Start Game")),
                rotation=0
            )]
        )

    def test_finds_correct_world_asset(self) -> None:
        presenter = PixelPresenter(
            screen_size=PixelVector(800, 600),
            assets={
                Graphic.PLAYER: ImageAsset(file=Path("assets/wizard.png"), size=PixelVector(100, 100))
            },
        )

        presenter.draw([PlayerModel(id=0, position=WorldVector(1, 0))])

        self.assertEqual(
            presenter.render_models,
            [RenderModel(
                id=0,
                position=PixelVector(100, 0),
                asset=ImageAsset(file=Path("assets/wizard.png"), size=PixelVector(100, 100)),
                rotation=0
            )]
        )
        
    def test_start_quit_button_ui(self) -> None:
        presenter = PixelPresenter(
            screen_size=PixelVector(800, 600),
            assets={
                Graphic.START_GAME_BUTTON: BoxAsset(size=PixelVector(200, 100), color=RGB(0, 255, 0), text=Text("START")),
                Graphic.QUIT_GAME_BUTTON:  BoxAsset(size=PixelVector(200, 100), color=RGB(255, 0, 0), text=Text("QUIT")),
            },
        )

        presenter.draw([
            StartButton(id=0, highlight=True),
            QuitButton(id=1, highlight=False)
        ])

        self.assertEqual(
            presenter.render_models,
            [
                RenderModel(id=0, position=PixelVector(100, 200), asset=BoxAsset(size=PixelVector(200, 100), color=RGB(0, 255, 0), text=Text("START"))),
                RenderModel(id=1, position=PixelVector(100, 400), asset=BoxAsset(size=PixelVector(200, 100), color=RGB(255, 0, 0), text=Text("QUIT"))),
                ]
        )


    def test_orb_ui(self) -> None:
        presenter = PixelPresenter(
            screen_size=PixelVector(800, 600),
            assets={
                Graphic.FIRE_ORB_SLOT:       CircleAsset(radius=25, color=RGB(255,0,0)),
                Graphic.WATER_ORB_SLOT:      CircleAsset(radius=25, color=RGB(0,0,255)),
                Graphic.EMPTY_ORB_SLOT:      CircleAsset(radius=25, color=RGB(0,0,0)),
                Graphic.ORB_SLOT_BACKGROUND: BoxAsset(size=PixelVector(250, 50), color=RGB(0,255,255))
            },
        )

        presenter.draw([
            OrbSlots([Element.FIRE, Element.WATER, None])
        ])
        
        self.assertEqual(
            presenter.render_models,
    [
                RenderModel(position=PixelVector(500, 0),  asset=BoxAsset(size=PixelVector(250, 50), color=RGB(0, 255, 255))),
                RenderModel(position=PixelVector(550, 25), asset=CircleAsset(radius=25, color=RGB(255, 0, 0))),
                RenderModel(position=PixelVector(600, 25), asset=CircleAsset(radius=25, color=RGB(0, 0, 255))),
                RenderModel(position=PixelVector(650, 25), asset=CircleAsset(radius=25, color=RGB(0, 0, 0))),
            ]
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
