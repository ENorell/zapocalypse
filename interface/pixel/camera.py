from domain.model import WorldVector
from interface.pixel.render_model import PixelVector


def transform_world_to_pixel(world_coordinate: WorldVector) -> PixelVector:
    x, y = world_coordinate
    return PixelVector(round(x*100), round(y*100))


def transform_pixel_to_world(pixel_coordinate: PixelVector) -> WorldVector:
    x, y = pixel_coordinate
    return WorldVector(round(x/100), round(y/100))
