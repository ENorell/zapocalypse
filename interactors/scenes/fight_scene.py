import math

from domain.model import WorldVector, Level
from interactors.interactors import Scene, Presenter, UserInput, WorldPresenterModel, WorldGraphic


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
            WorldPresenterModel(id(player), graphic=WorldGraphic.PLAYER, position=player.position),
            *(
                WorldPresenterModel(id(wall), graphic=WorldGraphic.WALL, position=wall.position)
                for wall in self.level.get_walls()
            ),
            *(
                WorldPresenterModel(id(orb), graphic=WorldGraphic.ORB, position=orb.position)
                for orb in self.level.get_orbs()
            )
        ])
        
