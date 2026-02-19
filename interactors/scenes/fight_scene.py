import math

from domain.model import WorldVector, Level, PickupOrb
from interactors.interactors import Scene, Presenter, UserInput, HUDPresenterModel, HUDGraphic, WorldPresenterModel, WorldGraphic, WorldGraphics


def input_direction(user_input: UserInput) -> WorldVector:
    x = user_input.right - user_input.left
    y = user_input.down - user_input.up
    magnitude = math.hypot(x,y)
    return magnitude and WorldVector(
        x/magnitude,
        y/magnitude,
    ) or WorldVector(0,0)

def _is_orb_hovered(user_input: UserInput) -> bool:
    return id(HUDGraphic.ORB_INVENTORY_SLOTS) in user_input.selected_ids

class FightScene(Scene):
    def __init__(self, presenter: Presenter, level: Level):
        self.level = level
        self._presenter = presenter

    # def create_hud(self) -> None:
    #     hud_backdrop = self.hu

    def start(self):
        for _ in range(8):
            self.level.spawn_orb_in_free_position(4,4)

    def update(self, user_input: UserInput) -> None:

        player = self.level.player
        orbs = self.level._orbs

        distance = player.get_speed() * user_input.delta_time.total_seconds()
        
        self.level.push_player(direction=input_direction(user_input), distance=distance)

        pick_up_orb = PickupOrb(player, orbs)
        pick_up_orb.execute()
        # if pickup_effect := self.level.can_pickup_orb():
        #     self.level.do_pickup_orb()

        self._presenter.draw([
            WorldPresenterModel(id(player), graphic=WorldGraphic.PLAYER, position=player.position),
            *(
                WorldPresenterModel(
                    id(wall), 
                    graphic=WorldGraphics.resolve_world_graphic(variant=wall.wall.name, fallback_world_graphic=WorldGraphic.WALL), 
                    position=wall.position)
                for wall in self.level.get_walls()
            ),
            *(
                WorldPresenterModel(
                    id(orb), 
                    graphic=WorldGraphics.resolve_world_graphic(variant=orb.element.name, fallback_world_graphic=WorldGraphic.ORB_ELEMENT), 
                    position=orb.position)
                for orb in self.level.get_orbs()
            ),
            HUDPresenterModel(id(HUDGraphic.ORB_INVENTORY_BACKDROP), HUDGraphic.ORB_INVENTORY_BACKDROP),
            HUDPresenterModel(id(HUDGraphic.ORB_INVENTORY_SLOT_ONE), HUDGraphic.ORB_INVENTORY_SLOT_ONE),
            HUDPresenterModel(id(HUDGraphic.ORB_INVENTORY_SLOT_TWO), HUDGraphic.ORB_INVENTORY_SLOT_TWO),
            HUDPresenterModel(id(HUDGraphic.ORB_INVENTORY_SLOT_THREE), HUDGraphic.ORB_INVENTORY_SLOT_THREE)
        ])
        
