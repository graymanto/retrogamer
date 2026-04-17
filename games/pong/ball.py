# games/pong/ball.py
# MicroPython-compatible.

from lib.engine.sprite import Sprite, SCALE
from lib.engine.colors import WHITE
from lib.utils.math_helpers import sign

# Speed in SCALE units per second (pixels/sec * SCALE)
BALL_SPEED_X_INIT = 4 * SCALE   # ~4 pixels/sec horizontal
BALL_SPEED_Y_INIT = 2 * SCALE   # ~2 pixels/sec vertical
BALL_SPEED_X_MAX  = 9 * SCALE
BALL_SPEED_Y_MAX  = 6 * SCALE
BALL_SPEED_INCREMENT = SCALE    # +1 px/sec on each paddle hit


class Ball(Sprite):
    """The pong ball. Bounces off walls and paddles."""

    def __init__(self):
        super().__init__(6, 4, w=1, h=1, color=WHITE)
        self._hit_count = 0
        self._reset(direction=1)

    def _reset(self, direction=1):
        """Reset to centre with initial speed. direction: 1=right, -1=left."""
        self.set_pixel_pos(6, 4)
        self._hit_count = 0
        sx = BALL_SPEED_X_INIT * direction
        # Alternate vertical direction each reset for variety
        sy = BALL_SPEED_Y_INIT if direction > 0 else -BALL_SPEED_Y_INIT
        self.vel.x = sx
        self.vel.y = sy

    def reset(self, direction=1):
        self._reset(direction)

    def bounce_x(self, paddle_center_y=None):
        """Reverse horizontal direction. Optionally adjust y angle based on hit position."""
        self.vel.x = -self.vel.x
        self._hit_count += 1

        # Speed up on each hit, capped at max
        sx = sign(self.vel.x)
        new_speed_x = min(BALL_SPEED_X_MAX, BALL_SPEED_X_INIT + self._hit_count * BALL_SPEED_INCREMENT)
        self.vel.x = sx * new_speed_x

        # Adjust y direction based on where ball hit the paddle
        if paddle_center_y is not None:
            diff = self.pixel_y - paddle_center_y
            # diff: -1 = hit top half, 0 = hit middle, +1 = hit bottom half
            if diff < 0:
                self.vel.y = -abs(self.vel.y)
            elif diff > 0:
                self.vel.y = abs(self.vel.y)
            # else: keep current y direction

    def bounce_y(self):
        """Reverse vertical direction (wall bounce)."""
        self.vel.y = -self.vel.y

    def check_wall_bounce(self):
        """Return True if the ball hit a top or bottom wall and bounced.

        Uses sub-pixel pos (not pixel_y) so the condition only fires once per
        bounce — not repeatedly while pixel_y stays at 0 due to accumulation lag.
        The velocity-direction guard prevents re-triggering after the bounce.
        """
        if self.pos.y <= 0 and self.vel.y < 0:
            self.pos.y = 0
            self.vel.y = abs(self.vel.y)   # force moving down
            return True
        if self.pos.y >= 7 * SCALE and self.vel.y > 0:
            self.pos.y = 7 * SCALE
            self.vel.y = -abs(self.vel.y)  # force moving up
            return True
        return False

    def is_off_left(self):
        return self.pos.x < 0

    def is_off_right(self):
        return self.pos.x > 11 * SCALE
