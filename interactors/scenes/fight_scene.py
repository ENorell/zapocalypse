import math
from typing import Optional


from domain.model import WorldVector, Level, Player, move
from interactors.presenter_model import PlayerModel, WallModel, OrbModel, OrbSlots, PresenterModel
from interactors.scene import Scene, Presenter, UserInput

# 
# def _get_move_target(player: Player, user_input: UserInput) -> Optional[WorldVector]:
#     x = user_input.right - user_input.left
#     y = user_input.down - user_input.up
#     magnitude = math.hypot(x, y)
#     distance = player.get_speed() * user_input.delta_time.total_seconds()
#     if not distance or not magnitude:
#         return None
#     
#     return WorldVector(
#         player.position.x + x * distance / magnitude,
#         player.position.y + y * distance / magnitude,
#         player.position.z
#     )
# 
# 
# class FightScene(Scene):
#     def __init__(self, presenter: Presenter, player: Player, level: Level):
#         self._presenter = presenter
#         self._level = level
#         self._player = player
# 
#     def start(self) -> None:
#         for _ in range(5):
#             self._level.spawn_orb(1)
# 
#     def update(self, user_input: UserInput) -> None:
#         if move_target := _get_move_target(self._player, user_input):
#             move(self._player, move_target, self._level)
# 
#         self._presenter.draw([
#             PlayerModel(id(self._player), position=self._player.position),
#             *self._get_level_presenter_models(),
#             OrbSlots(self._player.elements)
#         ])
#         
#     def _get_level_presenter_models(self) -> list[PresenterModel]:
#         wall_models: list[PresenterModel] = [
#             WallModel(id(wall), wall_type=wall.wall_type, position=wall.position)
#             for wall in self._level.walls
#         ]
#         orb_models: list[PresenterModel] = [
#             OrbModel(id(orb), element=orb.element, position=orb.position)
#             for orb in self._level.orbs
#         ]
#         return wall_models + orb_models



from domain.spell import *


# class PresentFight:
#     def __init__(self, presenter) -> None:
#         self._presenter = presenter
# 
#     def apply(self, context: Context) -> None:
#         self._presenter.draw([
#             PlayerModel(id(context._player), position=context._player.position),
#             *self._get_level_presenter_models(),
#             OrbSlots(context._player.elements)
#         ])
# 
#     def _get_level_presenter_models(self) -> list[PresenterModel]:
#         wall_models: list[PresenterModel] = [
#             WallModel(id(wall), wall_type=wall.wall_type, position=wall.position)
#             for wall in self._level.walls
#         ]
#         orb_models: list[PresenterModel] = [
#             OrbModel(id(orb), element=orb.element, position=orb.position)
#             for orb in self._level.orbs
#         ]
#         return wall_models + orb_models


# def make_fight_presenter(presenter: Presenter) -> Callable[[UserInput, Context], None]:
#     #present_fight = PresentFight(presenter)
#     def fight_presenter_system(_: UserInput, context: Context) -> None:
#         # Probably input will be needed for presenting eventually
#         # effect = lambda context: draw_walls(context)
#         # presenter.draw(models)
#         wall_models: list[PresenterModel] = [
#             WallModel(id(wall), wall_type=wall.wall_type, position=wall.position)
#             for wall in context.walls
#         ]
#         orb_models: list[PresenterModel] = [
#             OrbModel(id(orb), element=orb.element, position=orb.position)
#             for orb in context.orbs
#         ]
#         presenter.draw([
#             PlayerModel(id(context._player), position=context._player.position),
#             *wall_models,
#             *orb_models,
#             OrbSlots(context._player.elements)
#         ])
# 
#     return fight_presenter_system


class DrawFightSystem:
    def __init__(self, presenter: Presenter) -> None:
        self._presenter = presenter
        
    def update(self, _: UserInput, context: World) -> None:
        # Probably user input will be needed for presenting eventually

        wall_models: list[PresenterModel] = [
            WallModel(id(wall), wall_type=wall.wall_type, position=wall.position)
            for wall in context.level.walls
        ]
        orb_models: list[PresenterModel] = [
            OrbModel(id(orb), element=orb.element, position=orb.position)
            for orb in context.level.orbs
        ]
        self._presenter.draw([
            PlayerModel(id(context.caster), position=context.caster.position),
            *wall_models,
            *orb_models,
            OrbSlots(context.caster.elements)
        ])


class MoveSystem:
    @staticmethod
    def update(user_input: UserInput, context: World) -> None:
        move_direction: Callable[[UserInput], WorldVector] = lambda i: WorldVector(i.right - i.left, i.down - i.up)
        frame_duration: Callable[[UserInput], timedelta] = lambda i: i.delta_time
        command = create_run_command(move_direction(user_input), frame_duration(user_input))
        command.apply(context)

def spawn_starting_orbs(state: Scene) -> None:
        for _ in range(5):
            state._context.level.spawn_orb(1)

def create_fight_scene(context: World, presenter: Presenter) -> Scene:
    return Scene(
        context,
        #make_move_system(),
        #make_orb_system(),
        #make_spell_system(),
        MoveSystem(),
        DrawFightSystem(presenter),#make_fight_presenter(presenter)
        start=spawn_starting_orbs
    )

