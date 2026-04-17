# games/flappy/states.py
# MicroPython-compatible. All Flappy Bird game states.
#
# Layout (12 wide × 8 tall):
#   Bird: fixed at column 2, vertical position governed by physics.
#   Pipes: 1-pixel-wide vertical strips scrolling left; 3-row gap.
#   Score: count of pipes passed through.
#
# Controls:
#   Menu    : UP = back to launcher, A or DOWN = start
#   Game    : A or B = flap
#   GameOver: UP = back to launcher, DOWN = play again

import random
from lib.engine.state  import GameState
from lib.engine.colors import WHITE, YELLOW, RED, CYAN
from lib.engine.font   import draw_char
from lib.engine.sprite import SCALE
from lib.hal           import UP, DOWN, A, B

# ── Physics ───────────────────────────────────────────────────────────────────
# Values tuned for playability on the slow-refresh hardware:
#   - Gravity is gentle so the bird takes ~1s to fall 4 rows from rest.
#   - Max fall velocity limits terminal speed to ~1 px per 4 frames.
#   - Flap kick gives ~2.4 px rise per press — enough to cross a 3-row gap
#     with one flap but not so strong it overshoots into the top pipe.
_GRAVITY      = 10 * SCALE   # sub/s²  — downward acceleration
_FLAP_VEL     = -7 * SCALE   # sub/s   — velocity set on flap (upward)
_MAX_FALL_VEL =  7 * SCALE   # sub/s   — cap on downward velocity

# ── Bird ──────────────────────────────────────────────────────────────────────
_BIRD_X   = 2        # fixed horizontal column
_BIRD_C   = (255, 220, 0)   # yellow

# ── Pipes ─────────────────────────────────────────────────────────────────────
_GAP_H          = 3          # gap height in rows
_PIPE_SPACING   = 7 * SCALE  # sub-pixel gap between consecutive pipe left-edges
_INIT_SPEED     = 3 * SCALE  # sub/s  — initial leftward pipe speed
_MAX_SPEED      = 6 * SCALE  # sub/s  — max pipe speed
_SPEED_UP_EVERY = 5          # pipes scored before each speed increase
_SPEED_STEP     = SCALE // 2 # sub/s  — speed added per step

_PIPE_C = (0, 180, 0)   # green pipes

# ── Background ────────────────────────────────────────────────────────────────
_SKY_C = (0, 0, 25)


def _rand_gap(avoid):
    """Random gap_y in 1–4, different from avoid (prevents same gap twice)."""
    y = 1 + random.randint(0, 3)
    if y == avoid:
        y = (y % 4) + 1
    return y


def _draw_sky(hal):
    for y in range(8):
        for x in range(12):
            hal.set_pixel(x, y, _SKY_C)


class MenuState(GameState):
    """Title screen. UP = launcher, A / DOWN = start."""

    def __init__(self, game):
        super().__init__(game)
        self._timer  = 0
        self._blink  = True
        self._bird_y = 3 * SCALE
        self._bird_v = 0

    def on_enter(self):
        self._timer  = 0
        self._bird_y = 3 * SCALE
        self._bird_v = 0

    def update(self, dt):
        self._timer += dt
        self._blink  = (self._timer // 400) % 2 == 0

        # Animate bird bobbing up and down
        self._bird_v += _GRAVITY * dt // 1000
        if self._bird_v > _MAX_FALL_VEL:
            self._bird_v = _MAX_FALL_VEL
        self._bird_y += self._bird_v * dt // 1000
        by = self._bird_y // SCALE
        if by < 1:
            self._bird_y = 1 * SCALE
            self._bird_v = abs(self._bird_v)
        elif by > 5:
            self._bird_y = 5 * SCALE
            self._bird_v = -abs(self._bird_v)

        if self.hal.is_pressed(UP):
            self.game.quit()
        elif self.hal.is_pressed(A) or self.hal.is_pressed(DOWN):
            self.game.states.request_switch(PlayingState(self.game))

    def render(self):
        hal = self.hal
        _draw_sky(hal)
        by = self._bird_y // SCALE
        hal.set_pixel(_BIRD_X, by, _BIRD_C)
        draw_char(hal, 'F', 2, 5, CYAN)
        draw_char(hal, 'B', 6, 5, CYAN)
        if self._blink:
            hal.set_pixel(5, 7, WHITE)
            hal.set_pixel(6, 7, WHITE)


class PlayingState(GameState):
    """Main gameplay state."""

    def on_enter(self):
        self.game.score  = 0
        self._speed      = _INIT_SPEED
        self._bird_y     = 3 * SCALE
        self._bird_vel   = 0
        self._dead       = False
        self._dead_timer = 0
        # Bird holds still until the player's first flap press.
        # This gives the player time to get ready before gravity kicks in.
        self._waiting    = True
        self._wait_timer = 0

        # Edge-trigger for flap buttons
        self._pk_a = False
        self._pk_b = False

        # Two pipes cycling; first pipe starts far enough right to give
        # the player time to react before it arrives at the bird's column.
        g0 = _rand_gap(0)
        g1 = _rand_gap(g0)
        self._pipes = [
            {'x': 11 * SCALE,              'gap_y': g0, 'scored': False},
            {'x': 11 * SCALE + _PIPE_SPACING, 'gap_y': g1, 'scored': False},
        ]

    # ── Input / physics ──────────────────────────────────────────────────────

    def _flap(self):
        self._bird_vel = _FLAP_VEL
        self.hal.play_tone(440, 30)

    def _die(self):
        self._dead       = True
        self._dead_timer = 600
        self.hal.play_tone(110, 400)
        self.hal.vibrate(duration_ms=150)

    # ── Update ───────────────────────────────────────────────────────────────

    def update(self, dt):
        if self._dead:
            self._dead_timer -= dt
            if self._dead_timer <= 0:
                self.game.states.request_switch(
                    GameOverState(self.game, self.game.score)
                )
            return

        # Waiting for first flap — bird hovers, pipes not yet moving
        if self._waiting:
            self._wait_timer += dt
            a = self.hal.is_pressed(A)
            b = self.hal.is_pressed(B)
            if (a and not self._pk_a) or (b and not self._pk_b):
                self._waiting = False
                self._flap()
            self._pk_a = a
            self._pk_b = b
            return

        # Flap (edge-triggered: one flap per press)
        a = self.hal.is_pressed(A)
        b = self.hal.is_pressed(B)
        if (a and not self._pk_a) or (b and not self._pk_b):
            self._flap()
        self._pk_a = a
        self._pk_b = b

        # Bird physics
        self._bird_vel += _GRAVITY * dt // 1000
        if self._bird_vel > _MAX_FALL_VEL:
            self._bird_vel = _MAX_FALL_VEL
        self._bird_y += self._bird_vel * dt // 1000

        bird_y = self._bird_y // SCALE
        if bird_y < 0 or bird_y > 7:
            self._die()
            return

        # Scroll pipes and check collisions/score
        for pipe in self._pipes:
            prev_px = pipe['x'] // SCALE
            pipe['x'] -= self._speed * dt // 1000

            # Recycle pipe that has fully scrolled off left
            if pipe['x'] < 0:
                other = self._pipes[0] if pipe is self._pipes[1] else self._pipes[1]
                pipe['x'] = other['x'] + _PIPE_SPACING
                pipe['gap_y'] = _rand_gap(pipe['gap_y'])
                pipe['scored'] = False
                prev_px = pipe['x'] // SCALE   # reset — no collision from recycled pipe

            curr_px = pipe['x'] // SCALE

            # Collision: the pipe passed through or is at the bird's column this frame.
            # Check prev_px too because the pipe can jump a pixel boundary mid-frame.
            if curr_px <= _BIRD_X <= prev_px:
                gap_y = pipe['gap_y']
                if bird_y < gap_y or bird_y >= gap_y + _GAP_H:
                    self._die()
                    return

            # Score: pipe has just passed the bird's column
            if not pipe['scored'] and curr_px < _BIRD_X:
                pipe['scored'] = True
                self.game.score += 1
                self.hal.play_tone(660, 60)
                if self.game.score % _SPEED_UP_EVERY == 0:
                    self._speed = min(_MAX_SPEED, self._speed + _SPEED_STEP)

    # ── Render ───────────────────────────────────────────────────────────────

    def render(self):
        hal = self.hal
        _draw_sky(hal)

        # Pipes
        for pipe in self._pipes:
            px = pipe['x'] // SCALE
            if 0 <= px <= 11:
                gap_y = pipe['gap_y']
                for y in range(8):
                    if y < gap_y or y >= gap_y + _GAP_H:
                        hal.set_pixel(px, y, _PIPE_C)

        # Bird
        bird_y = self._bird_y // SCALE
        if 0 <= bird_y <= 7:
            if self._dead:
                if (self._dead_timer // 80) % 2 == 0:
                    hal.set_pixel(_BIRD_X, bird_y, RED)
            elif self._waiting:
                # Blink the bird while waiting for first flap
                if (self._wait_timer // 300) % 2 == 0:
                    hal.set_pixel(_BIRD_X, bird_y, _BIRD_C)
            else:
                hal.set_pixel(_BIRD_X, bird_y, _BIRD_C)

        # Score tally: one white dot per point in the top-right corner (max 8).
        # Full numeric score is shown on the game-over screen.
        dots = min(self.game.score, 8)
        for i in range(dots):
            hal.set_pixel(11 - i, 0, WHITE)


class GameOverState(GameState):
    """Score display. UP = launcher, DOWN = play again."""

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
            _draw_sky(hal)

        s = str(self._score)
        n = len(s)
        if n == 1:
            draw_char(hal, s[0], 4, 1, YELLOW)
        elif n == 2:
            draw_char(hal, s[0], 1, 1, YELLOW)
            draw_char(hal, s[1], 5, 1, YELLOW)
        else:
            draw_char(hal, s[0], 0, 1, YELLOW)
            draw_char(hal, s[1], 4, 1, YELLOW)
            draw_char(hal, s[2], 8, 1, YELLOW)

        draw_char(hal, 'G', 0, 6, _BIRD_C)
        draw_char(hal, 'O', 4, 6, _BIRD_C)

        if self._blink:
            hal.set_pixel(10, 7, WHITE)
            hal.set_pixel(11, 7, WHITE)
