# games/breakout/bricks.py
# MicroPython-compatible.

from lib.engine.colors import RED, ORANGE, YELLOW, GREEN

BRICK_ROWS = 4
BRICK_COLS = 12

# Per-row config: (color, base_point_value)
# Rows ordered top-to-bottom (row 0 = y=0 on screen, highest value).
_ROW_CONFIG = [
    (RED,    3),
    (ORANGE, 2),
    (YELLOW, 1),
    (GREEN,  1),
]


class BrickGrid:
    """
    4-row × 12-col brick field occupying display rows 0-3.
    Points are multiplied by the current wave number in PlayingState.
    """

    def __init__(self):
        # _grid[row][col] = True if the brick is still alive
        self._grid = [[True] * BRICK_COLS for _ in range(BRICK_ROWS)]

    def is_alive(self, col, row):
        if 0 <= row < BRICK_ROWS and 0 <= col < BRICK_COLS:
            return self._grid[row][col]
        return False

    def clear(self, col, row):
        """Destroy brick and return its base point value (0 if already gone)."""
        if self.is_alive(col, row):
            self._grid[row][col] = False
            return _ROW_CONFIG[row][1]
        return 0

    def alive_count(self):
        count = 0
        for row in self._grid:
            for b in row:
                if b:
                    count += 1
        return count

    def draw(self, hal):
        for row in range(BRICK_ROWS):
            color, _ = _ROW_CONFIG[row]
            for col in range(BRICK_COLS):
                if self._grid[row][col]:
                    hal.set_pixel(col, row, color)
