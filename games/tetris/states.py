# games/tetris/states.py
# MicroPython-compatible. All Tetris game states.
#
# Display layout (12 wide × 8 tall):
#   Full 12 × 8 grid used as the playfield.
#
# Piece selection: 7-bag randomiser — one of each piece per 7 draws, reshuffled
#   each cycle. Prevents piece droughts.
#
# Line clear: a row clears when _CLEAR_THRESHOLD or more of its 12 cells are
#   filled (default 10). Accommodates the extra-wide board.
#
# Scoring: cleared_lines × level × base_table[lines].
# Level increases every 5 lines. Drop speed scales with level (1000ms → 100ms).
# Game ends when a new piece cannot be placed at its spawn position.
#
# Controls:
#   Menu     : LEFT = launcher, A or DOWN = start
#   Game     : LEFT / RIGHT = move, A or UP = rotate, DOWN = soft drop, B = hard drop
#   GameOver : LEFT = launcher, A or DOWN = play again

import random

from lib.engine.state  import GameState
from lib.engine.colors import YELLOW, RED, GREEN, BLUE, CYAN, ORANGE, PURPLE
from lib.engine.font   import draw_char
from lib.hal           import LEFT, RIGHT, DOWN, UP, A, B

_PF_W = 12   # playfield width — full display width
_PF_H = 8    # playfield height (rows 0-7)

# ── Tetrominoes ───────────────────────────────────────────────────────────────
# Outer tuple: one entry per piece type (0-6).
# Each entry: tuple of rotations.
# Each rotation: tuple of (dr, dc) cell offsets from the anchor point.
_PIECES = (
    # 0: I — cyan
    (((0,0),(0,1),(0,2),(0,3)),
     ((0,0),(1,0),(2,0),(3,0))),
    # 1: O — yellow, single rotation
    (((0,0),(0,1),(1,0),(1,1)),),
    # 2: T — purple
    (((0,1),(1,0),(1,1),(1,2)),
     ((0,0),(1,0),(1,1),(2,0)),
     ((0,0),(0,1),(0,2),(1,1)),
     ((0,1),(1,0),(1,1),(2,1))),
    # 3: S — green
    (((0,1),(0,2),(1,0),(1,1)),
     ((0,0),(1,0),(1,1),(2,1))),
    # 4: Z — red
    (((0,0),(0,1),(1,1),(1,2)),
     ((0,1),(1,0),(1,1),(2,0))),
    # 5: J — blue
    (((0,0),(1,0),(1,1),(1,2)),
     ((0,0),(0,1),(1,0),(2,0)),
     ((0,0),(0,1),(0,2),(1,2)),
     ((0,1),(1,1),(2,0),(2,1))),
    # 6: L — orange
    (((0,2),(1,0),(1,1),(1,2)),
     ((0,0),(1,0),(2,0),(2,1)),
     ((0,0),(0,1),(0,2),(1,0)),
     ((0,0),(0,1),(1,1),(2,1))),
)

_COLORS = (CYAN, YELLOW, PURPLE, GREEN, RED, BLUE, ORANGE)

# Anchor column when spawning each piece type (centres it in the 12-wide field)
_SPAWN_C = (4, 5, 4, 4, 4, 4, 4)

# Score for 1 / 2 / 3 / 4 lines cleared (multiplied by current level)
_SCORE_TABLE = (0, 10, 25, 50, 80)

_LINES_PER_LVL    = 5   # lines needed to advance one level
_CLEAR_THRESHOLD  = 10  # cells filled (out of 12) needed to clear a row

# Dim block colours used in the menu background (full 12-wide rows)
_MENU_BLOCKS = (
    (0,5,(0,44,51)),(1,5,(0,44,51)),(2,5,(0,44,51)),(3,5,(0,44,51)),
    (4,5,(32,0,40)),(5,5,(32,0,40)),(6,5,(32,0,40)),
    (0,6,(51,20,0)),(1,6,(51,20,0)),(2,6,(51,20,0)),(3,6,(51,40,0)),(4,6,(51,40,0)),
    (5,6,(0,40,0)),(6,6,(0,40,0)),(7,6,(0,40,0)),(8,6,(0,40,0)),
    (0,7,(51,0,0)),(1,7,(51,0,0)),(2,7,(0,40,0)),(3,7,(0,40,0)),
    (4,7,(51,40,0)),(5,7,(51,40,0)),(6,7,(0,0,51)),(7,7,(0,0,51)),
    (8,7,(51,20,0)),(9,7,(51,20,0)),(10,7,(51,20,0)),(11,7,(51,20,0)),
)

# Timing constants
_LOCK_DELAY   = 650   # ms the piece stays on the ground before auto-locking
_SOFT_DROP_MS = 40    # drop interval (ms) while DOWN is held
_MOVE_INIT_MS = 170   # ms before left/right auto-repeat begins
_MOVE_RPT_MS  = 70    # ms between auto-repeat steps


def _drop_ms(level):
    """Auto-drop interval in ms at the given level (1000ms at L1 → 100ms floor)."""
    v = 1000 - level * 60
    if v < 100:
        return 100
    return v


class MenuState(GameState):
    """Tetris title screen. A or DOWN = start, LEFT = launcher."""

    def __init__(self, game):
        super().__init__(game)
        self._timer = 0
        self._blink = True

    def on_enter(self):
        self._timer = 0

    def update(self, dt):
        self._timer += dt
        self._blink  = (self._timer // 400) % 2 == 0

        if self.hal.is_pressed(LEFT):
            self.game.quit()
        elif self.hal.is_pressed(A) or self.hal.is_pressed(DOWN):
            self.game.states.request_switch(PlayingState(self.game))

    def render(self):
        hal = self.hal

        # Dim stacked blocks suggesting a filled Tetris board
        for col, row, color in _MENU_BLOCKS:
            hal.set_pixel(col, row, color)

        # "TE" label centred across the full 12-wide display
        # T at col 2 (cols 2-4), E at col 7 (cols 7-9) — centred with 2-px gap
        draw_char(hal, 'T', 2, 1, PURPLE)
        draw_char(hal, 'E', 7, 1, PURPLE)

        # Blinking "press A" prompt
        if self._blink:
            hal.set_pixel(5, 7, PURPLE)
            hal.set_pixel(6, 7, PURPLE)


class PlayingState(GameState):
    """Main Tetris gameplay."""

    def on_enter(self):
        self._board        = [[None] * _PF_W for _ in range(_PF_H)]
        self.game.score    = 0
        self.game.level    = 1
        self._lines        = 0
        self._drop_t       = _drop_ms(1)
        self._lock_t       = _LOCK_DELAY
        self._was_grounded = False
        self._bag          = []   # 7-bag piece randomiser
        self._next         = self._draw_piece()
        # Input state
        self._pk_rot   = False
        self._pk_b     = False
        self._move_dir = 0
        self._move_t   = 0
        # Spawn first piece
        self._spawn()

    # ── Piece helpers ─────────────────────────────────────────────────────────

    def _draw_piece(self):
        """Draw the next piece type from the 7-bag.
        When the bag empties it is refilled with one of each piece type,
        shuffled with Fisher-Yates. Guarantees no piece appears twice before
        all seven have been seen."""
        if not self._bag:
            self._bag = list(range(7))
            for i in range(6, 0, -1):
                j = random.randint(0, i)
                self._bag[i], self._bag[j] = self._bag[j], self._bag[i]
        return self._bag.pop()

    def _cells(self, ptype, rot, r, c):
        """Return list of (row, col) for all cells of a piece placement."""
        result = []
        for dr, dc in _PIECES[ptype][rot]:
            result.append((r + dr, c + dc))
        return result

    def _valid(self, ptype, rot, r, c):
        """True if the piece placement is inside the playfield and unoccupied."""
        for cr, cc in self._cells(ptype, rot, r, c):
            if cr < 0 or cr >= _PF_H or cc < 0 or cc >= _PF_W:
                return False
            if self._board[cr][cc] is not None:
                return False
        return True

    def _spawn(self):
        """Bring the queued next piece into play and queue a new next piece."""
        self._ptype        = self._next
        self._prot         = 0
        self._pr           = 0
        self._pc           = _SPAWN_C[self._ptype]
        self._next         = self._draw_piece()
        self._was_grounded = False
        self._drop_t       = _drop_ms(self.game.level)
        if not self._valid(self._ptype, self._prot, self._pr, self._pc):
            # Stack has reached the top — game over
            self.game.states.request_switch(
                GameOverState(self.game, self.game.score)
            )

    def _lock(self):
        """Write the active piece into the board, clear full lines, spawn next."""
        color = _COLORS[self._ptype]
        for cr, cc in self._cells(self._ptype, self._prot, self._pr, self._pc):
            if 0 <= cr < _PF_H and 0 <= cc < _PF_W:
                self._board[cr][cc] = color
        self.hal.play_tone(330, 50)
        self._clear_lines()
        self._spawn()

    def _clear_lines(self):
        """Remove rows that meet the fill threshold, drop rows above, award score."""
        kept    = []
        cleared = 0
        for row in self._board:
            filled = 0
            for cell in row:
                if cell is not None:
                    filled += 1
            if filled >= _CLEAR_THRESHOLD:
                cleared += 1
            else:
                kept.append(row)
        if cleared == 0:
            return
        for _ in range(cleared):
            kept.insert(0, [None] * _PF_W)
        self._board  = kept
        self._lines += cleared
        score_lines = cleared if cleared < len(_SCORE_TABLE) else len(_SCORE_TABLE) - 1
        self.game.score += _SCORE_TABLE[score_lines] * self.game.level
        new_level = self._lines // _LINES_PER_LVL + 1
        if new_level != self.game.level:
            self.game.level = new_level
            self.hal.play_tone(880, 120)
        else:
            self.hal.play_tone(550, 80)
        self.hal.vibrate(duration_ms=80)

    # ── Input ─────────────────────────────────────────────────────────────────

    def _handle_input(self, dt):
        hal   = self.hal
        left  = hal.is_pressed(LEFT)
        right = hal.is_pressed(RIGHT)
        rot   = hal.is_pressed(A) or hal.is_pressed(UP)
        b_key = hal.is_pressed(B)

        # Rotate: edge-triggered with simple wall-kick (try ±1 column)
        if rot and not self._pk_rot:
            nr = (self._prot + 1) % len(_PIECES[self._ptype])
            if self._valid(self._ptype, nr, self._pr, self._pc):
                self._prot = nr
                hal.play_tone(440, 25)
            elif self._valid(self._ptype, nr, self._pr, self._pc - 1):
                self._pc  -= 1
                self._prot = nr
                hal.play_tone(440, 25)
            elif self._valid(self._ptype, nr, self._pr, self._pc + 1):
                self._pc  += 1
                self._prot = nr
                hal.play_tone(440, 25)
        self._pk_rot = rot

        # Hard drop (B): slam piece to lowest valid row and lock immediately
        if b_key and not self._pk_b:
            while self._valid(self._ptype, self._prot, self._pr + 1, self._pc):
                self._pr += 1
            self._lock()
        self._pk_b = b_key

        # Left / right movement with initial delay then auto-repeat
        new_dir = 0
        if left and not right:
            new_dir = -1
        elif right and not left:
            new_dir = 1

        if new_dir != 0:
            if new_dir != self._move_dir:
                # New direction — move once immediately, then start repeat timer
                self._move_dir = new_dir
                self._move_t   = _MOVE_INIT_MS
                if self._valid(self._ptype, self._prot, self._pr, self._pc + new_dir):
                    self._pc += new_dir
                    hal.play_tone(220, 20)
            else:
                self._move_t -= dt
                if self._move_t <= 0:
                    self._move_t = _MOVE_RPT_MS
                    if self._valid(self._ptype, self._prot, self._pr, self._pc + new_dir):
                        self._pc += new_dir
                        hal.play_tone(220, 20)
        else:
            self._move_dir = 0

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt):
        self._handle_input(dt)

        on_ground = not self._valid(self._ptype, self._prot, self._pr + 1, self._pc)

        if on_ground:
            # Start the lock timer the first time the piece lands
            if not self._was_grounded:
                self._was_grounded = True
                self._lock_t       = _LOCK_DELAY
            self._lock_t -= dt
            if self._lock_t <= 0:
                self._lock()
        else:
            self._was_grounded = False

            # Gravity — speed up while DOWN is held (soft drop)
            drop_interval = _drop_ms(self.game.level)
            if self.hal.is_pressed(DOWN) and drop_interval > _SOFT_DROP_MS:
                drop_interval = _SOFT_DROP_MS
                # Clamp the pending timer immediately so the first step fires
                # without waiting for the slow natural-drop timer to expire.
                if self._drop_t > _SOFT_DROP_MS:
                    self._drop_t = _SOFT_DROP_MS

            self._drop_t -= dt
            if self._drop_t <= 0:
                self._drop_t = drop_interval
                self._pr    += 1

    # ── Render ────────────────────────────────────────────────────────────────

    def render(self):
        hal = self.hal

        # Board — locked cells
        for r in range(_PF_H):
            for c in range(_PF_W):
                cell = self._board[r][c]
                if cell is not None:
                    hal.set_pixel(c, r, cell)

        # Ghost piece — dim landing preview (draw before active piece)
        ghost_r = self._pr
        while self._valid(self._ptype, self._prot, ghost_r + 1, self._pc):
            ghost_r += 1
        if ghost_r != self._pr:
            gr, gg, gb = _COLORS[self._ptype]
            ghost_color = (gr // 5, gg // 5, gb // 5)
            for cr, cc in self._cells(self._ptype, self._prot, ghost_r, self._pc):
                if 0 <= cr < _PF_H and 0 <= cc < _PF_W:
                    hal.set_pixel(cc, cr, ghost_color)

        # Active piece (on top of ghost)
        active_color = _COLORS[self._ptype]
        for cr, cc in self._cells(self._ptype, self._prot, self._pr, self._pc):
            if 0 <= cr < _PF_H and 0 <= cc < _PF_W:
                hal.set_pixel(cc, cr, active_color)



class GameOverState(GameState):
    """Shown when the stack reaches the top. Score displayed; A/DOWN = play again, LEFT = launcher."""

    def __init__(self, game, score):
        super().__init__(game)
        self._score = score
        self._timer = 0
        self._blink = True

    def on_enter(self):
        self._timer = 0

    def update(self, dt):
        self._timer += dt
        self._blink  = (self._timer // 400) % 2 == 0

        if self._timer > 800 and self.hal.is_pressed(LEFT):
            self.game.quit()
        elif self._timer > 800 and (self.hal.is_pressed(A) or self.hal.is_pressed(DOWN)):
            self.game.states.request_switch(PlayingState(self.game))

    def render(self):
        hal = self.hal

        # Blinking dim blue background
        if self._blink:
            for y in range(8):
                for x in range(12):
                    hal.set_pixel(x, y, (0, 15, 35))

        # Score — up to 3 digits centred across the display
        s = str(self._score)
        n = len(s)
        if n == 1:
            draw_char(hal, s[0], 4, 1, PURPLE)
        elif n == 2:
            draw_char(hal, s[0], 1, 1, PURPLE)
            draw_char(hal, s[1], 5, 1, PURPLE)
        else:
            draw_char(hal, s[0], 0, 1, PURPLE)
            draw_char(hal, s[1], 4, 1, PURPLE)
            draw_char(hal, s[2], 8, 1, PURPLE)

        # "TE" game-over label
        draw_char(hal, 'T', 0, 6, PURPLE)
        draw_char(hal, 'E', 4, 6, PURPLE)

        # Blinking "press A" prompt
        if self._blink:
            hal.set_pixel(10, 7, PURPLE)
            hal.set_pixel(11, 7, PURPLE)
