# games/breakout/ball.py
# MicroPython-compatible.

from lib.engine.sprite import Sprite, SCALE
from lib.engine.colors import WHITE

# Speeds in SCALE units per second (pixels/sec * SCALE)
BALL_SPEED_X_INIT = 3 * SCALE
BALL_SPEED_Y_INIT = 3 * SCALE
BALL_SPEED_MAX    = 6 * SCALE
BALL_SPEED_INC    = SCALE // 8   # +0.125 px/s per paddle hit — reaches max ~24 hits


class Ball(Sprite):
    """The breakout ball. Bounces off walls, the paddle, and bricks."""

    def __init__(self):
        super().__init__(5, 6, w=1, h=1, color=WHITE)
        self._hit_count = 0

    def reset(self):
        """Place ball in launch position and zero its velocity."""
        self.set_pixel_pos(5, 6)
        self._hit_count = 0
        self.vel.x = 0
        self.vel.y = 0

    def launch(self, direction=1, speed_bonus=0):
        """Give the ball its initial velocity. Call after reset()."""
        sx = min(BALL_SPEED_MAX, BALL_SPEED_X_INIT + speed_bonus)
        sy = min(BALL_SPEED_MAX, BALL_SPEED_Y_INIT + speed_bonus)
        self.vel.x = sx * direction
        self.vel.y = -sy   # always launch upward

    def bounce_x(self):
        self.vel.x = -self.vel.x

    def bounce_y(self):
        self.vel.y = -self.vel.y

    def check_walls(self):
        """Bounce off left, right, top walls. Returns True if ball fell off bottom."""
        if self.pos.x <= 0 and self.vel.x < 0:
            self.pos.x = 0
            self.vel.x = abs(self.vel.x)
        if self.pos.x >= 11 * SCALE and self.vel.x > 0:
            self.pos.x = 11 * SCALE
            self.vel.x = -abs(self.vel.x)
        if self.pos.y <= 0 and self.vel.y < 0:
            self.pos.y = 0
            self.vel.y = abs(self.vel.y)
        return self.pos.y > 7 * SCALE

    def bounce_paddle(self, paddle_x, paddle_w, hit_px=None):
        """
        Reflect off the paddle. Angle adjusts based on where the ball hits:
        left third → deflect left, right third → deflect right, centre → keep x.
        Speed increases with each paddle hit, capped at BALL_SPEED_MAX.
        hit_px: interpolated pixel x at the moment of crossing (more accurate
                than self.pixel_x when the ball overshoots on a diagonal).
        """
        if hit_px is None:
            hit_px = self.pixel_x
        paddle_center = paddle_x + paddle_w // 2
        offset = hit_px - paddle_center

        if offset < 0:
            self.vel.x = -abs(self.vel.x)
        elif offset > 0:
            self.vel.x = abs(self.vel.x)

        self._hit_count += 1
        new_sx = min(BALL_SPEED_MAX, BALL_SPEED_X_INIT + self._hit_count * BALL_SPEED_INC)
        new_sy = min(BALL_SPEED_MAX, BALL_SPEED_Y_INIT + self._hit_count * BALL_SPEED_INC)
        sx = 1 if self.vel.x >= 0 else -1
        self.vel.x = sx * new_sx
        self.vel.y = -new_sy        # always launch upward off paddle
        self.pos.y = 6 * SCALE      # push clear to prevent sticking
