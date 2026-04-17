# games/frogger/states.py
# MicroPython-compatible. All Frogger game states.
#
# Layout (12 wide × 8 tall):
#   Row 0: goal  — water with 5 lily pads (visual only; any column scores)
#   Row 1: river — logs drift RIGHT (fast)
#   Row 2: river — logs drift LEFT  (medium)
#   Row 3: river — logs drift RIGHT (slow, more logs)
#   Row 4: safe bank (median)
#   Row 5: road  — cars drift LEFT  (fast)
#   Row 6: road  — cars drift RIGHT (slow)
#   Row 7: start bank (safe)
#
# Movement: UP/DOWN/LEFT/RIGHT hop one cell, edge-triggered (one hop per press).
# River: frog must be on a log or it drowns.
# Road: frog must not overlap a car or it dies.
# Goal row: any column scores.
#
# Levels: every 3 crossings all lanes speed up by 1 px/s (max level 5).
# Level flash shows for 800 ms after each level-up.
# Level and crossings persist across deaths within a game.
#
# Lives: 3.  Score = successful crossings.
# UP = quit to launcher (menu/game-over).  DOWN = start/retry.

from lib.engine.state  import GameState
from lib.engine.colors import WHITE, RED, YELLOW
from lib.engine.font   import draw_char
from lib.engine.sprite import SCALE
from lib.hal           import UP, DOWN, LEFT, RIGHT

# ── Colors ────────────────────────────────────────────────────────────────────
_FROG_C  = (255, 220,  0)   # bright yellow — contrasts against all surface colours
_WATER_C = (0,    0,  60)
_BANK_C  = (0,   50,   0)
_ROAD_C  = (30,  30,  30)
_LOG_C   = (130, 80,  15)
_CAR1_C  = (220,  0,   0)   # left-moving cars
_CAR2_C  = (255, 120,  0)   # right-moving cars
_PAD_C   = (0,   90,   0)   # lily pad decoration

# ── Map ───────────────────────────────────────────────────────────────────────
_GOAL_ROW   = 0
_RIVER_ROWS = (1, 2, 3)
_BANK_ROW   = 4
_ROAD_ROWS  = (5, 6)
_START_ROW  = 7
_PAD_COLS   = (1, 3, 5, 7, 9)   # visual decoration only

# ── Level system ──────────────────────────────────────────────────────────────
_CROSSINGS_PER_LEVEL = 3   # crossings before advancing one level

# Each level is a full lane config: (row, is_water, dir, speed_px_s, obj_w, init_xs)
# Variety comes from object counts, widths, AND directions — not just speed.
#
# L1 → L2: one extra car on the slow lane
# L2 → L3: logs narrow (w3→w2), fast-lane cars widen (w1→w2) — different feel
# L3 → L4: all three river lanes flip direction — muscle memory reset
# L4 → L5: 4 cars on the fast lane, highest speeds
_LEVEL_CONFIGS = (
    # ── Level 1: intro ────────────────────────────────────────────────────────
    (
        (1, True,  +1, 4, 3, (0, 7)),       # wide logs rightward  (2 logs)
        (2, True,  -1, 3, 3, (2, 8)),       # wide logs leftward   (2 logs)
        (3, True,  +1, 2, 2, (0, 4, 8)),    # medium logs right    (3 logs)
        (5, False, -1, 4, 1, (0, 4, 8)),    # thin cars left       (3 cars)
        (6, False, +1, 3, 1, (1, 7)),       # thin cars right      (2 cars)
    ),
    # ── Level 2: one extra car, mild speed bump ───────────────────────────────
    (
        (1, True,  +1, 4, 3, (0, 7)),
        (2, True,  -1, 4, 3, (2, 8)),
        (3, True,  +1, 3, 2, (0, 4, 8)),
        (5, False, -1, 5, 1, (0, 4, 8)),
        (6, False, +1, 3, 1, (0, 4, 8)),    # 3rd car added ← change
    ),
    # ── Level 3: shorter logs, wider cars (structure not speed) ───────────────
    (
        (1, True,  +1, 4, 2, (0, 6)),       # logs narrowed w3→w2 ← change
        (2, True,  -1, 4, 2, (2, 8)),       # logs narrowed        ← change
        (3, True,  +1, 3, 2, (0, 4, 8)),
        (5, False, -1, 5, 2, (0, 4, 8)),    # cars widened w1→w2  ← change
        (6, False, +1, 4, 1, (0, 4, 8)),
    ),
    # ── Level 4: all river directions flip (muscle-memory reset) ──────────────
    (
        (1, True,  -1, 4, 2, (0, 6)),       # was rightward → now LEFT  ← change
        (2, True,  +1, 4, 2, (2, 8)),       # was leftward  → now RIGHT ← change
        (3, True,  -1, 3, 2, (0, 4, 8)),    # was rightward → now LEFT  ← change
        (5, False, -1, 5, 2, (0, 4, 8)),
        (6, False, +1, 4, 2, (0, 4, 8)),    # 3 wide cars
    ),
    # ── Level 5: 4 cars on fast lane, gentle overall speed increase ───────────
    (
        (1, True,  -1, 5, 2, (0, 6)),
        (2, True,  +1, 4, 2, (2, 8)),
        (3, True,  -1, 3, 2, (0, 4, 8)),
        (5, False, -1, 6, 1, (0, 3, 6, 9)), # 4 cars! ← change
        (6, False, +1, 5, 2, (1, 7)),
    ),
)

_MAX_LEVEL = len(_LEVEL_CONFIGS)

# Colour shown for the level-up flash, one per level
_LEVEL_FLASH_COLORS = (
    (0,   200,  0),    # L1 green  (unused — level-up shows the NEW level)
    (220, 200,  0),    # L2 yellow
    (255, 100,  0),    # L3 orange
    (255,  0,   0),    # L4 red
    (220,  0,  220),   # L5 magenta
)


def _obj_covers(pos_sub, obj_w, frog_x):
    """True if an object (sub-pixel pos_sub, width obj_w) covers pixel col frog_x."""
    px = pos_sub // SCALE
    for dx in range(obj_w):
        if (px + dx) % 12 == frog_x:
            return True
    return False


def _draw_bg(hal):
    """Draw static background rows."""
    for x in range(12):
        hal.set_pixel(x, _GOAL_ROW, _WATER_C)
    for row in _RIVER_ROWS:
        for x in range(12):
            hal.set_pixel(x, row, _WATER_C)
    for x in range(12):
        hal.set_pixel(x, _BANK_ROW, _BANK_C)
    for row in _ROAD_ROWS:
        for x in range(12):
            hal.set_pixel(x, row, _ROAD_C)
    for x in range(12):
        hal.set_pixel(x, _START_ROW, _BANK_C)
    for px in _PAD_COLS:
        hal.set_pixel(px, _GOAL_ROW, _PAD_C)


class MenuState(GameState):
    """
    Frogger title screen. Shows map with a pixel frog hopping upward.
    DOWN = start, UP = back to launcher.
    """

    def __init__(self, game):
        super().__init__(game)
        self._timer  = 0
        self._blink  = True
        self._demo_y = _START_ROW
        self._hop_t  = 0

    def on_enter(self):
        self._timer  = 0
        self._demo_y = _START_ROW
        self._hop_t  = 0

    def update(self, dt):
        self._timer += dt
        self._blink  = (self._timer // 400) % 2 == 0

        self._hop_t += dt
        if self._hop_t >= 380:
            self._hop_t -= 380
            self._demo_y -= 1
            if self._demo_y < 0:
                self._demo_y = _START_ROW

        if self.hal.is_pressed(UP):
            self.game.quit()
        elif self.hal.is_pressed(DOWN):
            self.game.states.request_switch(PlayingState(self.game))

    def render(self):
        hal = self.hal
        _draw_bg(hal)
        hal.set_pixel(5, self._demo_y, _FROG_C)
        if self._blink:
            hal.set_pixel(5, _START_ROW, WHITE)
            hal.set_pixel(6, _START_ROW, WHITE)


class PlayingState(GameState):
    """Main Frogger gameplay with level progression."""

    def on_enter(self):
        self.game.score = 0
        self.game.lives = 3
        self._level     = 1
        self._crossings = 0
        self._level_flash       = 0
        self._level_flash_color = _LEVEL_FLASH_COLORS[0]

        self._build_lanes(1)

        self._frog_x   = 5
        self._frog_y   = _START_ROW
        self._drift    = 0

        self._dead         = False
        self._dead_timer   = 0
        self._win          = False
        self._win_timer    = 0
        # Short immunity after landing on a river row: absorbs the 1-frame
        # sub-pixel lag between log position and frog drift on entry.
        self._river_grace  = 0

        # Edge-trigger keys
        self._pk_up    = False
        self._pk_down  = False
        self._pk_left  = False
        self._pk_right = False

    # ── Level management ─────────────────────────────────────────────────────

    def _build_lanes(self, level):
        """Construct lane state from the config for the given level."""
        self._lanes = []
        for row, is_water, direction, speed, obj_w, init_xs in _LEVEL_CONFIGS[level - 1]:
            color = _LOG_C if is_water else (_CAR1_C if direction < 0 else _CAR2_C)
            self._lanes.append({
                'row':   row,
                'water': is_water,
                'dir':   direction,
                'speed': speed * SCALE,
                'w':     obj_w,
                'pos':   [x * SCALE for x in init_xs],
                'color': color,
            })

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _lane_for_row(self, row):
        for lane in self._lanes:
            if lane['row'] == row:
                return lane
        return None

    def _on_log(self, row, frog_x):
        lane = self._lane_for_row(row)
        if lane is None:
            return False
        w = lane['w']
        for pos in lane['pos']:
            px = pos // SCALE
            for dx in range(w):
                if (px + dx) % 12 == frog_x:
                    return True
        return False

    def _hit_car(self, row, frog_x):
        lane = self._lane_for_row(row)
        if lane is None:
            return False
        for pos in lane['pos']:
            if _obj_covers(pos, lane['w'], frog_x):
                return True
        return False

    def _kill_frog(self):
        self._dead       = True
        self._dead_timer = 700
        self.hal.play_tone(110, 400)
        self.hal.vibrate(duration_ms=200)

    # ── Update ───────────────────────────────────────────────────────────────

    def update(self, dt):
        self._update_lanes(dt)

        if self._dead:
            self._update_dead(dt)
            return
        if self._win:
            self._update_win(dt)
            return

        # Level-up announcement: keep lanes moving and drift running,
        # but block player input so they can read the level number.
        if self._level_flash > 0:
            self._level_flash -= dt
            self._update_drift(dt)
            return

        self._update_input()
        self._update_drift(dt)
        self._check_hazards()

    def _update_lanes(self, dt):
        for lane in self._lanes:
            vel   = lane['dir'] * lane['speed']
            obj_w = lane['w']
            for i in range(len(lane['pos'])):
                lane['pos'][i] += vel * dt // 1000
                if lane['dir'] > 0 and lane['pos'][i] >= 12 * SCALE:
                    lane['pos'][i] -= 12 * SCALE
                elif lane['dir'] < 0 and lane['pos'][i] < -obj_w * SCALE:
                    lane['pos'][i] += 12 * SCALE

    def _update_input(self):
        hal  = self.hal
        up   = hal.is_pressed(UP)
        down = hal.is_pressed(DOWN)
        left = hal.is_pressed(LEFT)
        rght = hal.is_pressed(RIGHT)

        moved = False
        if up and not self._pk_up:
            new_y = self._frog_y - 1
            if new_y >= _GOAL_ROW:
                self._frog_y = new_y
                self._drift  = 0
                if new_y in _RIVER_ROWS:
                    self._river_grace = 2
                moved = True
        elif down and not self._pk_down:
            new_y = self._frog_y + 1
            if new_y <= _START_ROW:
                self._frog_y = new_y
                self._drift  = 0
                if new_y in _RIVER_ROWS:
                    self._river_grace = 2
                moved = True
        elif left and not self._pk_left:
            new_x = self._frog_x - 1
            if new_x >= 0:
                self._frog_x = new_x
                moved = True
        elif rght and not self._pk_right:
            new_x = self._frog_x + 1
            if new_x <= 11:
                self._frog_x = new_x
                moved = True

        if moved:
            hal.play_tone(440, 25)

        self._pk_up    = up
        self._pk_down  = down
        self._pk_left  = left
        self._pk_right = rght

    def _update_drift(self, dt):
        """When on a river row, frog drifts with its log lane."""
        if self._frog_y not in _RIVER_ROWS:
            return
        lane = self._lane_for_row(self._frog_y)
        if lane is None:
            return
        self._drift += lane['dir'] * lane['speed'] * dt // 1000
        # Wrap frog_x so it follows logs that scroll off screen edges.
        while self._drift >= SCALE:
            self._frog_x = (self._frog_x + 1) % 12
            self._drift  -= SCALE
        while self._drift <= -SCALE:
            self._frog_x = (self._frog_x - 1) % 12
            self._drift  += SCALE

    def _check_hazards(self):
        fx = self._frog_x
        fy = self._frog_y

        # Goal row — any column is a crossing (pads are visual only)
        if fy == _GOAL_ROW:
            self._win        = True
            self._win_timer  = 500
            self.game.score += 1
            self._crossings += 1
            self.hal.play_tone(880, 200)
            self.hal.vibrate(duration_ms=80)

            # Level up every N crossings, up to _MAX_LEVEL
            if self._crossings % _CROSSINGS_PER_LEVEL == 0 and self._level < _MAX_LEVEL:
                self._level += 1
                self._build_lanes(self._level)   # rebuild with new widths/counts/dirs
                self._level_flash_color = _LEVEL_FLASH_COLORS[self._level - 1]
                self._level_flash = 800          # shown after the win animation
                self.hal.play_tone(1047, 150)    # high-C fanfare
            return

        if fy in _RIVER_ROWS:
            if self._river_grace > 0:
                self._river_grace -= 1
            elif not self._on_log(fy, fx):
                self._kill_frog()
            return

        if fy in _ROAD_ROWS:
            if self._hit_car(fy, fx):
                self._kill_frog()

    def _update_dead(self, dt):
        self._dead_timer -= dt
        if self._dead_timer <= 0:
            self._dead = False
            self.game.lives -= 1
            if self.game.lives <= 0:
                self.game.states.request_switch(
                    GameOverState(self.game, self.game.score)
                )
            else:
                self._frog_x = 5
                self._frog_y = _START_ROW
                self._drift  = 0

    def _update_win(self, dt):
        self._win_timer -= dt
        if self._win_timer <= 0:
            self._win    = False
            self._frog_x = 5
            self._frog_y = _START_ROW
            self._drift  = 0

    # ── Render ────────────────────────────────────────────────────────────────

    def render(self):
        hal = self.hal

        _draw_bg(hal)

        # Lane objects
        for lane in self._lanes:
            row   = lane['row']
            color = lane['color']
            obj_w = lane['w']
            for pos in lane['pos']:
                px = pos // SCALE
                for dx in range(obj_w):
                    hal.set_pixel((px + dx) % 12, row, color)

        # Frog
        if self._dead:
            if (self._dead_timer // 80) % 2 == 0:
                hal.set_pixel(self._frog_x, self._frog_y, RED)
        elif self._win:
            if (self._win_timer // 80) % 2 == 0:
                hal.set_pixel(self._frog_x, self._frog_y, WHITE)
        else:
            hal.set_pixel(self._frog_x, self._frog_y, _FROG_C)

        # Lives dots on start bank
        for i in range(self.game.lives):
            hal.set_pixel(11 - i * 2, _START_ROW, YELLOW)

        # Level-up flash overlay: shown after win animation while input is blocked.
        # Colour encodes the new level (yellow→orange→red→magenta).
        if not self._win and self._level_flash > 0:
            c = self._level_flash_color
            draw_char(hal, 'L', 2, 2, c)
            draw_char(hal, str(self._level), 6, 2, c)


class GameOverState(GameState):
    """Score display. DOWN = play again, UP = back to launcher."""

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

        if self._timer > 800 and self.hal.is_pressed(UP):
            self.game.quit()
        elif self._timer > 800 and self.hal.is_pressed(DOWN):
            self.game.states.request_switch(PlayingState(self.game))

    def render(self):
        hal = self.hal

        if self._blink:
            for y in range(8):
                for x in range(12):
                    hal.set_pixel(x, y, _WATER_C)

        s = str(self._score)
        if len(s) == 1:
            draw_char(hal, s, 4, 1, YELLOW)
        else:
            draw_char(hal, s[0], 1, 1, YELLOW)
            draw_char(hal, s[1], 5, 1, YELLOW)

        draw_char(hal, 'G', 0, 6, _FROG_C)
        draw_char(hal, 'O', 4, 6, _FROG_C)

        if self._blink:
            hal.set_pixel(10, 7, WHITE)
            hal.set_pixel(11, 7, WHITE)
