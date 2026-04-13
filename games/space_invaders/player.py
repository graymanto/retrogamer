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
        """Read HAL buttons and move accordingly. Returns 'left', 'right', or None."""
        from lib.hal import LEFT, RIGHT
        direction = None

        if hal.is_pressed(LEFT):
            direction = -1
        elif hal.is_pressed(RIGHT):
            direction = 1

        if direction is None:
            self._move_timer   = 0
            self._move_initial = True
            return None

        self._move_timer += dt
        threshold = MOVE_INITIAL_MS if self._move_initial else MOVE_REPEAT_MS

        if self._move_timer >= threshold:
            self._move_timer   = 0
            self._move_initial = False
            new_x = self.x + direction
            if 0 <= new_x <= 11:
                self.x = new_x
            return direction

        return None

    def draw(self, hal):
        if self.active:
            hal.set_pixel(self.x, self.y, self.color)
