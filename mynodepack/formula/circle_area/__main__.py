
### standard library import
from math import pi


def get_circle_area(radius:float=1.0) -> [{'name': 'circle_area', 'type': float}]:
    return pi * (radius **2)

main_callable = get_circle_area
