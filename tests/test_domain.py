from unittest import TestCase
from datetime import timedelta
import random

from domain.spawning_system import OrbSpawner, AnySpawnPositions, RandomPositionSelector, TileSpawner, WallSpawner
from domain.model import WorldVector, Level, Wall, WallType, ElementOrb, Element, Tile, TileType
from domain.spell import Spell, Context, AnyResult, CasterPlayerTarget, AllOrbs, AllWalls, ExactNumber, Conditional, \
    ElementOrbTarget, ElementOrbPositionTarget, IsMovableCondition, DisplaceEffect, NoEffect, MoveDestinationTarget, \
    Target, CasterPositionTarget, PlayerRunSpeed, \
    Effect, RootedEffect, DotEffect, HealEffect, EqualDurationDotTicker, Number, ExactNumber, MoveType, MoveType, Player, \
    create_run_command, conjure_spell  \

import domain.events as events


class TestCollisions(TestCase):
    def setUp(self):
        self.player = Player(WorldVector(1, 1), [])
        self.level = Level()
        self.wall_spawner = WallSpawner(self.level)
        self.context = Context(self.player, self.level, [self.player])

    def test_can_move_next_to_wall(self) -> None:
        
        self.wall_spawner.spawn_object_at(WorldVector(2, 2), WallType.STONE)

        time = timedelta(seconds=4)
        seconds = time.total_seconds()
        run_speed = PlayerRunSpeed(CasterPlayerTarget()).evaluate(self.context)
        distance = seconds * run_speed
        
        run = create_run_command(WorldVector(1, 0), time)
        run.apply(self.context)
        
        # self.assertNotIn(events.Collision(), self.player.events)
        self.assertEqual(self.player.position, WorldVector(1 + distance, 1))

    # def test_wall_collision(self) -> None:
    #     self.wall_spawner.spawn_object_at(WorldVector(2, 1), WallType.STONE)

    #     # target = CasterPositionTarget()
    #     # target_player = CasterPlayerTarget()
    #     # target_position = MoveDestinationTarget(target, WorldVector(1, 0), timedelta(seconds=1), PlayerRunSpeed(target_player))
    #     # expected_position = target_position.resolve(self.context)
    #     run = create_run_command(WorldVector(1, 0), timedelta(seconds=1))
    #     run.apply(self.context)

    #     # self.assertIn(events.Collision(), self.player.events)
    #     self.assertEqual(self.player.position, WorldVector(1, 1))


# class TestPickupOrb(TestCase):
#     def test_orb_pickup(self) -> None:
#         player = Player(WorldVector(2, 3), [])
#         level = Level()
#         orb_spawner = OrbSpawner(level)
#         orb_spawner.spawn_object_at(WorldVector(3,3), Element.WIND)
#         context = Context(player, level, [])
        
#         run_effect = create_run_command(WorldVector(4, 0), timedelta(seconds=10))
#         run_effect.apply(context)

#         # self.assertIn(events.OrbPickup(), player.events)
#         self.assertIn(Element.WIND, player._elements)
        

class TestSpells(TestCase):
    def test_create_spell(self):
        elements = [Element.FIRE, Element.FIRE, Element.WIND]
        player = Player(WorldVector(0,0), elements)
        
        self.assertIsInstance(
            conjure_spell(player), Spell
        )


class TestSpawnOrb(TestCase):
    def test_spawn_orb(self) -> None:
        level = Level()
        orb_spawner = OrbSpawner(level)

        position = WorldVector(3, 3)
        element = Element.FIRE

        orb_spawner.spawn_object_at(position, element)

        self.assertTrue(
            any(
                orb.position == position and orb.element == element
                for orb in level.orbs
            )
        )

class TestSpawnOrbRandom(TestCase):
    def test_spawn_orb(self) -> None:
        level = Level()
        orb_spawner = OrbSpawner(level)

        temp_spawn_positions = [
            WorldVector(x, y)
            for x in range(-1, 1)
            for y in range(-1, 1)
        ]

        level_spawn_positions = AnySpawnPositions(temp_spawn_positions)
        random_selector = RandomPositionSelector(level_spawn_positions)

        element = random.choice(list(Element))

        orb_spawner.spawn_object(random_selector, element)

        orb = level.orbs[0]
        self.assertEqual(len(level.orbs), 1)
        self.assertIn(orb.position, temp_spawn_positions)
        self.assertEqual(orb.element, element)


class TestPlayerMove(TestCase):
    def test_run(self) -> None:
        self.player = Player(WorldVector(2, 3), [])
        self.level = Level()
        self.players = [self.player]

        self.context  = Context(caster = self.player, level = self.level, players = self.players)

        direction = WorldVector(1, 1)
        duration = timedelta(seconds=1)

        run_effect = create_run_command(direction, duration)
        run_effect.apply(self.context)

        expected_position = CasterPlayerTarget().resolve(self.context).position
        self.assertEqual(self.player.position, expected_position)

class TestOrbMove(TestCase):

    def test_move_orb(self) -> None:
        self.level = Level()
        self.player = Player(WorldVector(0, 0), [])
        self.orb_spawner = OrbSpawner(self.level)

        position = WorldVector(3.0, 3.0)
        element = Element.FIRE
        self.orb_spawner.spawn_object_at(position, element)
        self.context = Context(caster = self.player, level=self.level, players=[])

        print(self.level.orbs)
                
        direction = WorldVector(1, 1)
        orb_target = ElementOrbTarget(WorldVector(3.0, 3.0))
        destination_target = MoveDestinationTarget(
                    origin=ElementOrbPositionTarget(orb_target),
                    direction=direction,
                    duration=timedelta(seconds=1),
                    speed=ExactNumber(5.0)
                )
        
        destination = destination_target.resolve(self.context)

        Conditional(
            AnyResult(orb_target),
            on_pass=
                Conditional(
                    IsMovableCondition(orb_target), 
                    on_pass=
                        DisplaceEffect(orb_target, destination_target),
                    on_fail=
                        NoEffect()
                ),
            on_fail=NoEffect()  
        ).apply(self.context)

        orb = self.level.orbs[0]
        self.assertEqual(orb.position, destination)

class test_dot_effect(TestCase):
    def setUp(self):
        self.level = Level()
        self.player = Player(WorldVector(0, 0), [])
        self.context = Context(caster = self.player, level=self.level, players=[])
        self.dot_effect = DotEffect(
            effect=HealEffect(CasterPlayerTarget(), ExactNumber(5)),
            ticker=EqualDurationDotTicker(ExactNumber(5.0),ExactNumber(2))
        )

    def test_add_dot_effect(self):

        self.player.add_dot_effect(self.dot_effect)

        self.assertIn(self.dot_effect, self.player._active_effects)

    def test_heal_dot_effect(self):
        self.player.take_damage(20)

        self.player.add_dot_effect(self.dot_effect)

        for delta_time in range(13):
            for effect in list(self.player._active_effects):
                effect.update(timedelta(seconds=delta_time), self.context)

        self.assertEqual(self.player.health, 90)








# class TestTraverseTile(TestCase):
#     def traverse_tile(self) -> None:
#         self.level = Level()
#         self.player = Player(WorldVector(3,3), [], 100)

#         tile_spawner = TileSpawner(self.level)
#         tile_spawner.spawn_object_at(WorldVector(3,4), Tile(TileType.FIRE), on_traverse_effects=[RootedEffect])

        
        