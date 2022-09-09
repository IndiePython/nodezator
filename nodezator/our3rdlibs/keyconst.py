"""Facility for keyboard-related constants."""

from pygame import K_KP1, K_KP2, K_KP3, K_KP4, K_KP5, K_KP6, K_KP7, K_KP8, K_KP9


KEYPAD_TO_COORDINATE_MAP = {
    K_KP1: "bottomleft",
    K_KP2: "midbottom",
    K_KP3: "bottomright",
    K_KP4: "midleft",
    K_KP5: "center",
    K_KP6: "midright",
    K_KP7: "topleft",
    K_KP8: "midtop",
    K_KP9: "topright",
}
