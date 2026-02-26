import math
from typing import Optional, Sequence


from domain.model import WorldVector, Level, Player, ElementOrb, Wall, move
from interactors.presenter_model import PlayerModel, WallModel, OrbModel, OrbSlots, PresenterModel
from interactors.scene import Scene, Presenter, UserInput


def _get_move_target(player: Player, user_input: UserInput) -> Optional[WorldVector]:
    x = user_input.right - user_input.left
    y = user_input.down - user_input.up
    magnitude = math.hypot(x, y)
    distance = player.get_speed() * user_input.delta_time.total_seconds()
    if not distance or not magnitude:
        return None
    
    return WorldVector(
        player.position.x + x * distance / magnitude,
        player.position.y + y * distance / magnitude,
        player.position.z
    )


class FightScene(Scene):
    def __init__(self, presenter: Presenter, player: Player, level: Level):
        self._presenter = presenter
        self._level = level
        self._player = player

    def start(self) -> None:
        for _ in range(5):
            self._level.spawn_orb(1)

    def update(self, user_input: UserInput) -> None:
        if move_target := _get_move_target(self._player, user_input):
            move(self._player, move_target, self._level)

        self._presenter.draw([
            PlayerModel(id(self._player), position=self._player.position),
            *self._get_level_presenter_models(),
            OrbSlots(self._player.elements)
        ])
        
    def _get_level_presenter_models(self) -> Sequence[PresenterModel]:
        wall_models = [
            WallModel(id(wall), wall_type=wall.wall_type, position=wall.position)
            for wall in self._level.walls
        ]
        orb_models = [
            OrbModel(id(orb), element=orb.element, position=orb.position)
            for orb in self._level.orbs
        ]
        return wall_models + orb_models
