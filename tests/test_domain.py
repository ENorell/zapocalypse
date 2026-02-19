from unittest import TestCase
from datetime import timedelta

from domain.model import Player, WorldVector, Wall, Level, ElementOrb, Element, Physics, FireBall, Move


class TestCollisions(TestCase):
    # def test_can_move_next_to_wall(self) -> None:
    #     player = Player(WorldVector(1, 1))
    #     wall = Wall(WorldVector(2, 1))
        
    #     world = Level(player, [wall], [])
        
    #     world.push_player(WorldVector(0, 1), distance=1)
    #     self.assertEqual(player.position, (1, 2))
        
    # def test_no_collision(self) -> None:
    #     player = Player(WorldVector(1, 1))
    #     wall = Wall(WorldVector(2, 1))
    #     physics = Physics([wall], player)
        
    #     delta_time = timedelta(seconds=1)
    #     direction = WorldVector(1, 0)
        
    #     target = player.get_run_target(direction, delta_time)
    #     self.assertFalse(physics.has_collision(target))
    #     player.move_to(target)
    
    # def test_move_command(self):
    #     player = Player(WorldVector(1, 1))
    #     wall = Wall(WorldVector(2, 1))
        
    #     with Move(player, WorldVector(1,0), timedelta(seconds=1)) as cmd:
    #         if not cmd.collides_with(wall): cmd.execute()
            
    #     cmd = Move(player, WorldVector(1,0), timedelta(seconds=1))
    #     if not cmd.collides_with(wall): cmd.execute()
            
    #     if cmd:=Move(player, WorldVector(1,0), timedelta(seconds=1)) and not cmd.collides_with(wall):
    #         cmd.execute()
        

    # def test_cant_move_into_wall(self) -> None:
    #     player = Player(WorldVector(1.1,1))
    #     wall = Wall(WorldVector(2,1))

    #     world = Level(player, [wall], [])

    #     world.push_player(WorldVector(1, 0), distance=1)
    #     self.assertEqual(player.position, (1.1,1))
        

    # def test_pick_up_orb(self) -> None:
    #     player = Player(WorldVector(0, 0))
    #     world = Level(player, [], orbs=[ElementOrb(Element.WIND, WorldVector(1, 0))])
    #     world.push_player(WorldVector(1, 0), distance=1)
        
    #     self.assertTrue(world.can_pickup_orb())
    #     world.do_pickup_orb()

    #     self.assertIn(Element.WIND, player._elements)
    #     self.assertNotIn(Element.WIND, world._orbs)
        
        def test_spawn_orb_unique_position(self) -> None:
            world = Level(None, [], [])
            for _ in range(4):
                world.spawn_orb_in_free_position(1, 1)

            self.assertEqual(len(world._orbs), 4)

            # with self.assertRaises(ValueError):
            #     world.spawn_orb_in_free_position(0, 0)
        
# class TestSpells(TestCase):
#     def test_cast_spell(self):
#         player = Player(WorldVector(1.1, 1))
#         wall = Wall(WorldVector(2, 1))
        
#         spell = FireBall()
        
#         cast(spell, player)