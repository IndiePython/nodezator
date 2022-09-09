"""Facility w/ functions for particles pattern drawing."""

### standard library imports

from random import sample, choice

from functools import partial


### third-party imports

from pygame import Surface

from pygame.math import Vector2


### local imports

from .....surfsman.draw import draw_linear_gradient

from .....surfsman.icon import render_layered_icon


### constant: standard distance between two points in
### the canvas, in both x and y axes
POINT_DISTANCE = 20


### utility functions

## operation to get a colored particle surface given the
## color and height


def get_colored_particle_surf(icon_ordinal, height, color):
    """Return surface representing colored character.

    Works just like a partial implementation of the
    render_layered_icon() function.

    Parameters
    ==========
    icon_ordinal (integer)
        integers representing character used as particle
        to be drawn.
    height (positive integer)
        height of surface in pixels.
    color (sequence of integers)
        represents the color of the particle in the
        surface; integers represent values of RGB channels
        respectively and are all in range(256).
    """
    return render_layered_icon(
        chars=[chr(icon_ordinal)],
        dimension_name="height",
        dimension_value=height,
        colors=[color],
    )


## function to return an integer representing a random
## distance in pixels to move from a given location;
## we use half the standard point distance, so that two
## offset points can never reach each other

min_value = (POINT_DISTANCE // 2) * -1
max_value = POINT_DISTANCE // 2

random_distance = lambda: choice(range(min_value, max_value + 1))


## function to return population with arithmetically
## increased number of items


def increase_item_count(a_list, step=1):
    """Return list w/ arithmetically increased count of items.

    Parameters
    ==========

    a_list (list)
        list with items to be arithmetically increased.
    step (positive integers)
        constant by which to increase the item count
        arithmetically.

    Doctests
    ========

    >>> increase_item_count([10, 20, 30])
    [10, 20, 20, 30, 30, 30]
    >>> increase_item_count([10, 20, 30], 2)
    [10, 20, 20, 20, 30, 30, 30, 30, 30]
    """
    ### create a list to store a new population of items
    item_population = []

    ### define a range from 1 to the original number of
    ### items times the step, plus 1;
    ###
    ### such integers represent increasing item counts

    start = 1
    stop = (len(a_list) * step) + 1

    item_counts = range(start, stop, step)

    ### now iterate pairs formed by the items and
    ### item_counts, extending the population by a new
    ### list containing that item n times, where n is the
    ### item count

    for item, item_count in zip(a_list, item_counts):
        item_population.extend([item] * item_count)

    ### finally return the new list
    return item_population


### main function


def draw_particles(icon_ordinal, heights, canvas_surf, colors):
    """Draw particles of varying sizes, colors and locations.

    Parameters
    ==========
    icon_ordinal (integer)
        integer representing character used as particle
        to be drawn.
    heights (list with 3 integers)
        height values to use for the particles.
    canvas_surf (pygame.Surface instance)
        surface wherein to draw the particles pattern.
    colors (list whose items are sequences of integers)
        each item in this list represents a color and
        the integers, all in range(256), represent values
        for the red, green and blue channels of a color
        (a 4th integer may also be present representing
        the value of an alpha channel).
    """
    ### draw a gradient on the canvas

    draw_linear_gradient(
        canvas_surf,
        colors[0],
        start_percentage=0.125,
        stop_percentage=1,
        max_lightness_percentage=0.7,
        min_lightness_percentage=0.5,
        direction="left_to_right",
    )

    ### obtain a new color list from the given one, in which
    ### the items are turned into tuples
    colors = [tuple(color) for color in colors]

    ### create a nested dict whose keys are heights which
    ### point to another dicts whose keys are colors which
    ### point to particle surfaces of that color and height

    height_to_colors = {
        ## keys of this dictionary are the different heights
        ## of particle surfaces
        height: {
            ## such height keys point to inner dictionaries
            ## where keys are tuple instances representing a
            ## color which points to particle surfaces filled
            ## with that color and the height which points to
            ## this dict
            color: get_colored_particle_surf(icon_ordinal, height, color)
            ## the inner dict is built by iterating over the
            ## colors
            for color in colors
        }
        ## the outer dict is built by iterating over the
        ## heights
        for height in heights
    }

    ### calculate all spots (points) in a rect larger than
    ### the canvas which are distant from each other by the
    ### POINT_DISTANCE and offset by a random distance

    ## obtain the canvas rect
    canvas_rect = canvas_surf.get_rect()

    ## make a copy from it, inflated in both dimensions
    ## by 4 times the point distance

    larger_rect = canvas_rect.inflate(POINT_DISTANCE * 4, POINT_DISTANCE * 4)

    ## finally align the center of the larger/inflated rect
    ## with the center from the canvas rect
    larger_rect.center = canvas_rect.center

    ## obtain the range from one boundary to another in
    ## both x and y axes

    x_range = range(larger_rect.left, larger_rect.right, POINT_DISTANCE)

    y_range = range(larger_rect.top, larger_rect.bottom, POINT_DISTANCE)

    ## finally store all points in a list, offsetting the
    ## actual x and y values by a random distance

    all_spots = [
        (x + random_distance(), y + random_distance()) for x in x_range for y in y_range
    ]

    ### calculate spots (points) in a new medium area within
    ### the canvas, align to the canvas' midright, which
    ### occupies 2/3 of the canvas' width and is even
    ### further deflated by the POINT_DISTANCE in both
    ### dimensions;
    ###
    ### such spots are obtained from the list containing
    ### all spots, but only the ones within the radius
    ### formed between the center of the new area and its
    ### topright coordinate

    ## copy canvas rect
    medium_area = canvas_rect.copy()

    ## perform size transformations

    medium_area.width //= 3
    medium_area.width *= 2

    medium_area.inflate_ip(-POINT_DISTANCE, -POINT_DISTANCE)

    ## align its midright coordinates to the canvas'
    ## midright coordianates
    medium_area.midright = canvas_rect.midright

    ## obtain a 2d vector from the area's center and also
    ## calculate its distance to the topright coordinates

    center = Vector2(medium_area.center)
    radius = center.distance_to(medium_area.topright)

    ## then create the new list of spots from the list with
    ## all spots, only using points within the radius
    ## previously obtained

    less_spots = [spot for spot in all_spots if center.distance_to(spot) <= radius]

    ### calculate spots (points) in an even smaller area
    ### this time within the previously created area;
    ###
    ### such spots are obtained from the list containing
    ### all spots, but only the ones within the radius
    ### formed between the center of this new area and its
    ### topright coordinate, just like we did in the
    ### previous area

    ## obtain a copy of the medium area deflated to half
    ## its size

    small_area = medium_area.inflate(
        tuple((dimension // 2) * -1 for dimension in medium_area.size)
    )

    ## obtain a 2d vector from the area's center and also
    ## calculate its distance to the topright coordinates

    center = Vector2(small_area.center)
    radius = center.distance_to(small_area.topright)

    ## then create the new list of spots from the list with
    ## all spots, only using points within the radius
    ## previously obtained

    even_less_spots = [spot for spot in all_spots if center.distance_to(spot) <= radius]

    ### separate the first color from the remaining ones
    first_color, *other_colors = colors

    ### obtain a new function which returns the next
    ### color to use from the given colors;
    ###
    ### how this function works will depend on whether
    ### there are other colors besides the first one

    ## if there are other colors, we make a new function
    ## so that it randomly returns a new color from a list
    ## of colors which has the colors from the original
    ## list of colors repeated in different proportions,
    ## the first colors being more in higher number than
    ## the last ones

    if other_colors:

        ## obtain a list representing a population of
        ## colors with colors repeating themselves in
        ## different proportions;
        ##
        ## note that we pass the colors in reverse order
        ## to the function, because this way the first
        ## colors, now at the end of the list, will be
        ## repeated more times; once the function returns,
        ## we reverse it again so the original first colors
        ## appear back at the beginning
        color_population = increase_item_count(colors[::-1])[::-1]

        ## finally, create the function which picks a
        ## color from the population at almost at
        ## random, because we changed the quantity of the
        ## colors so the first colors will have a higher
        ## chance of being picked
        next_color = lambda: choice(color_population)

    ## otherwise the function keeps returning the first
    ## color (since it is the only color)
    else:
        next_color = lambda: first_color

    ### for each pair of height/list of spots, draw
    ### particles of that height in varied colors on the
    ### spots sampled from the given ones
    ###
    ### this promotes the illusion of depth because the
    ### larger particles are always blitted over the smaller
    ### ones, making the larger ones appear closer to the
    ### screen

    for height, spots in zip(heights, (all_spots, less_spots, even_less_spots)):

        ## reference the dict with particle surfaces for
        ## each color locally, all surfaces being of the
        ## specified height
        color_to_surfs = height_to_colors[height]

        ## sample the given spots proportionally to their
        ## quantity
        spot_samples = sample(spots, len(spots) // 10)

        ## iterate over the sampled spots, retrieving a
        ## particle surface of the next given color each
        ## time, blitting the surface on that spot in the
        ## canvas

        for spot in spot_samples:

            particle_surf = color_to_surfs[next_color()]

            canvas_surf.blit(particle_surf, spot)

    ### uncomment lines below to draw visual representations
    ### of the different areas in the canvas surface
    ### represented by medium_area and small_area
    ###
    ### from pygame.draw import rect as draw_rect
    ### draw_rect(canvas_surf, (255,)*3, medium_area, 2)
    ### draw_rect(canvas_surf, (255,)*3, small_area,  2)


### partial implementation of the draw_particles function

draw_circles = partial(draw_particles, 101, [18, 26, 34])
