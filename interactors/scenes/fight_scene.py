from typing import Callable
from datetime import timedelta
import random

from domain.model import WorldVector, Level, Player, move, Element
from domain.spell import spell_list, World, create_run_command, Effect, create_fireball_spell
from interactors.presenter_model import PlayerModel, WallModel, OrbModel, OrbSlots, PresenterModel, ProjectileModel
from interactors.scene import Scene, Presenter, UserInput


class DrawFightSystem:
    def __init__(self, presenter: Presenter) -> None:
        self._presenter = presenter
        
    def update(self, _: UserInput, context: World) -> None:
        # Probably user input will be needed for presenting eventually
        projectile_models: list[PresenterModel] = [
            ProjectileModel(id(projectile), position=projectile.position)
            for projectile in context.projectiles
        ]
        wall_models: list[PresenterModel] = [
            WallModel(id(wall), wall_type=wall.wall_type, position=wall.position)
            for wall in context.level.walls
        ]
        orb_models: list[PresenterModel] = [
            OrbModel(id(orb), element=orb.element, position=orb.position)
            for orb in context.level.orbs
        ]
        self._presenter.draw([
            PlayerModel(id(context.player), position=context.player.position),
            *wall_models,
            *orb_models,
            *projectile_models,
            OrbSlots(context.player.elements)
        ])


class MoveSystem: # PlayerControlSystem? One per player?
    @staticmethod
    def update(user_input: UserInput, context: World) -> None:
        move_direction: Callable[[UserInput], WorldVector] = lambda i: WorldVector(i.right - i.left, i.down - i.up)
        frame_duration: Callable[[UserInput], timedelta] = lambda i: i.delta_time
        command = create_run_command(move_direction(user_input), frame_duration(user_input))
        command.apply(context)


class ProjectileSystem:
    @staticmethod
    def _is_outside_world(position: WorldVector) -> bool: # Rudimentary logic to clean up projectiles
        x, y, _ = position
        return abs(x) > 100 or abs(y) > 100

    @staticmethod
    def update(user_input: UserInput, world: World) -> None:
        for projectile in world.projectiles:
            projectile.fly(user_input.delta_time)

            if ProjectileSystem._is_outside_world(projectile.position):
                world.projectiles.remove(projectile)
                del projectile


class SpawnOrbSystem:  # Generalize?
    def __init__(self):
        self._spawn_timer: Callable[[timedelta], bool] = self._repeatable_timer(3.0)  # Inject or instantiate?
        self._position_selector = lambda _: WorldVector(random.randint(1, 10), random.randint(1, 10))
        self._element_selector = lambda _: random.choice(list(Element))

    def update(self, user_input: UserInput, context: World) -> None:
        if not self._spawn_timer(user_input.delta_time):
            return
        position = self._position_selector(context)
        element = self._element_selector(context)
        context.level.spawn_orb(1.0)

    @staticmethod
    def _repeatable_timer(frequency: float) -> Callable[[timedelta], bool]:
        time_counted = 0.0  # make timedelta everywhere?
        def is_triggered(tick_time: timedelta) -> bool:
            nonlocal time_counted
            time_counted += tick_time.total_seconds()
            if time_counted > frequency:
                time_counted -= frequency
                return True
            return False
        return is_triggered


class SpellSystem:
    def __init__(self):
        self._cast_spell_input: Callable[[UserInput], bool] = lambda i: i.confirm

    def update(self, user_input: UserInput, context: World) -> None:
        if not self._cast_spell_input(user_input):
            return
        spell = self._conjure_spell(user_input, context)
        spell.apply(context)

    @staticmethod
    def _conjure_spell(user_input: UserInput, context: World) -> Effect[World]:  # Optional[Spell]:
        for cost, make_spell in spell_list:
            spell = make_spell(user_input.cursor_position)
            if not cost.check(context.player): continue
            # if not spell.precondition.check(player): continue
            cost.apply(context.player)
            return spell
        else:
            return create_fireball_spell(user_input.cursor_position) # NoEffect() #


def spawn_starting_orbs(state: Scene) -> None:
    for _ in range(5):
        state._context.level.spawn_orb(1)


def create_fight_scene(context: World, presenter: Presenter) -> Scene:
    return Scene(
        context,
        MoveSystem(),
        SpawnOrbSystem(),
        ProjectileSystem(),
        SpellSystem(),
        DrawFightSystem(presenter),
        start=spawn_starting_orbs
    )

