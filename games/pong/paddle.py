# games/pong/paddle.py
# MicroPython-compatible.

from lib.engine.sprite import Sprite, SCALE

PADDLE_H      = 2
PADDLE_SPEED  = 12 * SCALE   # pixels/sec


class Paddle(Sprite):
    """A pong paddle. 1 pixel wide, PADDLE_H pixels tall."""

    def __init__(self, pixel_x, color):
        super().__init__(pixel_x, 3, w=1, h=PADDLE_H, color=color)

    @property
    def center_y(self):
        """Pixel y of the paddle's centre (rounded down)."""
        return self.pixel_y + self.height // 2

    def move_up(self, dt):
        """Move paddle upward, clamped to screen."""
        self.vel.y = -PADDLE_SPEED
        self.update(dt)
        self.vel.y = 0
        self.clamp_to_screen(min_x=self.pixel_x, max_x=self.pixel_x)

    def move_down(self, dt):
        """Move paddle downward, clamped to screen."""
        self.vel.y = PADDLE_SPEED
        self.update(dt)
        self.vel.y = 0
        self.clamp_to_screen(min_x=self.pixel_x, max_x=self.pixel_x)
