# games/launcher/game.py
# MicroPython-compatible. Boot screen for selecting a game.
#
# Controls:
#   LEFT / RIGHT  — scroll through games
#   A             — launch selected game
#
# Display layout (12x8):
#   Row 0    : position indicator dots (one per game, current highlighted)
#   Rows 1-5 : two-char game label centred (e.g. "PG" for Pong, "SI" for Space Invaders)
#   Row 6    : (blank)
#   Row 7    : blinking dots — press A to launch
#
#   Col 0-1  : left arrow < (visible when a previous game exists)
#   Col 10-11: right arrow > (visible when a next game exists)
#
# After quit(), self.selected holds the GAME_REGISTRY index that was chosen.

from lib.engine.game   import BaseGame
from lib.engine.colors import YELLOW, GREEN, CYAN, ORANGE, MAGENTA, PURPLE, DIM_WHITE, WHITE
from lib.engine.font   import draw_char
from lib.hal           import LEFT, RIGHT, A


def _make_pong(hal):
    from games.pong.game import PongGame
    return PongGame(hal)


def _make_space_invaders(hal):
    from games.space_invaders.game import SpaceInvadersGame
    return SpaceInvadersGame(hal)


def _make_snake(hal):
    from games.snake.game import SnakeGame
    return SnakeGame(hal)


def _make_breakout(hal):
    from games.breakout.game import BreakoutGame
    return BreakoutGame(hal)


def _make_simon(hal):
    from games.simon.game import SimonGame
    return SimonGame(hal)


def _make_frogger(hal):
    from games.frogger.game import FroggerGame
    return FroggerGame(hal)


def _make_flappy(hal):
    from games.flappy.game import FlappyGame
    return FlappyGame(hal)


def _make_tetris(hal):
    from games.tetris.game import TetrisGame
    return TetrisGame(hal)


# Registry entries: (two_char_label, color, factory_fn)
# factory_fn(hal) returns a ready-to-run BaseGame instance.
# Add new games here — nothing else needs changing.
GAME_REGISTRY = [
    ("PG", YELLOW,  _make_pong),
    ("SI", GREEN,   _make_space_invaders),
    ("SN", CYAN,    _make_snake),
    ("BR", ORANGE,  _make_breakout),
    ("SS", MAGENTA, _make_simon),
    ("FR", CYAN,    _make_frogger),
    ("FB", CYAN,    _make_flappy),
    ("TE", PURPLE,  _make_tetris),
]


class LauncherGame(BaseGame):
    """
    Game selection carousel shown on boot.
    Scroll with LEFT/RIGHT, launch with A.
    Returns to this screen when a game calls game.quit().
    """

    def on_start(self):
        self.hal.set_brightness(30)
        self.selected  = 0   # set on quit so runner knows which game to launch
        self._index    = 0
        self._timer    = 0
        self._blink    = True
        self._debounce = 0   # cooldown between navigation presses (ms)

    def update(self, dt):
        self._timer    += dt
        self._blink     = (self._timer // 400) % 2 == 0
        self._debounce  = max(0, self._debounce - dt)

        hal = self.hal
        n   = len(GAME_REGISTRY)

        if self._debounce == 0:
            if hal.is_pressed(RIGHT) and self._index < n - 1:
                self._index    += 1
                self._debounce  = 220
                self._timer     = 0   # restart blink phase so label snaps on
                hal.play_tone(440, 40)
            elif hal.is_pressed(LEFT) and self._index > 0:
                self._index    -= 1
                self._debounce  = 220
                self._timer     = 0
                hal.play_tone(440, 40)

        if hal.is_pressed(A):
            self.selected = self._index
            hal.play_tone(880, 60)
            self.quit()

    def render(self):
        hal              = self.hal
        idx              = self._index
        n                = len(GAME_REGISTRY)
        label, color, _  = GAME_REGISTRY[idx]

        # Two-char label centred in cols 2-8, rows 1-5.
        # Each 3-wide glyph + 1-px gap: 3+1+3 = 7 px, starting at x=2.
        draw_char(hal, label[0], 2, 1, color)
        draw_char(hal, label[1], 6, 1, color)

        # Left arrow <  — col 0-1, rows 2-4
        if idx > 0:
            hal.set_pixel(1, 2, DIM_WHITE)
            hal.set_pixel(0, 3, WHITE)
            hal.set_pixel(1, 4, DIM_WHITE)

        # Right arrow >  — col 10-11, rows 2-4
        if idx < n - 1:
            hal.set_pixel(10, 2, DIM_WHITE)
            hal.set_pixel(11, 3, WHITE)
            hal.set_pixel(10, 4, DIM_WHITE)

        # Position dots at row 0, centred across the display.
        dot_x = (12 - n) // 2
        for i in range(n):
            c = color if i == idx else DIM_WHITE
            hal.set_pixel(dot_x + i, 0, c)

        # Blinking "press A" indicator at row 7
        if self._blink:
            hal.set_pixel(5, 7, color)
            hal.set_pixel(6, 7, color)
