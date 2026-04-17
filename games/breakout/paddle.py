# games/breakout/paddle.py
# MicroPython-compatible.

from lib.engine.sprite import Sprite, SCALE
from lib.engine.colors import WHITE

PADDLE_W     = 3
PADDLE_SPEED = 10 * SCALE   # pixels/sec


class Paddle(Sprite):
    """Horizontal breakout paddle. 3 pixels wide, sits on the bottom row."""

    def __init__(self):
        # Start centred-ish: x=4 so paddle occupies cols 4-6
        super().__init__(4, 7, w=PADDLE_W, h=1, color=WHITE)

    def move_left(self, dt):
        self.vel.x = -PADDLE_SPEED
        self.update(dt)
        self.vel.x = 0
        self.clamp_to_screen(min_y=7, max_y=7)

    def move_right(self, dt):
        self.vel.x = PADDLE_SPEED
        self.update(dt)
        self.vel.x = 0
        self.clamp_to_screen(min_y=7, max_y=7)
