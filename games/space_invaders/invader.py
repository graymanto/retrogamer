# games/space_invaders/invader.py
# MicroPython-compatible. Manages the invader grid as a 2D boolean array.

from lib.engine.colors import CYAN, GREEN, YELLOW
import random

# One colour per row of invaders
ROW_COLORS = [CYAN, GREEN, YELLOW]

# Points per row
ROW_POINTS = [30, 20, 10]


class InvaderGrid:
    """
    The invader formation. Uses a 2D bool array — no per-invader Sprite objects
    to keep memory usage low on MicroPython.

    Layout (default): 8 columns × 3 rows, starting at pixel (2, 0).
    Movement: steps right one pixel each interval; reverses and drops 1 row at edges.
    """

    def __init__(self, cols=8, rows=3, start_x=2, start_y=0):
        self.cols    = cols
        self.rows    = rows
        self.x       = start_x    # left edge pixel
        self.y       = start_y    # top edge pixel
        self.dx      = 1          # current horizontal direction

        # grid[row][col] = True means alive
        self.grid = [[True] * cols for _ in range(rows)]

        self._step_timer = 0
        self._step_tone  = 0   # alternates 0/1 for march sound

        # Firing state per column: timer countdown until next shot
        self._fire_timers = [random.randint(1000, 3000) for _ in range(cols)]

    # ---------- Grid queries ----------

    def alive_count(self):
        """Return number of living invaders."""
        n = 0
        for row in self.grid:
            for cell in row:
                if cell:
                    n += 1
        return n

    def _step_interval_ms(self):
        """Speed increases as invaders die. Ranges from 800ms (full) to ~100ms (1 left)."""
        alive = self.alive_count()
        total = self.cols * self.rows
        return max(80, 80 + alive * 30)

    def has_reached_player(self):
        """True if bottom row of invaders has reached row 6 (player is row 7)."""
        return self.y + self.rows - 1 >= 6

    # ---------- Update ----------

    def update(self, dt, hal):
        """Advance step timer, move grid if due. Returns list of tone freqs to play."""
        self._step_timer += dt
        tones = []

        if self._step_timer >= self._step_interval_ms():
            self._step_timer = 0
            self._do_step()
            # March sound alternates between two tones
            freq = 120 if self._step_tone == 0 else 90
            self._step_tone = 1 - self._step_tone
            tones.append(freq)

        return tones

    def _do_step(self):
        """Move grid one step. Reverse and drop when hitting edges."""
        # Find actual extents (some columns may be empty)
        min_col = self._leftmost_col()
        max_col = self._rightmost_col()
        if min_col is None:
            return

        left_edge  = self.x + min_col
        right_edge = self.x + max_col

        if self.dx == 1 and right_edge >= 11:
            self.y  += 1
            self.dx  = -1
        elif self.dx == -1 and left_edge <= 0:
            self.y  += 1
            self.dx  = 1
        else:
            self.x += self.dx

    def _leftmost_col(self):
        for col in range(self.cols):
            for row in range(self.rows):
                if self.grid[row][col]:
                    return col
        return None

    def _rightmost_col(self):
        for col in range(self.cols - 1, -1, -1):
            for row in range(self.rows):
                if self.grid[row][col]:
                    return col
        return None

    # ---------- Collision ----------

    def check_hit(self, bx, by):
        """Check if a bullet at (bx, by) hits any invader.
        Returns points scored (0 if no hit)."""
        col = bx - self.x
        row = by - self.y
        if 0 <= row < self.rows and 0 <= col < self.cols:
            if self.grid[row][col]:
                self.grid[row][col] = False
                return ROW_POINTS[row % len(ROW_POINTS)]
        return 0

    # ---------- Shooting ----------

    def update_shooting(self, dt):
        """Decrement fire timers. Returns list of (px, py) for new invader bullets."""
        shots = []
        for col in range(self.cols):
            self._fire_timers[col] -= dt
            if self._fire_timers[col] <= 0:
                # Reset timer
                self._fire_timers[col] = random.randint(1500, 4000)
                # Find bottom-most alive invader in this column
                shooter = self._bottom_invader(col)
                if shooter is not None:
                    shots.append(shooter)
        return shots

    def _bottom_invader(self, col):
        """Return pixel (x, y) of the bottom-most alive invader in col, or None."""
        for row in range(self.rows - 1, -1, -1):
            if self.grid[row][col]:
                return (self.x + col, self.y + row)
        return None

    # ---------- Rendering ----------

    def draw(self, hal):
        for row in range(self.rows):
            color = ROW_COLORS[row % len(ROW_COLORS)]
            for col in range(self.cols):
                if self.grid[row][col]:
                    px = self.x + col
                    py = self.y + row
                    if 0 <= px < 12 and 0 <= py < 8:
                        hal.set_pixel(px, py, color)
