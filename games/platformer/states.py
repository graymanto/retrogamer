# games/platformer/states.py
# MicroPython-compatible. All Platformer game states.
#
# Layout: full 12×8 display. Level scrolls horizontally (levels are 36 px wide).
#
# Tile key:
#   ' '  empty / sky
#   '#'  solid platform  — player lands on / is blocked by these
#   'S'  spawn           — treated as solid; player starts here
#   'H'  hazard          — non-solid; kills on contact
#   'C'  coin            — non-solid; collected for +1 score
#   'X'  exit            — non-solid; completes the level
#
# Controls:
#   Menu    : LEFT = back to launcher, A or DOWN = start
#   Playing : LEFT/RIGHT = walk, UP or A = jump
#   GameOver: LEFT = launcher, A or DOWN = play again

from lib.engine.state  import GameState
from lib.engine.colors import WHITE, RED, YELLOW, CYAN, MAGENTA
from lib.engine.font   import draw_char
from lib.engine.sprite import SCALE
from lib.hal           import UP, DOWN, LEFT, RIGHT, A

# ── Physics constants ─────────────────────────────────────────────────────────
# All velocities / accelerations are in sub-pixels per second (1 px = SCALE=256).
# Physics step: v += a*dt/1000;  pos += v*dt/1000  (integer, truncated).
#
# Gravity 22 px/s²: falls one row in ~0.30 s from rest — fast enough to feel weighty
# on a tiny screen without being uncontrollable.
# Jump  -14 px/s  → apex ≈ 14²/(2*22) ≈ 4.5 rows from the jump pixel.
# Walk    8 px/s  → crosses 36-wide level in ~4.5 s.
_GRAVITY    = 22 * SCALE   # sub-px / s²
_JUMP_VEL   = -11 * SCALE  # sub-px / s  (negative = upward)
_MAX_FALL   =  9 * SCALE   # sub-px / s  terminal velocity cap
_WALK_SPEED =  8 * SCALE   # sub-px / s

# ── Display ───────────────────────────────────────────────────────────────────
_W = 12   # viewport width  (full display columns)
_H = 8    # viewport height (full display rows)

# ── Colors ────────────────────────────────────────────────────────────────────
_SKY_C    = (0,   0,  20)   # near-black blue
_PLAT_C   = (50,  50, 80)   # blue-grey solid platform
_HAZARD_C = RED
_COIN_C   = YELLOW
_EXIT_C   = CYAN
_PLAYER_C = WHITE
_LIFE_C   = (100, 0,  80)   # dim magenta life dots


def _draw_sky(hal):
    for y in range(_H):
        for x in range(_W):
            hal.set_pixel(x, y, _SKY_C)


def _clamp(v, lo, hi):
    if v < lo:
        return lo
    if v > hi:
        return hi
    return v


# ─────────────────────────────────────────────────────────────────────────────
class MenuState(GameState):
    """Title screen. LEFT = launcher, A / DOWN = start."""

    def __init__(self, game):
        super().__init__(game)
        self._timer = 0
        self._blink = True

    def on_enter(self):
        self._timer = 0

    def update(self, dt):
        self._timer += dt
        self._blink = (self._timer // 400) % 2 == 0

        if self.hal.is_pressed(LEFT):
            self.game.quit()
        elif self.hal.is_pressed(A) or self.hal.is_pressed(DOWN):
            self.game.level_idx = 0
            self.game.score     = 0
            self.game.lives     = 3
            self.game.states.request_switch(PlayingState(self.game))

    def render(self):
        hal = self.hal
        _draw_sky(hal)
        # Draw a simple platform silhouette for context
        for x in range(_W):
            hal.set_pixel(x, 7, _PLAT_C)
        for x in range(3, 7):
            hal.set_pixel(x, 5, _PLAT_C)
        # "PL" title
        draw_char(hal, 'P', 1, 1, MAGENTA)
        draw_char(hal, 'L', 5, 1, MAGENTA)
        # Blink prompt
        if self._blink:
            hal.set_pixel(5, 7, WHITE)
            hal.set_pixel(6, 7, WHITE)


# ─────────────────────────────────────────────────────────────────────────────
class PlayingState(GameState):
    """Main gameplay: physics, scrolling, tile interaction."""

    # ── Setup ────────────────────────────────────────────────────────────────

    def on_enter(self):
        self._load_level(self.game.levels[self.game.level_idx])
        self._dying      = False
        self._die_timer  = 0
        self._pk_up      = False
        self._pk_a       = False

    def _load_level(self, level):
        self._rows        = level['rows']
        self._level_w     = len(self._rows[0])
        self._collected   = set()   # (row, col) pairs for spent coins
        # scroll > 0: auto-scroll mode (Geometry Dash style).
        # Value is pixels/second; stored as sub-pixels/second for physics.
        self._auto_scroll = level.get('scroll', 0) * SCALE

        # Locate spawn tile 'S'
        spawn_col = 1
        spawn_row = 6
        for r in range(_H):
            for c in range(self._level_w):
                if self._rows[r][c] == 'S':
                    spawn_col = c
                    spawn_row = r
        self._spawn = (spawn_col, spawn_row)
        self._respawn()

    def _respawn(self):
        sc, sr = self._spawn
        self._px      = sc * SCALE
        self._py      = sr * SCALE
        self._vy      = 0
        self._dying   = False
        self._die_timer = 0
        # In auto-scroll mode pin player to screen col 2; normal = col 5
        offset = 2 if self._auto_scroll > 0 else 5
        self._cam_x = _clamp(sc - offset, 0, self._level_w - _W)

    # ── Tile helpers ─────────────────────────────────────────────────────────

    def _tile_at(self, col, row):
        """Return tile char. Out-of-bounds = '#' (treat as solid wall/floor)."""
        if row < 0 or row >= _H or col < 0 or col >= self._level_w:
            return '#'
        ch = self._rows[row][col]
        if ch == 'C' and (row, col) in self._collected:
            return ' '
        return ch

    def _is_solid(self, col, row):
        t = self._tile_at(col, row)
        # '#' and 'S' are blocking; hazard/coin/exit are passable
        return t == '#' or t == 'S'

    # ── Physics ──────────────────────────────────────────────────────────────

    def _physics(self, dt):
        hal = self.hal

        # ── Jump (edge-triggered; only when standing on solid) ───────────────
        up = hal.is_pressed(UP)
        a  = hal.is_pressed(A)
        grounded = self._is_solid(self._px // SCALE, self._py // SCALE + 1)
        if grounded and ((up and not self._pk_up) or (a and not self._pk_a)):
            self._vy = _JUMP_VEL
            hal.play_tone(523, 60)
        self._pk_up = up
        self._pk_a  = a

        # ── Gravity ──────────────────────────────────────────────────────────
        self._vy += _GRAVITY * dt // 1000
        if self._vy > _MAX_FALL:
            self._vy = _MAX_FALL

        # ── Horizontal movement ───────────────────────────────────────────────
        if self._auto_scroll > 0:
            # Auto-scroll (Geometry Dash) mode: player always moves right at a
            # fixed speed. Left/right input is ignored. Hitting any solid tile
            # from the right is instant death — the player must jump over
            # obstacles rather than being blocked by them.
            vx = self._auto_scroll
        else:
            vx = 0
            if hal.is_pressed(LEFT):
                vx = -_WALK_SPEED
            elif hal.is_pressed(RIGHT):
                vx = _WALK_SPEED

        new_px  = self._px + vx * dt // 1000
        new_col = new_px // SCALE
        cur_col = self._px // SCALE
        cur_row = self._py // SCALE

        if new_col != cur_col and self._is_solid(new_col, cur_row):
            if self._auto_scroll > 0:
                self._die()   # wall collision = death in auto-scroll mode
                return
            new_px = self._px   # wall blocks in manual mode
        self._px = _clamp(new_px, 0, (self._level_w - 1) * SCALE)

        # ── Camera ───────────────────────────────────────────────────────────
        player_col = self._px // SCALE
        if self._auto_scroll > 0:
            # Player stays near column 2 of the viewport; world scrolls past
            self._cam_x = _clamp(player_col - 2, 0, self._level_w - _W)
            # Fell behind the camera's left edge → crushed
            if player_col < self._cam_x:
                self._die()
                return
            # Reached the right end of the level → complete
            if player_col >= self._level_w - 1:
                self._level_complete()
                return
        else:
            self._cam_x = _clamp(player_col - 5, 0, self._level_w - _W)

        # ── Vertical movement ─────────────────────────────────────────────────
        new_py  = self._py + self._vy * dt // 1000
        new_row = new_py // SCALE
        cur_col = self._px // SCALE   # updated after horizontal step
        cur_row = self._py // SCALE   # recompute — px move can't change row

        if new_row > cur_row:
            # Moving downward — check floor
            if self._is_solid(cur_col, new_row):
                new_py   = cur_row * SCALE   # land on top of the tile
                self._vy = 0
        elif new_row < cur_row:
            # Moving upward — check ceiling
            if self._is_solid(cur_col, new_row):
                new_py   = cur_row * SCALE
                self._vy = 0
        else:
            # Stayed in the same pixel row this frame.
            # Explicitly manage ground contact to avoid sub-pixel drift.
            if self._vy >= 0:
                if self._is_solid(cur_col, cur_row + 1):
                    # Solid directly below: snap to exact row top and kill vy.
                    # This prevents floating accumulation while standing still.
                    new_py   = cur_row * SCALE
                    self._vy = 0
                else:
                    # Floor just disappeared (walked off a ledge) or mid-air.
                    # Nudge to the very bottom of the current pixel row so that
                    # gravity will push us into the row below on the next frame,
                    # eliminating the multi-frame "walking on air" delay.
                    new_py = (cur_row + 1) * SCALE - 1

        # Clamp top of screen
        if new_py < 0:
            new_py   = 0
            self._vy = 0

        # Fell off the bottom of the display — treat as a pit death
        if new_py >= _H * SCALE:
            self._die()
            return

        self._py = new_py

    # ── Tile effects ─────────────────────────────────────────────────────────

    def _check_tiles(self):
        col = self._px // SCALE
        row = self._py // SCALE
        t   = self._tile_at(col, row)

        if t == 'H':
            self._die()
        elif t == 'C':
            key = (row, col)
            if key not in self._collected:
                self._collected.add(key)
                self.game.score += 1
                self.hal.play_tone(880, 60)
        elif t == 'X':
            self._level_complete()

    def _die(self):
        if self._dying:
            return
        self._dying     = True
        self._die_timer = 800
        self.game.lives -= 1
        self.hal.play_tone(110, 400)
        self.hal.vibrate(duration_ms=200)

    def _level_complete(self):
        self.hal.play_tone(1047, 300)
        next_idx = self.game.level_idx + 1
        if next_idx < len(self.game.levels):
            self.game.level_idx = next_idx
            self.game.states.request_switch(PlayingState(self.game))
        else:
            self.game.states.request_switch(GameOverState(self.game, won=True))

    # ── Update ───────────────────────────────────────────────────────────────

    def update(self, dt):
        if self._dying:
            self._die_timer -= dt
            if self._die_timer <= 0:
                if self.game.lives <= 0:
                    self.game.states.request_switch(GameOverState(self.game, won=False))
                else:
                    self._respawn()
            return

        self._physics(dt)
        self._check_tiles()

    # ── Render ───────────────────────────────────────────────────────────────

    def render(self):
        hal = self.hal
        cam = self._cam_x

        _draw_sky(hal)

        # Tiles
        for sx in range(_W):
            lc = cam + sx
            for r in range(_H):
                t = self._tile_at(lc, r)
                if t == '#' or t == 'S':
                    hal.set_pixel(sx, r, _PLAT_C)
                elif t == 'H':
                    hal.set_pixel(sx, r, _HAZARD_C)
                elif t == 'C':
                    hal.set_pixel(sx, r, _COIN_C)
                elif t == 'X':
                    hal.set_pixel(sx, r, _EXIT_C)

        # Player
        px_s = self._px // SCALE - cam
        py_s = self._py // SCALE
        if 0 <= px_s < _W and 0 <= py_s < _H:
            if self._dying:
                if (self._die_timer // 80) % 2 == 0:
                    hal.set_pixel(px_s, py_s, RED)
            else:
                hal.set_pixel(px_s, py_s, _PLAYER_C)

        # Lives indicator: dim dots along the top edge
        lives = self.game.lives
        for i in range(lives if lives <= _W else _W):
            hal.set_pixel(i, 0, _LIFE_C)


# ─────────────────────────────────────────────────────────────────────────────
class GameOverState(GameState):
    """Score display after death or level clear. LEFT = launcher, A / DOWN = retry."""

    def __init__(self, game, won=False):
        super().__init__(game)
        self._won   = won
        self._timer = 0
        self._blink = True

    def on_enter(self):
        self._timer = 0

    def update(self, dt):
        self._timer += dt
        self._blink = (self._timer // 400) % 2 == 0
        if self._timer < 800:
            return   # brief lock-out so stray button releases don't skip screen
        if self.hal.is_pressed(LEFT):
            self.game.quit()
        elif self.hal.is_pressed(A) or self.hal.is_pressed(DOWN):
            self.game.level_idx = 0
            self.game.score     = 0
            self.game.lives     = 3
            self.game.states.request_switch(PlayingState(self.game))

    def render(self):
        hal   = self.hal
        score = self.game.score

        if self._blink:
            _draw_sky(hal)

        # Score digits (up to 3)
        s = str(score)
        if len(s) == 1:
            draw_char(hal, s[0], 4, 1, YELLOW)
        elif len(s) == 2:
            draw_char(hal, s[0], 1, 1, YELLOW)
            draw_char(hal, s[1], 5, 1, YELLOW)
        else:
            draw_char(hal, s[0], 0, 1, YELLOW)
            draw_char(hal, s[1], 4, 1, YELLOW)
            draw_char(hal, s[2], 8, 1, YELLOW)

        # "WIN" or "GO" label
        if self._won:
            draw_char(hal, 'W', 0, 6, CYAN)
            draw_char(hal, 'I', 4, 6, CYAN)
            draw_char(hal, 'N', 8, 6, CYAN)
        else:
            draw_char(hal, 'G', 1, 6, RED)
            draw_char(hal, 'O', 5, 6, RED)

        # Blink prompt dots
        if self._blink:
            hal.set_pixel(10, 7, WHITE)
            hal.set_pixel(11, 7, WHITE)
