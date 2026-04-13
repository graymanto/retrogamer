# lib/engine/sprite.py
# MicroPython-compatible. Integer fixed-point physics.
#
# SCALE = 256: positions and velocities are stored as (real_value * SCALE).
#   pos.x = real_pixel_x * SCALE
#   vel.x = real_pixels_per_ms * SCALE
#   update(dt): pos.x += vel.x * dt   (no division — accumulates each frame)
#   pixel_x: pos.x // SCALE
#
# Example: ball moving at 3 px/sec = 0.003 px/ms
#   vel.x = int(0.003 * 256) = 0   <- too slow, use larger unit
#
# Better: express velocity in pixels-per-second * SCALE, then divide dt by 1000:
#   vel.x = speed_px_per_sec * SCALE
#   update(dt): pos.x += vel.x * dt // 1000
#   This gives pos.x in units of (1/SCALE) pixels (exact accumulation).

SCALE = 256


class Vec2:
    """2D integer vector. Used for position and velocity."""
    __slots__ = ('x', 'y')

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class Sprite:
    """
    A game object with integer fixed-point position, velocity, size, and color.

    Position (pos.x, pos.y): in SCALE units. pixel_x = pos.x // SCALE.
    Velocity (vel.x, vel.y): in SCALE units per second (pixels/sec * SCALE).
    update(dt): advances position by vel * dt / 1000. dt is in milliseconds.
    """

    def __init__(self, pixel_x, pixel_y, w=1, h=1, color=(255, 255, 255)):
        self.pos    = Vec2(pixel_x * SCALE, pixel_y * SCALE)
        self.vel    = Vec2(0, 0)   # in SCALE units per second
        self.width  = w
        self.height = h
        self.color  = color
        self.active = True

    @property
    def pixel_x(self):
        return self.pos.x // SCALE

    @property
    def pixel_y(self):
        return self.pos.y // SCALE

    def set_pixel_pos(self, px, py):
        """Teleport to an exact pixel position (resets sub-pixel accumulation)."""
        self.pos.x = px * SCALE
        self.pos.y = py * SCALE

    def update(self, dt):
        """Advance position by velocity. dt in milliseconds."""
        self.pos.x += self.vel.x * dt // 1000
        self.pos.y += self.vel.y * dt // 1000

    def draw(self, hal):
        """Draw sprite rectangle to the HAL."""
        if not self.active:
            return
        px = self.pixel_x
        py = self.pixel_y
        for dy in range(self.height):
            for dx in range(self.width):
                nx = px + dx
                ny = py + dy
                if 0 <= nx < 12 and 0 <= ny < 8:
                    hal.set_pixel(nx, ny, self.color)

    def overlaps(self, other):
        """AABB collision check in pixel space."""
        ax = self.pixel_x
        ay = self.pixel_y
        bx = other.pixel_x
        by = other.pixel_y
        return (ax < bx + other.width  and
                ax + self.width  > bx  and
                ay < by + other.height and
                ay + self.height > by)

    def clamp_to_screen(self, min_x=0, max_x=11, min_y=0, max_y=7):
        """Clamp pixel position to screen bounds (accounts for sprite size)."""
        lo_x = min_x * SCALE
        hi_x = (max_x - self.width  + 1) * SCALE
        lo_y = min_y * SCALE
        hi_y = (max_y - self.height + 1) * SCALE
        if self.pos.x < lo_x:
            self.pos.x = lo_x
        if self.pos.x > hi_x:
            self.pos.x = hi_x
        if self.pos.y < lo_y:
            self.pos.y = lo_y
        if self.pos.y > hi_y:
            self.pos.y = hi_y
