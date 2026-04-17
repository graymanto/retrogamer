# games/snake/states.py
# MicroPython-compatible. All Snake game states.
#
# Differences from the original Kitronik snake:
#   - Ported to the HAL / BaseGame / StateMachine framework.
#   - Food is never placed on the snake body (original bug fixed).
#   - Scoring: +1 per food eaten, shown on the game-over screen.
#   - Speed increases with score (capped at a minimum step interval).
#   - No threading — input is polled each frame inside update().
#   - LEFT on title / game-over screen returns to the launcher.

from random import randint

from lib.engine.state  import GameState
from lib.engine.colors import GREEN, CYAN, WHITE, RED, YELLOW, DIM_WHITE
from lib.engine.font   import draw_char, draw_text
from lib.hal           import UP, DOWN, LEFT, RIGHT, A

# Snake colours
HEAD_COLOR = GREEN           # bright head
BODY_COLOR = CYAN            # distinct body

# Tone frequencies
NOTE_EAT  = 880
NOTE_DIE  = 110


class MenuState(GameState):
    """
    Snake title screen.
    Shows a demo snake looping a rectangular path.
    A = start game, LEFT = back to launcher.
    """

    # Clockwise rectangular loop in the centre of the 12x8 grid.
    # 20 positions total; the demo snake body trails 4 steps behind the head.
    _PATH = (
        (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2), (9, 2),
        (9, 3), (9, 4), (9, 5),
        (8, 5), (7, 5), (6, 5), (5, 5), (4, 5), (3, 5), (2, 5),
        (2, 4), (2, 3),
    )
    _DEMO_BODY_LEN = 4

    def __init__(self, game):
        super().__init__(game)
        self._timer      = 0
        self._blink      = True
        self._path_idx   = 0
        self._step_timer = 0

    def on_enter(self):
        self._timer    = 0
        self._path_idx = 0

    def update(self, dt):
        self._timer      += dt
        self._blink       = (self._timer // 400) % 2 == 0
        self._step_timer  += dt

        if self._step_timer >= 150:
            self._step_timer  -= 150
            n = len(self._PATH)
            self._path_idx = (self._path_idx + 1) % n

        if self.hal.is_pressed(LEFT):
            self.game.quit()   # return to launcher
        elif self.hal.is_pressed(A):
            self.game.states.request_switch(PlayingState(self.game))

    def render(self):
        hal = self.hal
        n   = len(self._PATH)
        idx = self._path_idx

        # Demo snake body (trails behind head along the path)
        for i in range(1, self._DEMO_BODY_LEN + 1):
            bx, by = self._PATH[(idx - i) % n]
            hal.set_pixel(bx, by, BODY_COLOR)

        # Demo snake head (drawn last so it sits on top)
        hx, hy = self._PATH[idx]
        hal.set_pixel(hx, hy, HEAD_COLOR)

        # Blinking "press A" indicator at row 7
        if self._blink:
            hal.set_pixel(5, 7, HEAD_COLOR)
            hal.set_pixel(6, 7, HEAD_COLOR)


class PlayingState(GameState):
    """
    Main Snake gameplay.

    Controls: UP/DOWN/LEFT/RIGHT to steer.
    The snake wraps at all four edges (no wall death).
    Speed starts at 300 ms/step and decreases by 10 ms per food eaten,
    capped at a minimum of 120 ms/step.
    """

    _MOVE_START   = 300   # ms per step at the beginning
    _MOVE_MIN     = 120   # fastest the game can get
    _MOVE_STEP    = 10    # ms shaved off per food eaten

    def on_enter(self):
        # Snake starts at the centre, one cell long, moving right.
        self._head     = [6, 4]
        self._body     = []             # list of [x, y] — head is NOT in body
        self._dir      = (1, 0)         # current movement direction
        self._next_dir = (1, 0)         # direction applied on the next step
        self._score    = 0
        self._move_timer    = 0
        self._move_interval = self._MOVE_START
        self._food     = self._place_food()
        self._start_delay   = 300       # pause before first move (ms)

    # ------------------------------------------------------------------
    # Food placement — never spawns on the snake (fixes original bug)
    # ------------------------------------------------------------------

    def _place_food(self):
        """Return a random [x, y] that is not occupied by the snake."""
        while True:
            x = randint(0, 11)
            y = randint(0, 7)
            if x == self._head[0] and y == self._head[1]:
                continue
            if not any(p[0] == x and p[1] == y for p in self._body):
                return [x, y]

    # ------------------------------------------------------------------
    # Update / step logic
    # ------------------------------------------------------------------

    def update(self, dt):
        hal = self.hal

        # Direction input — queued for next step; 180° reversal is rejected
        # by checking against the *current* direction, not the queued one.
        if hal.is_pressed(UP) and self._dir != (0, 1):
            self._next_dir = (0, -1)
        elif hal.is_pressed(DOWN) and self._dir != (0, -1):
            self._next_dir = (0, 1)
        elif hal.is_pressed(LEFT) and self._dir != (1, 0):
            self._next_dir = (-1, 0)
        elif hal.is_pressed(RIGHT) and self._dir != (-1, 0):
            self._next_dir = (1, 0)

        # Brief pause before first move so the player can orient
        if self._start_delay > 0:
            self._start_delay -= dt
            return

        self._move_timer += dt
        while self._move_timer >= self._move_interval:
            self._move_timer -= self._move_interval
            self._step()

    def _step(self):
        """Advance the snake by one cell."""
        self._dir = self._next_dir

        # New head position with wraparound
        nx = (self._head[0] + self._dir[0]) % 12
        ny = (self._head[1] + self._dir[1]) % 8

        # Self-collision check
        if any(p[0] == nx and p[1] == ny for p in self._body):
            self.hal.play_tone(NOTE_DIE, 400)
            self.hal.vibrate(duration_ms=200)
            self.game.states.request_switch(
                GameOverState(self.game, self._score)
            )
            return

        # Shift body: push old head position onto front, remove tail
        self._body.insert(0, [self._head[0], self._head[1]])
        self._head = [nx, ny]

        # Food check
        if self._head[0] == self._food[0] and self._head[1] == self._food[1]:
            # Grow (tail already inserted above, just don't pop it)
            self._score        += 1
            self._food          = self._place_food()
            self._move_interval = max(self._MOVE_MIN,
                                      self._MOVE_START - self._score * self._MOVE_STEP)
            self.hal.play_tone(NOTE_EAT, 60)
        else:
            # Move (remove tail to keep length constant)
            self._body.pop()

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def render(self):
        hal = self.hal

        # Food drawn first (behind everything else)
        hal.set_pixel(self._food[0], self._food[1], WHITE)

        # Snake body
        for part in self._body:
            hal.set_pixel(part[0], part[1], BODY_COLOR)

        # Snake head drawn last — always visible even at food position
        # (shouldn't overlap food thanks to _place_food, but belt-and-braces)
        hal.set_pixel(self._head[0], self._head[1], HEAD_COLOR)


class GameOverState(GameState):
    """
    Displayed when the snake collides with itself.
    Shows the score; A = play again, LEFT = back to launcher.
    """

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
            self.game.quit()   # return to launcher
        elif self._timer > 800 and self.hal.is_pressed(A):
            self.game.states.request_switch(MenuState(self.game))

    def render(self):
        hal = self.hal

        # Flashing red background
        if self._blink:
            for y in range(8):
                for x in range(12):
                    hal.set_pixel(x, y, (40, 0, 0))

        # Score — up to 3 digits, centred
        s = str(self._score)
        if len(s) == 1:
            draw_char(hal, s, 4, 1, YELLOW)
        elif len(s) == 2:
            draw_char(hal, s[0], 1, 1, YELLOW)
            draw_char(hal, s[1], 5, 1, YELLOW)
        else:
            draw_char(hal, s[0], 0, 1, YELLOW)
            draw_char(hal, s[1], 4, 1, YELLOW)
            draw_char(hal, s[2], 8, 1, YELLOW)

        # "GO" — game over hint at bottom-left
        draw_char(hal, "G", 0, 6, RED)
        draw_char(hal, "O", 4, 6, RED)

        # Blinking "press A" prompt
        if self._blink:
            hal.set_pixel(10, 7, YELLOW)
            hal.set_pixel(11, 7, YELLOW)
