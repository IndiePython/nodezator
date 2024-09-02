"""Facility with drawing functions for helping connect sockets.

Contains functions for injection and other useful objects.
"""

### standard library imports

from collections import deque

from itertools import chain


### third-party import

from pygame.transform import flip as flip_surface

from pygame.draw import (
    line as draw_line,
    circle as draw_circle,
)

from pygame.math import Vector2


### local imports

from ....config import IMAGES_DIR

from ....pygamesetup import SCREEN, SCREEN_RECT, blit_on_screen

from ....imagesman.cache import IMAGE_SURFS_DB

from ....surfsman.render import render_surface_from_svg_text

from ....textman.render import render_text

from ....svgutils import (
    get_circle_svg_text_from_radius,
    yield_transformed_svgs,
)

from ....userprefsman.validation import AVAILABLE_SOCKET_DETECTION_GRAPHICS

from ...socket.output import OutputSocket

from ..utils import clip_segment



### hand surfaces to assist in defining new connections

_open_hand_topleft = IMAGE_SURFS_DB['hand_open.png'][{'use_alpha': True}]

RELATIVE_POS_TO_OPEN_HAND = {
    (True, True): _open_hand_topleft,
    (False, True): flip_surface(_open_hand_topleft, True, False),
    (False, False): flip_surface(_open_hand_topleft, True, True),
    (True, False): flip_surface(_open_hand_topleft, False, True),
}

OPEN_HAND_TO_ITS_OPPOSITE = {
    surf: RELATIVE_POS_TO_OPEN_HAND[(*(not c for c in relative_pos),)]
    for relative_pos, surf in RELATIVE_POS_TO_OPEN_HAND.items()
}

_closed_hand_topleft = IMAGE_SURFS_DB['hand_closed.png'][{'use_alpha': True}]

RELATIVE_POS_TO_CLOSED_HAND = {
    (True, True): _closed_hand_topleft,
    (False, True): flip_surface(_closed_hand_topleft, True, False),
    (False, False): flip_surface(_closed_hand_topleft, True, True),
    (True, False): flip_surface(_closed_hand_topleft, False, True),
}

CLOSED_HAND_TO_ITS_OPPOSITE = {
    surf: RELATIVE_POS_TO_CLOSED_HAND[(*(not c for c in relative_pos),)]
    for relative_pos, surf in RELATIVE_POS_TO_CLOSED_HAND.items()
}

RELATIVE_POS_TO_CLOSED_HAND_OFFSET = {
    key: (5 if key[0] else -5, 5 if key[1] else -5)
    for key in RELATIVE_POS_TO_CLOSED_HAND
}

### rect
HAND_RECT = _open_hand_topleft.get_rect()

### baseball

## glove

_baseball_glove_topleft = IMAGE_SURFS_DB['baseball_glove.png'][{'use_alpha': True}]

RELATIVE_POS_TO_BASEBALL_GLOVE = {
    (True, True): _baseball_glove_topleft,
    (False, True): flip_surface(_baseball_glove_topleft, True, False),
    (False, False): flip_surface(_baseball_glove_topleft, True, True),
    (True, False): flip_surface(_baseball_glove_topleft, False, True),
}

## ball

_baseball_svg_text = (IMAGES_DIR / 'baseball.svg').read_text(encoding='utf-8')

_baseball = render_surface_from_svg_text(_baseball_svg_text).convert_alpha()
BASEBALL_RECT = _baseball.get_rect()

_cx, _cy = (d/2 for d in BASEBALL_RECT.size)

_values = tuple(f'{angle} {_cx} {_cy}' for angle in range(30, 360, 30))

_baseball_surfs = (_baseball,) + tuple(

    render_surface_from_svg_text(svg_text).convert_alpha()

    for svg_text in yield_transformed_svgs(
        _baseball_svg_text,
        'shapes',
        tuple(('rotate', value) for value in _values),
    )

)

BASEBALL_SURFS_DEQUE = deque(
    chain.from_iterable(
        (surf,) * 2
        for surf in _baseball_surfs
    )
)


### eyes

OPEN_WHITE = render_surface_from_svg_text(

    get_circle_svg_text_from_radius(
        12,
        fill_color='white',
        outline_color='black',
        outline_width=2,
    )

).convert_alpha()

EYE_RECT = OPEN_WHITE.get_rect()


OPEN_PUPIL = render_surface_from_svg_text(

    get_circle_svg_text_from_radius(
        6,
        fill_color='black',
    )

).convert_alpha()

OPEN_PUPIL_RECT = OPEN_PUPIL.get_rect()

_pupil_closed = render_text(
    text='0', font_height=32, foreground_color=(0, 0, 0)
)

_br = _pupil_closed.get_bounding_rect()
_o = _pupil_closed.subsurface(_br)
w, h = _o.get_size()
CLOSED_PUPIL = _o.subsurface((0, 0, w, h//2))
CLOSED_PUPIL_RECT = CLOSED_PUPIL.get_rect()

### clear references
del _open_hand_topleft, _closed_hand_topleft

###

QUADRANT_KWARGS_MAP = {
    False: {'draw_top_left': True, 'draw_bottom_left': True},
    True: {'draw_top_right': True, 'draw_bottom_right': True},
}


def draw_temp_segment_with_assisting_line(self):
    """Draw temporary segment to visually assist in connecting sockets.

    This draws a line from 'socket a' (the socket from where the line
    segment will be defined) to the cursor.

    If there's a nearby compatible socket, we also draw a line from the
    cursor to that socket or close to it (depending on how close it is).
    When this is the case, hand icons are drawn as well to indicate when
    the socket is close enough to establish a connection or not
    """
    ### reference values/objecs locally for quicker/easier access

    sa = self.socket_a

    sa_center = sa.rect.center

    mp = self.magnet_point

    ### try obtaining a segment between the center of socket a and the
    ### magnet point which is clipped to the screen

    try:
        start, end = clip_segment(sa_center, mp)

    ### if we don't success, just pass

    except ValueError:
        pass

    ### otherwise, draw the temporary line

    else:

        sbc = self.socket_b_candidate
        sb = self.socket_b


        if sbc:

            sbc_center = sbc.rect.center

            ## lines

            draw_line(SCREEN, sa.line_color, start, mp, 3)

            midpoint = Vector2(sbc_center).lerp(mp, self.percentage_to_mouse)

            draw_line(SCREEN, sbc.line_color, sbc_center, midpoint, 3)

        ### if there's a socket b, we draw an outline around
        ### it as well (where the magnet point is located),
        ### then draw the temporary line;
        ###
        ### we always use the color of the socket which is
        ### the output socket;

        elif sb:

            is_output_socket = isinstance(sb, OutputSocket)

            color = (

                sb.line_color
                if is_output_socket

                else sa.line_color

            )

            sb_center = sb.rect.center

            draw_circle(
                SCREEN,
                color,
                sb_center,
                12,
                2,
                **QUADRANT_KWARGS_MAP[is_output_socket],
            )

            ######################################

            draw_line(SCREEN, color, start, mp, 3)
            draw_line(SCREEN, color, mp, sb_center, 3)

        ### if there's no socket b, though, we just draw a line,
        ### using the color of socket a

        else:
            draw_line(SCREEN, sa.line_color, start, end, 3)

def draw_temp_segment_with_reaching_hands(self):
    """Draw temporary segment to visually assist in connecting sockets.

    This draws a line from 'socket a' (the socket from where the line
    segment will be defined) to the cursor.

    If there's a nearby compatible socket, we also draw a line from the
    cursor to that socket or close to it (depending on how close it is).
    When this is the case, hand icons are drawn as well to indicate when
    the socket is close enough to establish a connection or not
    """
    ### reference values/objecs locally for quicker/easier access

    sa = self.socket_a

    sa_center = sa.rect.center

    mp = self.magnet_point

    ### try obtaining a segment between the center of socket a and the
    ### magnet point which is clipped to the screen

    try:
        start, end = clip_segment(sa_center, mp)

    ### if we don't success, just pass

    except ValueError:
        pass

    ### otherwise, draw the temporary line

    else:

        sbc = self.socket_b_candidate
        sb = self.socket_b


        if sbc:

            ##
            sbc_center = sbc.rect.center

            ## lines

            draw_line(SCREEN, sa.line_color, start, mp, 3)

            midpoint = Vector2(sbc_center).lerp(mp, self.percentage_to_mouse)

            draw_line(SCREEN, sbc.line_color, sbc_center, midpoint, 3)

            ## hand from socket

            open_hand_surf = RELATIVE_POS_TO_OPEN_HAND[

                (
                    mp[0] < sbc_center[0],
                    mp[1] < sbc_center[1],
                )

            ]

            HAND_RECT.center = midpoint

            blit_on_screen(open_hand_surf, HAND_RECT)

            ### hand near mouse

            opposite_hand = OPEN_HAND_TO_ITS_OPPOSITE[open_hand_surf]

            HAND_RECT.center = mp
            blit_on_screen(opposite_hand, HAND_RECT)

        ### if there's a socket b, we draw an outline around
        ### it as well (where the magnet point is located),
        ### then draw the temporary line;
        ###
        ### we always use the color of the socket which is
        ### the output socket;

        elif sb:

            ###

            is_output_socket = isinstance(sb, OutputSocket)

            color = (

                sb.line_color
                if is_output_socket

                else sa.line_color

            )

            ###
            sb_center = sb.rect.center
            ###

            draw_line(SCREEN, color, start, mp, 3)
            draw_line(SCREEN, color, mp, sb_center, 3)

            ### hand from socket

            rel_pos = (
                mp[0] < sb_center[0],
                mp[1] < sb_center[1],
            )

            closed_hand_surf = RELATIVE_POS_TO_CLOSED_HAND[rel_pos]

            HAND_RECT.center = mp + RELATIVE_POS_TO_CLOSED_HAND_OFFSET[rel_pos] 

            blit_on_screen(closed_hand_surf, HAND_RECT)

            ### hand near mouse

            opposite_hand = CLOSED_HAND_TO_ITS_OPPOSITE[closed_hand_surf]

            HAND_RECT.center = mp

            blit_on_screen(opposite_hand, HAND_RECT)

        ### if there's no socket b, though, we just draw a line,
        ### using the color of socket a

        else:

            draw_line(SCREEN, sa.line_color, start, end, 3)

            open_hand_surf = RELATIVE_POS_TO_OPEN_HAND[

                (
                    sa_center[0] < mp[0],
                    sa_center[1] < mp[1],
                )

            ]

            HAND_RECT.center = mp
            opposite_hand = OPEN_HAND_TO_ITS_OPPOSITE[open_hand_surf]
            blit_on_screen(opposite_hand, HAND_RECT)

def draw_temp_segment_with_hands_and_eyes(self):
    """Draw temporary segment to visually assist in connecting sockets.

    This draws a line from 'socket a' (the socket from where the line
    segment will be defined) to the cursor.

    If there's a nearby compatible socket, we also draw a line from the
    cursor to that socket or close to it (depending on how close it is).
    When this is the case, hand icons are drawn as well to indicate when
    the socket is close enough to establish a connection or not
    """
    ### reference values/objecs locally for quicker/easier access

    sa = self.socket_a

    sa_center = sa.rect.center

    mp = self.magnet_point

    ### try obtaining a segment between the center of socket a and the
    ### magnet point which is clipped to the screen

    try:
        start, end = clip_segment(sa_center, mp)

    ### if we don't success, just pass

    except ValueError:
        pass

    ### otherwise, draw the temporary line

    else:

        sbc = self.socket_b_candidate
        sb = self.socket_b


        if sbc:

            ### eyes

            eyes_midtop = sbc.node.rect.move(0, 6).midtop

            EYE_RECT.bottomright = eyes_midtop

            pupil_vec = Vector2(EYE_RECT.center)
            dist = pupil_vec.distance_to(mp)
            percentage = 5 / dist if dist > 5 else 1

            OPEN_PUPIL_RECT.center = pupil_vec.lerp(mp, percentage)

            blit_on_screen(OPEN_WHITE, EYE_RECT)
            blit_on_screen(OPEN_PUPIL, OPEN_PUPIL_RECT)

            EYE_RECT.bottomleft = eyes_midtop

            pupil_vec = Vector2(EYE_RECT.center)
            dist = pupil_vec.distance_to(mp)
            percentage = 5 / dist if dist > 5 else 1

            OPEN_PUPIL_RECT.center = pupil_vec.lerp(mp, percentage)
            blit_on_screen(OPEN_WHITE, EYE_RECT)
            blit_on_screen(OPEN_PUPIL, OPEN_PUPIL_RECT)

            if SCREEN_RECT.colliderect(sa.node.rect):

                eyes_midtop = sa.node.rect.move(0, 6).midtop

                EYE_RECT.bottomright = eyes_midtop

                pupil_vec = Vector2(EYE_RECT.center)
                dist = pupil_vec.distance_to(mp)
                percentage = 5 / dist if dist > 5 else 1

                OPEN_PUPIL_RECT.center = pupil_vec.lerp(mp, percentage)

                blit_on_screen(OPEN_WHITE, EYE_RECT)
                blit_on_screen(OPEN_PUPIL, OPEN_PUPIL_RECT)

                EYE_RECT.bottomleft = eyes_midtop

                pupil_vec = Vector2(EYE_RECT.center)
                dist = pupil_vec.distance_to(mp)
                percentage = 5 / dist if dist > 5 else 1

                OPEN_PUPIL_RECT.center = pupil_vec.lerp(mp, percentage)
                blit_on_screen(OPEN_WHITE, EYE_RECT)
                blit_on_screen(OPEN_PUPIL, OPEN_PUPIL_RECT)

            ##
            sbc_center = sbc.rect.center

            ## lines

            draw_line(SCREEN, sa.line_color, start, mp, 3)

            midpoint = Vector2(sbc_center).lerp(mp, self.percentage_to_mouse)

            draw_line(SCREEN, sbc.line_color, sbc_center, midpoint, 3)

            ## hand from socket

            open_hand_surf = RELATIVE_POS_TO_OPEN_HAND[

                (
                    mp[0] < sbc_center[0],
                    mp[1] < sbc_center[1],
                )

            ]

            HAND_RECT.center = midpoint

            blit_on_screen(open_hand_surf, HAND_RECT)

            ### hand near mouse

            opposite_hand = OPEN_HAND_TO_ITS_OPPOSITE[open_hand_surf]

            HAND_RECT.center = mp
            blit_on_screen(opposite_hand, HAND_RECT)

        ### if there's a socket b, we draw an outline around
        ### it as well (where the magnet point is located),
        ### then draw the temporary line;
        ###
        ### we always use the color of the socket which is
        ### the output socket;

        elif sb:

            ### eyes

            eyes_midtop = sb.node.rect.move(0, 6).midtop

            EYE_RECT.bottomright = eyes_midtop
            CLOSED_PUPIL_RECT.center = EYE_RECT.center

            blit_on_screen(OPEN_WHITE, EYE_RECT)
            blit_on_screen(CLOSED_PUPIL, CLOSED_PUPIL_RECT)

            EYE_RECT.bottomleft = eyes_midtop
            CLOSED_PUPIL_RECT.center = EYE_RECT.center

            blit_on_screen(OPEN_WHITE, EYE_RECT)
            blit_on_screen(CLOSED_PUPIL, CLOSED_PUPIL_RECT)

            if SCREEN_RECT.colliderect(sa.node.rect):

                eyes_midtop = sa.node.rect.move(0, 6).midtop

                EYE_RECT.bottomright = eyes_midtop
                CLOSED_PUPIL_RECT.center = EYE_RECT.center

                blit_on_screen(OPEN_WHITE, EYE_RECT)
                blit_on_screen(CLOSED_PUPIL, CLOSED_PUPIL_RECT)

                EYE_RECT.bottomleft = eyes_midtop
                CLOSED_PUPIL_RECT.center = EYE_RECT.center

                blit_on_screen(OPEN_WHITE, EYE_RECT)
                blit_on_screen(CLOSED_PUPIL, CLOSED_PUPIL_RECT)

            ###

            is_output_socket = isinstance(sb, OutputSocket)

            color = (

                sb.line_color
                if is_output_socket

                else sa.line_color

            )

            ###
            sb_center = sb.rect.center
            ###

            draw_line(SCREEN, color, start, mp, 3)
            draw_line(SCREEN, color, mp, sb_center, 3)

            ### hand from socket

            rel_pos = (
                mp[0] < sb_center[0],
                mp[1] < sb_center[1],
            )

            closed_hand_surf = RELATIVE_POS_TO_CLOSED_HAND[rel_pos]

            HAND_RECT.center = mp + RELATIVE_POS_TO_CLOSED_HAND_OFFSET[rel_pos] 

            blit_on_screen(closed_hand_surf, HAND_RECT)

            ### hand near mouse

            opposite_hand = CLOSED_HAND_TO_ITS_OPPOSITE[closed_hand_surf]

            HAND_RECT.center = mp

            blit_on_screen(opposite_hand, HAND_RECT)

        ### if there's no socket b, though, we just draw a line,
        ### using the color of socket a

        else:

            if SCREEN_RECT.colliderect(sa.node.rect):

                eyes_midtop = sa.node.rect.move(0, 6).midtop

                EYE_RECT.bottomright = eyes_midtop

                pupil_vec = Vector2(EYE_RECT.center)

                dist = pupil_vec.distance_to(mp)
                percentage = 5 / dist if dist > 5 else 1

                OPEN_PUPIL_RECT.center = pupil_vec.lerp(mp, percentage)

                blit_on_screen(OPEN_WHITE, EYE_RECT)
                blit_on_screen(OPEN_PUPIL, OPEN_PUPIL_RECT)

                EYE_RECT.bottomleft = eyes_midtop

                pupil_vec = Vector2(EYE_RECT.center)
                dist = pupil_vec.distance_to(mp)
                percentage = 5 / dist if dist > 5 else 1

                OPEN_PUPIL_RECT.center = pupil_vec.lerp(mp, percentage)
                blit_on_screen(OPEN_WHITE, EYE_RECT)
                blit_on_screen(OPEN_PUPIL, OPEN_PUPIL_RECT)

            draw_line(SCREEN, sa.line_color, start, end, 3)

            open_hand_surf = RELATIVE_POS_TO_OPEN_HAND[

                (
                    sa_center[0] < mp[0],
                    sa_center[1] < mp[1],
                )

            ]

            HAND_RECT.center = mp
            opposite_hand = OPEN_HAND_TO_ITS_OPPOSITE[open_hand_surf]
            blit_on_screen(opposite_hand, HAND_RECT)

def draw_temp_segment_with_baseball_elements(self):
    """Draw temporary segment to visually assist in connecting sockets.

    This draws a line from 'socket a' (the socket from where the line
    segment will be defined) to the cursor.

    If there's a nearby compatible socket, we also draw a line from the
    cursor to that socket or close to it (depending on how close it is).
    When this is the case, hand icons are drawn as well to indicate when
    the socket is close enough to establish a connection or not
    """
    ### reference values/objecs locally for quicker/easier access

    sa = self.socket_a

    sa_center = sa.rect.center

    mp = self.magnet_point

    ### try obtaining a segment between the center of socket a and the
    ### magnet point which is clipped to the screen

    try:
        start, end = clip_segment(sa_center, mp)

    ### if we don't success, just pass

    except ValueError:
        pass

    ### otherwise, draw the temporary line

    else:

        sbc = self.socket_b_candidate
        sb = self.socket_b


        if sbc:

            ##
            sbc_center = sbc.rect.center

            ## lines

            startv = Vector2(start)
            d = startv.distance_to(end)

            if d > 30:

                p = 30/d
                end = startv.lerp(end,p)

            draw_line(SCREEN, sa.line_color, start, end, 3)

            midpoint = Vector2(sbc_center).lerp(mp, self.percentage_to_mouse)

            draw_line(SCREEN, sbc.line_color, sbc_center, midpoint, 3)

            ## glove from socket

            baseball_glove_surf = RELATIVE_POS_TO_BASEBALL_GLOVE[

                (
                    mp[0] < sbc_center[0],
                    mp[1] < sbc_center[1],
                )

            ]

            HAND_RECT.center = midpoint

            blit_on_screen(baseball_glove_surf, HAND_RECT)

            ### ball

            BASEBALL_RECT.center = mp
            BASEBALL_SURFS_DEQUE.rotate(-1)
            blit_on_screen(BASEBALL_SURFS_DEQUE[0], BASEBALL_RECT)

            ### hand near mouse

            open_hand_surf = RELATIVE_POS_TO_OPEN_HAND[

                (
                    mp[0] < sa_center[0],
                    mp[1] < sa_center[1],
                )

            ]

            HAND_RECT.center = end
            blit_on_screen(open_hand_surf, HAND_RECT)

        ### if there's a socket b, we draw an outline around
        ### it as well (where the magnet point is located),
        ### then draw the temporary line;
        ###
        ### we always use the color of the socket which is
        ### the output socket;

        elif sb:

            ###

            is_output_socket = isinstance(sb, OutputSocket)

            color = (

                sb.line_color
                if is_output_socket

                else sa.line_color

            )

            ###
            sb_center = sb.rect.center

            ###

            startv = Vector2(start)
            d = startv.distance_to(end)

            if d > 30:

                p = 30/d
                end = startv.lerp(end,p)

            draw_line(SCREEN, color, start, end, 3)
            draw_line(SCREEN, color, mp, sb_center, 3)

            ## glove from socket

            rel_pos = (
                mp[0] < sb_center[0],
                mp[1] < sb_center[1],
            )

            baseball_glove_surf = RELATIVE_POS_TO_BASEBALL_GLOVE[rel_pos]

            HAND_RECT.center = mp

            blit_on_screen(baseball_glove_surf, HAND_RECT)

            ### ball

            BASEBALL_RECT.center = mp
            blit_on_screen(BASEBALL_SURFS_DEQUE[0], BASEBALL_RECT)

            ### hand from socket a

            open_hand_surf = RELATIVE_POS_TO_OPEN_HAND[

                (
                    mp[0] < sa_center[0],
                    mp[1] < sa_center[1],
                )

            ]

            HAND_RECT.center = end

            blit_on_screen(open_hand_surf, HAND_RECT)

        ### if there's no socket b, though, we just draw a line,
        ### using the color of socket a

        else:

            startv = Vector2(start)
            d = startv.distance_to(end)

            if d > 30:

                p = 30/d
                end = startv.lerp(end,p)

            draw_line(SCREEN, sa.line_color, start, end, 3)

            BASEBALL_RECT.center = mp
            BASEBALL_SURFS_DEQUE.rotate(-1)
            blit_on_screen(BASEBALL_SURFS_DEQUE[0], BASEBALL_RECT)

            open_hand_surf = RELATIVE_POS_TO_OPEN_HAND[

                (
                    sa_center[0] < mp[0],
                    sa_center[1] < mp[1],
                )

            ]

            HAND_RECT.center = end
            opposite_hand = OPEN_HAND_TO_ITS_OPPOSITE[open_hand_surf]
            blit_on_screen(opposite_hand, HAND_RECT)

def draw_temp_segment_with_baseball_elements_and_eyes(self):
    """Draw temporary segment to visually assist in connecting sockets.

    This draws a line from 'socket a' (the socket from where the line
    segment will be defined) to the cursor.

    If there's a nearby compatible socket, we also draw a line from the
    cursor to that socket or close to it (depending on how close it is).
    When this is the case, hand icons are drawn as well to indicate when
    the socket is close enough to establish a connection or not
    """
    ### reference values/objecs locally for quicker/easier access

    sa = self.socket_a

    sa_center = sa.rect.center

    mp = self.magnet_point

    ### try obtaining a segment between the center of socket a and the
    ### magnet point which is clipped to the screen

    try:
        start, end = clip_segment(sa_center, mp)

    ### if we don't success, just pass

    except ValueError:
        pass

    ### otherwise, draw the temporary line

    else:

        sbc = self.socket_b_candidate
        sb = self.socket_b


        if sbc:

            ### eyes

            eyes_midtop = sbc.node.rect.move(0, 6).midtop

            EYE_RECT.bottomright = eyes_midtop

            pupil_vec = Vector2(EYE_RECT.center)
            dist = pupil_vec.distance_to(mp)
            percentage = 5 / dist if dist > 5 else 1

            OPEN_PUPIL_RECT.center = pupil_vec.lerp(mp, percentage)

            blit_on_screen(OPEN_WHITE, EYE_RECT)
            blit_on_screen(OPEN_PUPIL, OPEN_PUPIL_RECT)

            EYE_RECT.bottomleft = eyes_midtop

            pupil_vec = Vector2(EYE_RECT.center)
            dist = pupil_vec.distance_to(mp)
            percentage = 5 / dist if dist > 5 else 1

            OPEN_PUPIL_RECT.center = pupil_vec.lerp(mp, percentage)
            blit_on_screen(OPEN_WHITE, EYE_RECT)
            blit_on_screen(OPEN_PUPIL, OPEN_PUPIL_RECT)

            if SCREEN_RECT.colliderect(sa.node.rect):

                eyes_midtop = sa.node.rect.move(0, 6).midtop

                EYE_RECT.bottomright = eyes_midtop

                pupil_vec = Vector2(EYE_RECT.center)
                dist = pupil_vec.distance_to(mp)
                percentage = 5 / dist if dist > 5 else 1

                OPEN_PUPIL_RECT.center = pupil_vec.lerp(mp, percentage)

                blit_on_screen(OPEN_WHITE, EYE_RECT)
                blit_on_screen(OPEN_PUPIL, OPEN_PUPIL_RECT)

                EYE_RECT.bottomleft = eyes_midtop

                pupil_vec = Vector2(EYE_RECT.center)
                dist = pupil_vec.distance_to(mp)
                percentage = 5 / dist if dist > 5 else 1

                OPEN_PUPIL_RECT.center = pupil_vec.lerp(mp, percentage)
                blit_on_screen(OPEN_WHITE, EYE_RECT)
                blit_on_screen(OPEN_PUPIL, OPEN_PUPIL_RECT)

            ##
            sbc_center = sbc.rect.center

            ## lines

            startv = Vector2(start)
            d = startv.distance_to(end)

            if d > 30:

                p = 30/d
                end = startv.lerp(end,p)

            draw_line(SCREEN, sa.line_color, start, end, 3)

            midpoint = Vector2(sbc_center).lerp(mp, self.percentage_to_mouse)

            draw_line(SCREEN, sbc.line_color, sbc_center, midpoint, 3)

            ## glove from socket

            baseball_glove_surf = RELATIVE_POS_TO_BASEBALL_GLOVE[

                (
                    mp[0] < sbc_center[0],
                    mp[1] < sbc_center[1],
                )

            ]

            HAND_RECT.center = midpoint

            blit_on_screen(baseball_glove_surf, HAND_RECT)

            ### ball

            BASEBALL_RECT.center = mp
            BASEBALL_SURFS_DEQUE.rotate(-1)
            blit_on_screen(BASEBALL_SURFS_DEQUE[0], BASEBALL_RECT)

            ### hand near mouse

            open_hand_surf = RELATIVE_POS_TO_OPEN_HAND[

                (
                    mp[0] < sa_center[0],
                    mp[1] < sa_center[1],
                )

            ]

            HAND_RECT.center = end
            blit_on_screen(open_hand_surf, HAND_RECT)

        ### if there's a socket b, we draw an outline around
        ### it as well (where the magnet point is located),
        ### then draw the temporary line;
        ###
        ### we always use the color of the socket which is
        ### the output socket;

        elif sb:

            ### eyes

            eyes_midtop = sb.node.rect.move(0, 6).midtop

            EYE_RECT.bottomright = eyes_midtop
            CLOSED_PUPIL_RECT.center = EYE_RECT.center

            blit_on_screen(OPEN_WHITE, EYE_RECT)
            blit_on_screen(CLOSED_PUPIL, CLOSED_PUPIL_RECT)

            EYE_RECT.bottomleft = eyes_midtop
            CLOSED_PUPIL_RECT.center = EYE_RECT.center

            blit_on_screen(OPEN_WHITE, EYE_RECT)
            blit_on_screen(CLOSED_PUPIL, CLOSED_PUPIL_RECT)

            if SCREEN_RECT.colliderect(sa.node.rect):

                eyes_midtop = sa.node.rect.move(0, 6).midtop

                EYE_RECT.bottomright = eyes_midtop
                CLOSED_PUPIL_RECT.center = EYE_RECT.center

                blit_on_screen(OPEN_WHITE, EYE_RECT)
                blit_on_screen(CLOSED_PUPIL, CLOSED_PUPIL_RECT)

                EYE_RECT.bottomleft = eyes_midtop
                CLOSED_PUPIL_RECT.center = EYE_RECT.center

                blit_on_screen(OPEN_WHITE, EYE_RECT)
                blit_on_screen(CLOSED_PUPIL, CLOSED_PUPIL_RECT)

            ###

            is_output_socket = isinstance(sb, OutputSocket)

            color = (

                sb.line_color
                if is_output_socket

                else sa.line_color

            )

            ###
            sb_center = sb.rect.center

            ###

            startv = Vector2(start)
            d = startv.distance_to(end)

            if d > 30:

                p = 30/d
                end = startv.lerp(end,p)

            draw_line(SCREEN, color, start, end, 3)
            draw_line(SCREEN, color, mp, sb_center, 3)

            ## glove from socket

            rel_pos = (
                mp[0] < sb_center[0],
                mp[1] < sb_center[1],
            )

            baseball_glove_surf = RELATIVE_POS_TO_BASEBALL_GLOVE[rel_pos]

            HAND_RECT.center = mp

            blit_on_screen(baseball_glove_surf, HAND_RECT)

            ### ball

            BASEBALL_RECT.center = mp
            blit_on_screen(BASEBALL_SURFS_DEQUE[0], BASEBALL_RECT)

            ### hand from socket a

            open_hand_surf = RELATIVE_POS_TO_OPEN_HAND[

                (
                    mp[0] < sa_center[0],
                    mp[1] < sa_center[1],
                )

            ]

            HAND_RECT.center = end

            blit_on_screen(open_hand_surf, HAND_RECT)

        ### if there's no socket b, though, we just draw a line,
        ### using the color of socket a

        else:

            if SCREEN_RECT.colliderect(sa.node.rect):

                eyes_midtop = sa.node.rect.move(0, 6).midtop

                EYE_RECT.bottomright = eyes_midtop

                pupil_vec = Vector2(EYE_RECT.center)

                dist = pupil_vec.distance_to(mp)
                percentage = 5 / dist if dist > 5 else 1

                OPEN_PUPIL_RECT.center = pupil_vec.lerp(mp, percentage)

                blit_on_screen(OPEN_WHITE, EYE_RECT)
                blit_on_screen(OPEN_PUPIL, OPEN_PUPIL_RECT)

                EYE_RECT.bottomleft = eyes_midtop

                pupil_vec = Vector2(EYE_RECT.center)
                dist = pupil_vec.distance_to(mp)
                percentage = 5 / dist if dist > 5 else 1

                OPEN_PUPIL_RECT.center = pupil_vec.lerp(mp, percentage)
                blit_on_screen(OPEN_WHITE, EYE_RECT)
                blit_on_screen(OPEN_PUPIL, OPEN_PUPIL_RECT)

            startv = Vector2(start)
            d = startv.distance_to(end)

            if d > 30:

                p = 30/d
                end = startv.lerp(end,p)

            draw_line(SCREEN, sa.line_color, start, end, 3)

            BASEBALL_RECT.center = mp
            BASEBALL_SURFS_DEQUE.rotate(-1)
            blit_on_screen(BASEBALL_SURFS_DEQUE[0], BASEBALL_RECT)

            open_hand_surf = RELATIVE_POS_TO_OPEN_HAND[

                (
                    sa_center[0] < mp[0],
                    sa_center[1] < mp[1],
                )

            ]

            HAND_RECT.center = end
            opposite_hand = OPEN_HAND_TO_ITS_OPPOSITE[open_hand_surf]
            blit_on_screen(opposite_hand, HAND_RECT)


CONNECTION_ASSISTING_DRAWING_METHODS_MAP = {

  'assisting_line': draw_temp_segment_with_assisting_line,
  'reaching_hands': draw_temp_segment_with_reaching_hands,
  'hands_and_eyes': draw_temp_segment_with_hands_and_eyes,
  'baseball_elements': draw_temp_segment_with_baseball_elements,
  'baseball_elements_and_eyes': (
    draw_temp_segment_with_baseball_elements_and_eyes
  ),

}

if not AVAILABLE_SOCKET_DETECTION_GRAPHICS.issubset(
    CONNECTION_ASSISTING_DRAWING_METHODS_MAP
):

    raise ValueError(
        "all socket detection graphics must be represented in the"
        " DRAWING_METHODS_MAP."
    )
