from enum import Enum, auto
from typing import Protocol
from domain.model import WorldVector
import math

# class Camera(Protocol):
#     def get_camera_offset(self) -> WorldVector:
#             ...

class CameraRotation(Enum):
    left = auto()
    right = auto()

class CenterPlayerCamera():
    def __init__(self, screen_size: WorldVector):
        self.screen_size = screen_size
        self.rotation_angle = 0.0

    # def set_player_position(self, player_position: WorldVector) -> WorldVector:
    #     self.player_position = player_position

    # def rotate_camera(self, rotation: CameraRotation):
    #     if rotation == CameraRotation.left:
    #         self.rotation_angle = (self.rotation_angle + 1) % 360
    #     if rotation == CameraRotation.right:
    #         self.rotation_angle = (self.rotation_angle - 1) % 360

    def get_camera_offset(self, player_position: WorldVector) -> WorldVector:
        world_center_x = self.screen_size.x / 2
        world_center_y = self.screen_size.y / 2

        offset_x = player_position.x - world_center_x
        offset_y = player_position.y - world_center_y

        rad = math.radians(self.rotation_angle)
        rotated_x = offset_x * math.cos(rad) - offset_y * math.sin(rad)
        rotated_y = offset_x * math.sin(rad) + offset_y * math.cos(rad)

        return WorldVector(
            rotated_x,
            rotated_y
        )
    
    # def apply_rotation(self, world_position: WorldVector, camera_offset: WorldVector) -> WorldVector:
    #     """Rotate a world position around the player"""
    #     # position relative to player
    #     rel_x = world_position.x - (camera_offset.x + self.screen_size.x / 2)
    #     rel_y = world_position.y - (camera_offset.y + self.screen_size.y / 2)

    #     rad = math.radians(self.rotation_angle)
    #     rotated_x = rel_x * math.cos(rad) - rel_y * math.sin(rad)
    #     rotated_y = rel_x * math.sin(rad) + rel_y * math.cos(rad)

    #     # back to world coordinates
    #     rotated_world_x = rotated_x + (camera_offset.x + self.screen_size.x / 2)
    #     rotated_world_y = rotated_y + (camera_offset.y + self.screen_size.y / 2)

    #     return WorldVector(rotated_world_x, rotated_world_y)
    
# class LockCamera():
#     def __init__(self, screen_size: WorldVector):
#         self.screen_size = screen_size
        
#     def get_camera_offset(self) -> WorldVector:
#         ...
    
# class CameraSwitcher:
#     def __init__(self, cameras: list[Camera], default_camera: Camera = CenterPlayerCamera):
#         self._cameras = cameras
#         self._current_camera = default_camera

#     @property
#     def current_camera(self):
#         return self._current_camera
    
#     @property
#     def all_cameras(self):
#         return self._cameras

    # def switch_camera(self) -> None:
    #     cameras = self.all_cameras
    #     current_index = cameras.index(self._current_camera)
    #     next_index = (current_index + 1) % len(cameras)
    #     self._current_camera = cameras[next_index]