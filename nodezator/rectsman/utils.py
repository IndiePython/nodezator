""""""

### standard library import
from itertools import permutations


### third-party import
from pygame.math import Vector2


### local import
from .constants import ENDPOINTS_ATTR_NAMES


def get_minimum_distance_function(rect):

    def get_lowest_distance(another_rect):

        return min(

            Vector2(
                getattr(rect, attr_a)
            ).distance_to(
                getattr(another_rect, attr_b)
            )

            for attr_a, attr_b in permutations(ENDPOINTS_ATTR_NAMES, 2)

        )

    return get_lowest_distance


def get_relative_point(rect_a, point_a, rect_b):

    ###

    if not rect_a.collidepoint(point_a):
        return ValueError("'point_a' must collide with 'rect_a'")

    ###

    topleft = Vector2(rect_a.topleft)

    dx = topleft.distance_to((point_a[0], topleft[1]))
    dy = topleft.distance_to((topleft[0], point_a[1]))

    width_proportion = dx / rect_a.width
    height_proportion = dy / rect_a.height

    ###

    left, top, width, height = rect_b

    topleft.update((left, top))

    point_b = topleft + (
        width * width_proportion,
        height * height_proportion
    )

    return point_b
