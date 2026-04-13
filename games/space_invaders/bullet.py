# games/space_invaders/bullet.py
# MicroPython-compatible. Simple timer-based bullet (not Sprite-based).

from lib.engine.colors import WHITE, RED, YELLOW


class Bullet:
    """A single-pixel bullet that moves one pixel per tick.
    dy = -1 for player bullets (upward), +1 for invader bullets (downward)."""

    def __init__(self, x, y, dy, color=WHITE, speed_ms=80):
        self.x        = x
        self.y        = y
        self.dy       = dy       # direction: -1 or +1
        self.color    = color
        self.speed_ms = speed_ms  # ms between each pixel move
        self.active   = True
        self._timer   = 0

    def update(self, dt):
        """Advance timer; move bullet if interval elapsed. Deactivate if off screen."""
        if not self.active:
            return
        self._timer += dt
        if self._timer >= self.speed_ms:
            self._timer = 0
            self.y += self.dy
            if self.y < 0 or self.y > 7:
                self.active = False

    def draw(self, hal):
        if self.active and 0 <= self.x < 12 and 0 <= self.y < 8:
            hal.set_pixel(self.x, self.y, self.color)
