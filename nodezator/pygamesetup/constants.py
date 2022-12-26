
### third-party import
from pygame.time import Clock

# choose appropriate window resize event type according to
# availability

try:
    from pygame import WINDOWRESIZED
except ImportError:
    from pygame import VIDEORESIZE
    WINDOW_RESIZE_EVENT_TYPE = VIDEORESIZE
else:
    WINDOW_RESIZE_EVENT_TYPE = WINDOWRESIZED



### general screen setup constant
DEPTH = 32


### framerate-related values/objects

FPS = 24

_CLOCK = Clock()

maintain_fps = _CLOCK.tick
get_fps = _CLOCK.get_fps
