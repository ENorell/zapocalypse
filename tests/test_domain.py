from unittest import TestCase
from datetime import timedelta

from domain.model import Player, WorldVector, Wall, Level, ElementOrb, Element, FireStorm, move, conjure_spell, MoveType, Tile, TileType, DefaultTraversalRule, NoTraverseTraversalRule, MoveTypeTraversalRule, NoTraversalEffect
import domain.events as events


class TestCollisions(TestCase):
    def test_can_move_next_to_wall(self) -> None:
        player = Player(WorldVector(1, 1))
        level = Level([Wall(WorldVector(2, 1))])

        move(player, WorldVector(1, 2), level)

        self.assertNotIn(events.Collision(), player.events)
        self.assertEqual(player.position, (1, 2))

    def test_wall_collision(self) -> None:
        player = Player(WorldVector(0, 0))
        level = Level(walls=[Wall(target := WorldVector(1, 0))])

        move(player, target, level)

        self.assertIn(events.Collision(), player.events)
        self.assertEqual(player.position, WorldVector(0, 0))


class TestPickupOrb(TestCase):
    def test_orb_pickup(self) -> None:
        player = Player(WorldVector(0, 0))
        level = Level(walls=[], orbs=[ElementOrb(Element.WIND, target:=WorldVector(1, 0))])
        
        move(player, target, level)

        self.assertIn(events.OrbPickup(), player.events)
        self.assertIn(Element.WIND, player._elements)
        

class TestSpells(TestCase):
    def test_create_spell(self):
        elements = [Element.WIND, Element.WIND, Element.FIRE]
        
        self.assertIsInstance(
            conjure_spell(elements),
            FireStorm
        )
    
class TestTraverseTile(TestCase):
    def setUp(self):
        self.player = Player(WorldVector(1, 1), move_types=[MoveType.DEFAULT])
        self.level = Level(
            [],
            [Tile(TileType.GRASS, WorldVector(1, 3), DefaultTraversalRule(), NoTraversalEffect()),
            Tile(TileType.WALL, WorldVector(1, 4), NoTraverseTraversalRule(), NoTraversalEffect()),
            Tile(TileType.FIRE, WorldVector(1, 5), MoveTypeTraversalRule({MoveType.FLY}), NoTraversalEffect()),
            Tile(TileType.WATER, WorldVector(1, 6), MoveTypeTraversalRule({MoveType.SWIM, MoveType.FLY}), NoTraversalEffect())]
        )

    def test_grass_collision(self):
        move(self.player, WorldVector(1, 3), self.level)
        self.assertNotIn(events.Collision(), self.player.events)
        self.player.events.clear()

    def test_wall_collision(self):
        move(self.player, WorldVector(1, 4), self.level)
        self.assertIn(events.Collision(), self.player.events)
        self.player.events.clear()

    def test_fly_tile(self):
        self.player.add_move_type(MoveType.FLY)
        move(self.player, WorldVector(1, 5), self.level)
        self.assertNotIn(events.Collision(), self.player.events)
        self.player.events.clear()

    def test_walk_tile_collision(self):
        self.player.add_move_type(MoveType.WALK)
        move(self.player, WorldVector(1, 6), self.level)
        self.assertIn(events.Collision(), self.player.events)
        self.player.events.clear()