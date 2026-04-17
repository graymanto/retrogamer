# games/simon/states.py
# MicroPython-compatible. All Simon Says game states.
#
# Display layout (12 wide × 8 tall) — four colour quadrants:
#
#   ┌─────────┬──────────┐
#   │ RED     │ BLUE     │  rows 0-3
#   │  (UP)   │ (RIGHT)  │
#   ├─────────┼──────────┤
#   │ GREEN   │ YELLOW   │  rows 4-7
#   │ (DOWN)  │   (A)    │
#   └─────────┴──────────┘
#    cols 0-5   cols 6-11
#
# Playback: each element lights its quadrant and plays a tone for LIT_MS,
# then a GAP_MS dark pause before the next. A PRE_DELAY before the first
# element gives the player a moment to focus.
#
# Input: player presses the matching button for each element in order.
# Wrong press → game over. Score = number of rounds fully completed.
#
# UP on menu / game-over → back to launcher.  DOWN or A = start / play again.

from random import randint

from lib.engine.state  import GameState
from lib.engine.colors import RED, BLUE, GREEN, YELLOW, WHITE, DIM_WHITE
from lib.engine.font   import draw_char
from lib.hal           import UP, DOWN, LEFT, RIGHT, A, B

# ── Zone definitions ──────────────────────────────────────────────────────────

# Zone index → button, display region (x0,y0,x1,y1), bright colour, dim colour, tone (Hz)
# Mapping mirrors the screen layout: LEFT=top-left, RIGHT=top-right, A=bottom-left, B=bottom-right
_BUTTONS = (LEFT, RIGHT, A, B)

_BOUNDS = (
    (0,  0, 5, 3),   # zone 0: RED    top-left
    (6,  0, 11, 3),  # zone 1: BLUE   top-right
    (0,  4, 5, 7),   # zone 2: GREEN  bottom-left
    (6,  4, 11, 7),  # zone 3: YELLOW bottom-right
)

_COLORS = (RED, BLUE, GREEN, YELLOW)

_DIM = (
    (35,  0,  0),   # dim red
    ( 0,  0, 45),   # dim blue
    ( 0, 35,  0),   # dim green
    (45, 40,  0),   # dim yellow
)

_TONES = (392, 523, 659, 784)   # G4, C5, E5, G5

NOTE_WRONG = 120   # low buzz for wrong answer

# ── Playback timing (ms) ──────────────────────────────────────────────────────
_PRE_DELAY_MS = 700    # pause before first element in a round
_LIT_MS       = 420    # each element shown for this long
_GAP_MS       = 160    # dark gap between elements
_INPUT_GUARD  = 300    # debounce after transitioning to input phase

# ── Phase constants ───────────────────────────────────────────────────────────
_PHASE_PLAYBACK  = 0
_PHASE_INPUT     = 1
_PHASE_WIN_FLASH = 2


def _draw_zone(hal, zone, lit):
    """Fill a zone quadrant with its bright or dim colour."""
    x0, y0, x1, y1 = _BOUNDS[zone]
    color = _COLORS[zone] if lit else _DIM[zone]
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            hal.set_pixel(x, y, color)


class MenuState(GameState):
    """
    Simon title screen.
    Cycles through each zone in order to demonstrate the game.
    DOWN = start, UP = back to launcher.
    Controls: LEFT=top-left, RIGHT=top-right, A(Z)=bottom-left, B(X)=bottom-right.
    """

    def __init__(self, game):
        super().__init__(game)
        self._timer    = 0
        self._blink    = True

    def on_enter(self):
        self._timer = 0

    def update(self, dt):
        self._timer += dt
        self._blink  = (self._timer // 400) % 2 == 0

        if self.hal.is_pressed(UP):
            self.game.quit()
        elif self.hal.is_pressed(DOWN):
            self.game.states.request_switch(PlayingState(self.game))

    def render(self):
        hal      = self.hal
        demo_idx = (self._timer // 500) % 4   # cycle zone 0→1→2→3→0…

        for zone in range(4):
            _draw_zone(hal, zone, lit=(zone == demo_idx))

        # Blinking "press A" dots centred at bottom of each bottom zone
        if self._blink:
            hal.set_pixel(2,  7, WHITE)
            hal.set_pixel(9, 7, WHITE)


class PlayingState(GameState):
    """Simon gameplay. Sequence grows by one each round."""

    def on_enter(self):
        self.game.score    = 0
        self._sequence     = []
        self._rounds_done  = 0
        self._lit_zone     = -1    # which zone is highlighted (-1 = none)
        self._all_flash    = False  # True during win flash
        self._phase        = _PHASE_PLAYBACK
        self._phase_timer  = 0
        self._playback_idx = 0
        self._input_idx    = 0
        self._debounce     = 0
        self._start_new_round()

    # ── Round management ─────────────────────────────────────────────────────

    def _start_new_round(self):
        self._sequence.append(randint(0, 3))
        self._playback_idx = 0
        self._input_idx    = 0
        self._lit_zone     = -1
        self._all_flash    = False
        self._phase        = _PHASE_PLAYBACK
        self._phase_timer  = _PRE_DELAY_MS   # initial pause before first element

    # ── Update ───────────────────────────────────────────────────────────────

    def update(self, dt):
        self._debounce = max(0, self._debounce - dt)

        if self._phase == _PHASE_PLAYBACK:
            self._update_playback(dt)
        elif self._phase == _PHASE_INPUT:
            self._update_input(dt)
        elif self._phase == _PHASE_WIN_FLASH:
            self._update_win_flash(dt)

    def _update_playback(self, dt):
        self._phase_timer -= dt
        if self._phase_timer > 0:
            return

        if self._lit_zone >= 0:
            # Finished showing an element — enter gap
            self._lit_zone = -1
            self._playback_idx += 1
            if self._playback_idx >= len(self._sequence):
                # Full sequence played → switch to input
                self._phase       = _PHASE_INPUT
                self._debounce    = _INPUT_GUARD
            else:
                self._phase_timer = _GAP_MS
        else:
            # Finished a gap (or pre-delay) — show next element
            z = self._sequence[self._playback_idx]
            self._lit_zone    = z
            self._phase_timer = _LIT_MS
            self.hal.play_tone(_TONES[z], _LIT_MS - 40)

    def _update_input(self, dt):
        if self._debounce > 0:
            return

        hal     = self.hal
        pressed = -1
        for z, btn in enumerate(_BUTTONS):
            if hal.is_pressed(btn):
                pressed = z
                break

        if pressed < 0:
            return

        self._debounce = 200   # prevent double-press

        if pressed == self._sequence[self._input_idx]:
            # Correct press — briefly light the zone
            self._lit_zone = pressed
            hal.play_tone(_TONES[pressed], 150)
            hal.vibrate(duration_ms=40)
            self._input_idx += 1

            if self._input_idx >= len(self._sequence):
                # Round complete
                self._rounds_done     += 1
                self.game.score        = self._rounds_done
                self._phase            = _PHASE_WIN_FLASH
                self._phase_timer      = 700
                self._lit_zone         = -1
        else:
            # Wrong — game over
            hal.play_tone(NOTE_WRONG, 500)
            hal.vibrate(duration_ms=200)
            self.game.states.request_switch(
                GameOverState(self.game, self._rounds_done)
            )

    def _update_win_flash(self, dt):
        self._phase_timer -= dt
        self._all_flash    = (self._phase_timer // 100) % 2 == 0
        if self._phase_timer <= 0:
            self._all_flash = False
            self._start_new_round()

    # ── Render ────────────────────────────────────────────────────────────────

    def render(self):
        hal = self.hal
        for zone in range(4):
            lit = self._all_flash or (zone == self._lit_zone)
            _draw_zone(hal, zone, lit)


class GameOverState(GameState):
    """
    Shown when the player presses the wrong zone.
    Score = rounds fully completed. A = play again, LEFT = launcher.
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

        if self._timer > 800 and self.hal.is_pressed(UP):
            self.game.quit()
        elif self._timer > 800 and self.hal.is_pressed(DOWN):
            self.game.states.request_switch(PlayingState(self.game))

    def render(self):
        hal = self.hal

        # Flash all zones dim red on blink beats
        for zone in range(4):
            color = (40, 0, 0) if self._blink else _DIM[zone]
            x0, y0, x1, y1 = _BOUNDS[zone]
            for y in range(y0, y1 + 1):
                for x in range(x0, x1 + 1):
                    hal.set_pixel(x, y, color)

        # Score — up to 2 digits, centred
        s = str(self._score)
        if len(s) == 1:
            draw_char(hal, s, 4, 2, YELLOW)
        else:
            draw_char(hal, s[0], 1, 2, YELLOW)
            draw_char(hal, s[1], 5, 2, YELLOW)

        # Blinking "press A" indicator
        if self._blink:
            hal.set_pixel(10, 7, WHITE)
            hal.set_pixel(11, 7, WHITE)
