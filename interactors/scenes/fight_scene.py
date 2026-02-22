import math

from domain.model import WorldVector, Level
from interactors.presenter_model import PlayerModel, WallModel, OrbModel, OrbSlots
from interactors.scene import Scene, Presenter, UserInput


def input_direction(user_input: UserInput) -> WorldVector:
    x = user_input.right - user_input.left
    y = user_input.down - user_input.up
    magnitude = math.hypot(x,y)
    return magnitude and WorldVector(
        x/magnitude,
        y/magnitude,
    ) or WorldVector(0,0)


class FightScene(Scene):
    def __init__(self, presenter: Presenter, world_repository: Level):
        self.level = world_repository
        self._presenter = presenter

    def update(self, user_input: UserInput) -> None:

        player = self.level.player
        distance = player.get_speed() * user_input.delta_time.total_seconds()
        
        self.level.push_player(direction=input_direction(user_input), distance=distance)
        if pickup_effect := self.level.can_pickup_orb():
            self.level.do_pickup_orb()

        self._presenter.draw([
            PlayerModel(id(player), position=player.position),
            *(
                WallModel(id(wall), position=wall.position)
                for wall in self.level.get_walls()
            ),
            *(
                OrbModel(id(orb), element=orb.element, position=orb.position)
                for orb in self.level.get_orbs()
            ),
            OrbSlots(list(player._elements))
        ])
        
