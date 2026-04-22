from interactors.scene import Scene, Presenter, UserInput, StopGame, SceneSwitch, SceneChoice
from interactors.presenter_model import StartButton, QuitButton
from domain.spell import *


def _is_start_button_hovered(user_input: UserInput) -> bool:
    return id(StartButton) in user_input.selected_ids
def _is_start_button_clicked(user_input: UserInput) -> bool:
    return _is_start_button_hovered(user_input) and user_input.confirm

class StartGameSystem:
    @staticmethod
    def update(user_input: UserInput, _: World) -> None:
        if _is_start_button_clicked(user_input):
            raise SceneSwitch(SceneChoice.FIGHT)


def _is_quit_button_hovered(user_input: UserInput) -> bool:
    return id(QuitButton) in user_input.selected_ids
def _is_quit_button_clicked(user_input: UserInput) -> bool:
    return _is_quit_button_hovered(user_input) and user_input.confirm

class QuitGameSystem:
    @staticmethod
    def update(user_input: UserInput, _: World) -> None:
        if _is_quit_button_clicked(user_input):
            raise StopGame


class DrawStartMenuSystem:
    def __init__(self, presenter: Presenter) -> None:
        self._presenter = presenter
    def update(self, user_input: UserInput, _) -> None:
        self._presenter.draw([
            StartButton(id(StartButton), highlight=_is_start_button_hovered(user_input)),
            QuitButton(id(QuitButton), highlight=_is_quit_button_hovered(user_input))
        ])


def create_start_menu_scene(context: World, presenter) -> Scene:
    return Scene(
        context,
        StartGameSystem(),
        QuitGameSystem(),
        DrawStartMenuSystem(presenter)
    )

