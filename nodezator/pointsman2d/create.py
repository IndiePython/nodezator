from math import pi, sin, cos


def get_circle_points(quantity, radius, center=(0, 0)):
    """"""
    xc, yc = center

    for k in range(quantity):

        value = (k * 2 * pi) / quantity

        x = radius * cos(value)
        y = radius * sin(value)

        yield (x + xc, y + yc)
