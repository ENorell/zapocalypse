from interactors.interactors import Scene, Presenter, UserInput, StopGame, SceneSwitch, SceneChoice, UiPresenterModel, UiGraphic


def _is_start_button_hovered(user_input: UserInput) -> bool:
    return id(UiGraphic.START_GAME_BUTTON) in user_input.selected_ids
def _is_start_button_clicked(user_input: UserInput) -> bool:
    return _is_start_button_hovered(user_input) and user_input.confirm

def _is_quit_button_hovered(user_input: UserInput) -> bool:
    return id(UiGraphic.QUIT_GAME_BUTTON) in user_input.selected_ids
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
            UiPresenterModel(id(UiGraphic.START_GAME_BUTTON), UiGraphic.START_GAME_BUTTON, _is_start_button_hovered(user_input)),
            UiPresenterModel(id(UiGraphic.QUIT_GAME_BUTTON), UiGraphic.QUIT_GAME_BUTTON, _is_quit_button_hovered(user_input))
        ])

