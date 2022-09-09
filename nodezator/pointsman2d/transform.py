""""""

from math import sin, cos


def translate_points(points, delta):

    dx, dy = delta
    for x, y in points:
        yield (x + dx, y + dy)


def rotate_points(points, degrees=0, pivot=(0, 0)):

    xc, yc = pivot

    sin_value = sin(degrees)
    cos_value = cos(degrees)

    for x, y in points:

        yield (
            ((x - xc) * cos_value) - ((y - yc) * sin_value) + xc,
            ((x - xc) * sin_value) + ((y - yc) * cos_value) + yc,
        )
