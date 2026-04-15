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


from domain.spell import *

# How? needs to be created before state machine??
#def make_start_game_system() -> Callable[[UserInput], Effect[Context]]: #switch_state: Callable[[str], None]
def start_game_system(user_input: UserInput, _: World) -> None:
    if _is_start_button_clicked(user_input):
        raise SceneSwitch(SceneChoice.FIGHT)
    #return start_game_system

def quit_game_system(user_input: UserInput, _: World) -> None:
    if _is_quit_button_clicked(user_input):
        raise StopGame

#System = Callable[[UserInput, Context], None]

class StartGameSystem:
    @staticmethod
    def update(user_input: UserInput, _: World) -> None:
        if _is_start_button_clicked(user_input):
            raise SceneSwitch(SceneChoice.FIGHT)

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

# def make_start_menu_presenter(presenter: Presenter) -> Callable[[UserInput, Context], None]:
#     def start_menu_presenter(user_input: UserInput, _: Context) -> None:
#         presenter.draw([
#             StartButton(id(StartButton), highlight=_is_start_button_hovered(user_input)),
#             QuitButton(id(QuitButton), highlight=_is_quit_button_hovered(user_input))
#         ])
#     return start_menu_presenter


def create_start_menu_scene(context: World, presenter) -> Scene:
    return Scene(
        context,
        StartGameSystem(),
        QuitGameSystem(),
        DrawStartMenuSystem(presenter)
    )

