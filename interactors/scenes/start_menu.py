from interactors.scene import Scene, Presenter, UserInput, StopGame, SceneSwitch, SceneChoice
from interactors.presenter_model import StartButton, QuitButton


def _is_start_button_hovered(user_input: UserInput) -> bool:
    return id(StartButton) in user_input.selected_ids
def _is_start_button_clicked(user_input: UserInput) -> bool:
    return _is_start_button_hovered(user_input) and user_input.confirm

def _is_quit_button_hovered(user_input: UserInput) -> bool:
    return id(QuitButton) in user_input.selected_ids
def _is_quit_button_clicked(user_input: UserInput) -> bool:
    return _is_quit_button_hovered(user_input) and user_input.confirm


class StartMenu(Scene):
    def __init__(self, presenter: Presenter):
        self._presenter = presenter
        
    def update(self, user_input: UserInput) -> None:
        
        if _is_quit_button_clicked(user_input):
            raise StopGame
        elif _is_start_button_clicked(user_input):
            raise SceneSwitch(SceneChoice.FIGHT)
        
        self._presenter.draw([
            StartButton(id(StartButton), highlight=_is_start_button_hovered(user_input)),
            QuitButton(id(QuitButton), highlight=_is_quit_button_hovered(user_input))
        ])

