# games/space_invaders/player.py
# MicroPython-compatible. Player ship for space invaders.

from lib.engine.colors import GREEN

PLAYER_ROW   = 7
PLAYER_COLOR = GREEN

# Move-repeat timing
MOVE_INITIAL_MS = 180   # delay before hold-repeat kicks in
MOVE_REPEAT_MS  = 90    # repeat interval when held


class Player:
    """Player ship at the bottom of the screen. Moves left/right, fires upward."""

    def __init__(self):
        self.x      = 5     # pixel x position (0-11)
        self.y      = PLAYER_ROW
        self.color  = PLAYER_COLOR
        self.active = True

        # Move repeat state
        self._move_timer   = 0
        self._move_initial = True   # True = waiting for initial delay

    def handle_input(self, hal, dt):
        """Read HAL buttons and move accordingly. Returns the direction moved or None."""
        from lib.hal import LEFT, RIGHT
        direction = None

        if hal.is_pressed(LEFT):
            direction = -1
        elif hal.is_pressed(RIGHT):
            direction = 1

        if direction is None:
            # No button held — reset repeat state for next press
            self._move_timer   = 0
            self._move_initial = True
            return None

        # Move immediately on the first frame a button is pressed,
        # then repeat at MOVE_REPEAT_MS intervals while it remains held.
        if self._move_initial:
            self._move_initial = False
            self._move_timer   = 0
            new_x = self.x + direction
            if 0 <= new_x <= 11:
                self.x = new_x
            return direction

        self._move_timer += dt
        if self._move_timer >= MOVE_REPEAT_MS:
            self._move_timer = 0
            new_x = self.x + direction
            if 0 <= new_x <= 11:
                self.x = new_x
            return direction

        return None

    def draw(self, hal):
        if self.active:
            hal.set_pixel(self.x, self.y, self.color)
