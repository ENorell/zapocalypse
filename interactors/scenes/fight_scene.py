import math
from typing import Optional

from dataclasses import replace
from domain.spell import create_run_command, Context
from domain.model import Level, Player
from domain.spawning_system import *
from interactors.presenter_model import PlayerModel, WallModel, OrbModel, OrbSlots, PresenterModel, WorldPresenterModel
from interactors.scene import Scene, Presenter, UserInput
from interactors.camera import CenterPlayerCamera, CameraRotation

def _get_move_target(user_input: UserInput, context: Context) -> None | WorldVector:
    x = user_input.right - user_input.left
    y = user_input.down - user_input.up

    if x == 0 and y == 0:
        return None
    else:
        return WorldVector(x, y)
        
class FightScene(Scene):
    def __init__(self, presenter: Presenter, player: Player, level: Level, player_camera: CenterPlayerCamera):
        self._presenter = presenter
        self._level = level
        self._player = player
        self._camera = player_camera
        # self._camera_switcher = camera_switcher
        self._context = Context(self._player, self._level, [self._player])

    def start(self) -> None:
        orb_spawner = OrbSpawner(self._level)

        temp_spawn_positions = [
            WorldVector(self._player.position.x + x, self._player.position.y + y)
            for x in range(-1, 3)
            for y in range(-1, 3)
        ]

        level_spawn_positions = AnySpawnPositions(temp_spawn_positions)
        random_selector = RandomPositionSelector(level_spawn_positions)
        for i in range(8):
            orb_spawner.spawn_object(random_selector, random.choice(list(Element)))

        wall_spawner = WallSpawner(self._level)

        center_x = self._player.position.x
        center_y = self._player.position.y
        size = 4

        for x in range(center_x - size, center_x + size + 1):
            for y in range(center_y - size, center_y + size + 1):
                if x == center_x - size or x == center_x + size or y == center_y - size or y == center_y + size:
                    wall_spawner.spawn_object_at(WorldVector(x, y), WallType.STONE)

    def update(self, user_input: UserInput) -> None:
        
        moving_direction = _get_move_target(user_input, self._context)

        if moving_direction is not None:
            duration = user_input.delta_time
            run_effect = create_run_command(moving_direction, duration)
            run_effect.apply(self._context)

        camera_offset = self._camera.get_camera_offset(self._player.position)
        if user_input.rotate_camera_left:
            self._camera.rotate_camera(CameraRotation.left)
        elif user_input.rotate_camera_right:
            self._camera.rotate_camera(CameraRotation.right)

        self._presenter.draw([
            PlayerModel(id(self._player), position=self._player.position),
            *self._get_level_presenter_models(),
            OrbSlots(self._player.elements)],
            camera_offset
        )
        
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
