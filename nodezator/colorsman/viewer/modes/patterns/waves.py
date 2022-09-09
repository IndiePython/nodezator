"""Facility w/ function for waves pattern drawing."""

### standard library imports

from random import choice

from itertools import cycle


### local imports

from .....alphamask.main import AlphaMask

from .....surfsman.draw import draw_linear_gradient


### mask obtained from an image representing a wave
wave_mask = AlphaMask.from_image_name("mask_wave.png")

### store a rect the size of the mask
WAVE_RECT = wave_mask.get_rect()

### reference an operation to create colored wave surfaces
get_colored_wave = wave_mask.get_colored_surface


### main function


def draw_waves(canvas_surf, colors):
    """Draw waves of multiple colors.

    Parameters
    ==========
    canvas_surf (pygame.Surface instance)
        surface wherein to draw the waves pattern.
    colors (list whose items are sequences of integers)
        each item in this list represents a color and
        the integers, all in range(256), represent values
        for the red, green and blue channels of a color
        (a 4th integer may also be present representing
        the value of an alpha channel).
    """
    ### draw a gradient on the canvas surface

    draw_linear_gradient(
        canvas_surf,
        colors[0],
        start_percentage=0.125,
        stop_percentage=1,
        max_lightness_percentage=0.7,
        min_lightness_percentage=0.5,
        direction="left_to_right",
    )

    ### create a new list of colors where the items are
    ### converted into tuples
    color_tuples = [tuple(color) for color in colors]

    ### create a map which associates each color to a
    ### surface with a wave drawing of that color

    color_to_surf_map = {color: get_colored_wave(color) for color in color_tuples}

    ### create a list representing a population of colors
    ### depending on whether there are other colors beside
    ### the first one

    ## separate first color from the other ones
    first_color, *other_colors = color_tuples

    ## if there are other colors, create a new list
    ## representing a population of colors where each
    ## of the remaining colors is paired up with an
    ## instance of the first color

    if other_colors:

        color_population = []

        for color in other_colors:
            color_population.extend((first_color, color))

    ## otherwise the population is comprised of the first
    ## color alone
    else:
        color_population = [first_color]

    ### obtain a callable which returns the next color
    ### in the population cyclicly, each time it is executed
    next_color = cycle(color_population).__next__

    ### create objects/define values to use in the drawing
    ### loop

    ## obtain a rect for the canvas and extend its width
    ## by 20 pixels

    canvas_rect = canvas_surf.get_rect()
    canvas_rect.width += 20

    ## define a fixed x value from where to position the
    ## center of the wave horizontally whenever starting
    ## to blit the wave rect in the outer loop

    starting_centerx = (
        ## start from the canvas' left
        canvas_rect.left
        ## and add a random integer between 0 and a third
        ## of the wave's width
        + choice(range(0, (WAVE_RECT.width // 3) + 1))
    )

    ## align the top of the wave rect with the canvas' bottom
    ## bottom (as if the bottom was 30 pixels lower)
    WAVE_RECT.top = canvas_rect.move(0, 30).bottom

    ## lower the wave rect by a random amount within a small
    ## arbitrary range
    WAVE_RECT.y += choice(range(-20, -6))

    ## define a function to randomly pick an integer from
    ## a small arbitrary range
    random_increment = lambda: choice(range(-10, 11, 4))

    ## define a fixed offset used to align the wave after
    ## each blitting operation, so the pattern is drawn
    ## seamlessly as if wave was continuous
    pos_blit_offset = (0, -13)

    ### draw waves in the canvas gradually as you move the
    ### wave rect through the extension of the canvas from
    ### bottom to top and from left to right (diagonally),
    ### blitting the drawing in a fixed diagonal alignment
    ### that makes the waves' drawings appear continuous

    ## keep looping while the wave's bottom doesn't go
    ## above the canvas' top

    while WAVE_RECT.bottom > canvas_rect.top:

        ## backup the y coordinate of the wave
        initial_y = WAVE_RECT.y

        ## horizontally align the wave's center
        WAVE_RECT.centerx = starting_centerx

        ## randomize the horizontal position of the wave
        ## a bit
        WAVE_RECT.x += random_increment()

        ## grab the next color used to blit the waves
        wave_surf = color_to_surf_map[next_color()]

        ## keep looping while the wave's left doesn't go
        ## beyond the canvas' right, repositioning the
        ## wave relative to its own position after each
        ## blitting operation

        while WAVE_RECT.left < canvas_rect.right:

            # blit the wave
            canvas_surf.blit(wave_surf, WAVE_RECT)

            # align its midleft coordinates with its own
            # midright coordinates, with a fixed offset

            WAVE_RECT.midleft = WAVE_RECT.move(pos_blit_offset).midright

        ## realign the y coordinate of the wave with its
        ## initial own initial value, but 74 pixels higher
        ## (by subtracting the amount)
        WAVE_RECT.y = initial_y - 74
