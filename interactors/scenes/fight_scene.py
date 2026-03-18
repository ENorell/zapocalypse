import math
from typing import Optional


from domain.model import WorldVector, Level, Player, move
from domain.spawning_system import OrbSpawner
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
        player.position.y + y * distance / magnitude
    )


class FightScene(Scene):
    def __init__(self, presenter: Presenter, player: Player, level: Level):
        self._presenter = presenter
        self._level = level
        self._player = player

    def start(self) -> None:
        spawner = OrbSpawner(self._level)
        spawner.spawn_object()
        spawner.spawn_object()


    def update(self, user_input: UserInput) -> None:
        if move_target := _get_move_target(self._player, user_input):
            move(self._player, move_target, self._level)

        self._presenter.draw([
            PlayerModel(id(self._player), position=self._player.position),
            *self._get_level_presenter_models(),
            OrbSlots(self._player.elements)
        ])
        
    def _get_level_presenter_models(self) -> list[PresenterModel]:
        wall_models: list[PresenterModel] = [
            WallModel(id(wall), wall_type=wall.wall_type, position=wall.position)
            for wall in self._level.walls
        ]
        orb_models: list[PresenterModel] = [
            OrbModel(id(orb), element=orb.element, position=orb.position)
            for orb in self._level.orbs
        ]
        return wall_models + orb_models
