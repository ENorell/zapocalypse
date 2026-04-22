from unittest import TestCase
from datetime import timedelta

from domain.model import Player, WorldVector, Wall, Level, ElementOrb, Element, move
from domain.spell import conjure_spell
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
        player = Player(WorldVector(0,0), elements)
        
        self.assertIsInstance(
            conjure_spell(player),
            FireStorm
        )

    def test_cast_spell(self):
        player = Player(WorldVector(0, 0))
        level = Level(walls=[], orbs=[])
        spell = FireBall(player)

        spell.apply(level)

        self.assertIn(events.CastedSpell(), player.events)
        self.assertIn(Projectile(WorldVector(0, 0)), level.projectiles)