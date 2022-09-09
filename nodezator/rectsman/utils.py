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
            Vector2(getattr(rect, attr_a)).distance_to(getattr(another_rect, attr_b))
            for attr_a, attr_b in permutations(ENDPOINTS_ATTR_NAMES, 2)
        )

    return get_lowest_distance
