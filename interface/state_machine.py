from interactors.interactors import SceneChoice, Scene, UserInput, StopGame, SceneSwitch


class StateMachine:
    """Handles switching and activation of different states"""
    def __init__(self, scenes: dict[SceneChoice, Scene], start_scene: SceneChoice) -> None:
        self.scenes: dict[SceneChoice, Scene] = scenes
        self.scene: Scene = self.scenes[start_scene]
        self.is_running = True

    def switch_scene(self, next_state: SceneChoice) -> None:
        self.scene.cleanup()
        self.scene = self.scenes[next_state]
        self.scene.start()

    def update(self, user_input: UserInput) -> None:
        try:
            self.scene.update(user_input)
        except StopGame:
            self.is_running = False
        except SceneSwitch as scene_switch:
            self.switch_scene(scene_switch.scene)
