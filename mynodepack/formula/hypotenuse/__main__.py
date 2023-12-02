
### standard library import
from math import sqrt


def get_hypotenuse(leg1:float=3.0, leg2:float=4.0) -> [{'name': 'hypotenuse', 'type': float}]:
    return sqrt(
        (leg1**2) + (leg2**2)
    )

main_callable = get_hypotenuse