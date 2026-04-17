# games/breakout/states.py
# MicroPython-compatible. All Breakout game states.
#
# Display layout (12 wide × 8 tall):
#   Rows 0-3  : bricks (4 rows × 12 cols, colour-coded by row)
#   Rows 4-6  : open play area
#   Row  7    : paddle + ball when in launch phase
#
# Scoring: base points × current wave number.
#   RED bricks=3, ORANGE=2, YELLOW=1, GREEN=1 (base).
# Speed: ball speeds up with each paddle hit; each wave also adds a base bonus.
# Lives: 3 per game. Left on menu/gameover → launcher.

from lib.engine.state  import GameState
from lib.engine.colors import WHITE, RED, ORANGE, YELLOW, GREEN, DIM_WHITE, BLACK
from lib.engine.font   import draw_char, draw_text
from lib.hal           import LEFT, RIGHT, A

from lib.engine.sprite import SCALE

from games.breakout.ball   import Ball, BALL_SPEED_INC
from games.breakout.paddle import Paddle
from games.breakout.bricks import BrickGrid, BRICK_ROWS

# Dim versions of brick row colours used in menu/flash animations
_DIM_BRICK = [
    (50, 0,  0),    # dim red
    (50, 25, 0),    # dim orange
    (50, 50, 0),    # dim yellow
    (0,  50, 0),    # dim green
]

# Tone frequencies
NOTE_BRICK_LO  = 440   # lower rows
NOTE_BRICK_HI  = 660   # upper rows (more satisfying)
NOTE_PADDLE    = 330
NOTE_WALL      = 220
NOTE_LOST      = 110
NOTE_WIN       = 880

# Phase constants for PlayingState
_PHASE_LAUNCH      = 0   # ball resting on paddle, waiting for A
_PHASE_PLAYING     = 1   # ball in motion
_PHASE_BALL_LOST   = 2   # brief pause after ball falls off
_PHASE_LEVEL_CLEAR = 3   # all bricks gone — celebrate before next wave


class MenuState(GameState):
    """
    Breakout title screen with a demo: dim bricks at top, ball bouncing
    in the open area, paddle tracking it at the bottom.
    A = start, LEFT = back to launcher.
    """

    def __init__(self, game):
        super().__init__(game)
        self._timer   = 0
        self._blink   = True
        self._anim_t  = 0
        # Demo ball (integer pixel positions, no physics)
        self._bx  = 5
        self._by  = 5
        self._bdx = 1
        self._bdy = -1

    def on_enter(self):
        self._timer = 0

    def update(self, dt):
        self._timer  += dt
        self._blink   = (self._timer // 400) % 2 == 0
        self._anim_t  += dt

        # Step demo ball every 80ms
        if self._anim_t >= 80:
            self._anim_t -= 80
            self._bx += self._bdx
            self._by += self._bdy
            if self._bx <= 0:
                self._bx  = 0
                self._bdx = 1
            elif self._bx >= 11:
                self._bx  = 11
                self._bdx = -1
            # Bounce off top of open area (just below the brick zone)
            if self._by <= 4:
                self._by  = 4
                self._bdy = 1
            elif self._by >= 6:
                self._by  = 6
                self._bdy = -1

        if self.hal.is_pressed(LEFT):
            self.game.quit()
        elif self.hal.is_pressed(A):
            self.game.states.request_switch(PlayingState(self.game, wave=1))

    def render(self):
        hal = self.hal

        # Dim bricks at top
        for row in range(BRICK_ROWS):
            for col in range(12):
                hal.set_pixel(col, row, _DIM_BRICK[row])

        # Demo paddle tracking ball
        pad_x = max(0, min(9, self._bx - 1))
        for i in range(3):
            hal.set_pixel(pad_x + i, 7, WHITE)

        # Demo ball
        hal.set_pixel(self._bx, self._by, WHITE)

        # Blinking "press A" dots at row 7 right-side
        if self._blink:
            hal.set_pixel(10, 7, ORANGE)
            hal.set_pixel(11, 7, ORANGE)


class PlayingState(GameState):
    """Main Breakout gameplay."""

    def __init__(self, game, wave=1):
        super().__init__(game)
        self._wave = wave

    def on_enter(self):
        # Reset game state on first wave
        if self._wave == 1:
            self.game.score = 0
            self.game.lives = 3

        self._ball        = Ball()
        self._paddle      = Paddle()
        self._bricks      = BrickGrid()
        self._phase       = _PHASE_LAUNCH
        self._phase_timer = 0
        self._timer       = 0          # general timer (for blink etc.)
        self._launch_dir  = 1          # alternates left/right each launch
        self._flash_on    = False

        # Speed bonus grows with each wave (+0.5 px/s per wave)
        self._wave_speed_bonus = (self._wave - 1) * BALL_SPEED_INC

        # Park ball on paddle
        self._park_ball()

    def _park_ball(self):
        """Position ball centred above the paddle (LAUNCH phase)."""
        px = self._paddle.pixel_x + self._paddle.width // 2
        self._ball.reset()
        self._ball.set_pixel_pos(px, 6)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, dt):
        self._timer += dt
        if self._phase == _PHASE_LAUNCH:
            self._update_launch(dt)
        elif self._phase == _PHASE_PLAYING:
            self._update_playing(dt)
        elif self._phase == _PHASE_BALL_LOST:
            self._update_ball_lost(dt)
        elif self._phase == _PHASE_LEVEL_CLEAR:
            self._update_level_clear(dt)

    def _update_launch(self, dt):
        hal = self.hal

        # Paddle moves freely
        if hal.is_pressed(LEFT):
            self._paddle.move_left(dt)
        elif hal.is_pressed(RIGHT):
            self._paddle.move_right(dt)

        # Ball tracks paddle centre
        px = self._paddle.pixel_x + self._paddle.width // 2
        self._ball.set_pixel_pos(px, 6)

        if hal.is_pressed(A):
            self._ball.launch(direction=self._launch_dir,
                              speed_bonus=self._wave_speed_bonus)
            self._launch_dir = -self._launch_dir   # alternate next launch
            self._phase = _PHASE_PLAYING

    def _update_playing(self, dt):
        hal    = self.hal
        ball   = self._ball
        paddle = self._paddle

        # Paddle input
        if hal.is_pressed(LEFT):
            paddle.move_left(dt)
        elif hal.is_pressed(RIGHT):
            paddle.move_right(dt)

        # Remember position before move — pixel for brick face detection,
        # sub-pixel for paddle interpolation.
        prev_px    = ball.pixel_x
        prev_py    = ball.pixel_y
        prev_sub_x = ball.pos.x
        prev_sub_y = ball.pos.y

        # Advance ball
        ball.update(dt)

        # Wall bounces
        lost = ball.check_walls()

        # Paddle collision — use linear interpolation to find ball's x at the
        # moment it crossed the paddle row.  This fixes diagonal tunnel-through
        # at paddle ends.
        _PADDLE_Y_SUB = 7 * SCALE
        if ball.vel.y > 0 and ball.pos.y >= _PADDLE_Y_SUB:
            dy = ball.pos.y - prev_sub_y
            if dy > 0 and prev_sub_y < _PADDLE_Y_SUB:
                # Ball crossed the paddle row this frame — interpolate x
                dx     = ball.pos.x - prev_sub_x
                x_hit  = prev_sub_x + dx * (_PADDLE_Y_SUB - prev_sub_y) // dy
                hit_px = x_hit // SCALE
            else:
                hit_px = ball.pixel_x
            on_paddle = paddle.pixel_x <= hit_px < paddle.pixel_x + paddle.width
            if not on_paddle:
                # Interpolated x landed just outside the paddle edge due to
                # sub-pixel rounding on a steep diagonal approach.  Check the
                # ball's actual current column as a fallback.
                if paddle.pixel_x <= ball.pixel_x < paddle.pixel_x + paddle.width:
                    hit_px    = ball.pixel_x
                    on_paddle = True
            if on_paddle:
                ball.bounce_paddle(paddle.pixel_x, paddle.width, hit_px=hit_px)
                hal.play_tone(NOTE_PADDLE, 40)
                lost = False   # paddle caught it

        # Brick collision
        bx = ball.pixel_x
        by = ball.pixel_y
        if 0 <= by < BRICK_ROWS and 0 <= bx < 12 and self._bricks.is_alive(bx, by):
            pts = self._bricks.clear(bx, by)
            self.game.score += pts * self._wave   # wave multiplier
            # Determine which face of the brick was hit.
            # When the ball moved diagonally (both px and py changed), use the
            # sub-pixel distance to each axis boundary: whichever is smaller
            # relative to velocity was crossed first → that face was hit.
            if prev_px != bx and prev_py != by:
                vx = abs(ball.vel.x)
                vy = abs(ball.vel.y)
                # Sub-pixel distance from previous position to the face boundary
                if ball.vel.x > 0:
                    t_x = bx * SCALE - prev_sub_x          # dist to left face
                else:
                    t_x = prev_sub_x - (bx + 1) * SCALE    # dist to right face
                if ball.vel.y > 0:
                    t_y = by * SCALE - prev_sub_y          # dist to top face
                else:
                    t_y = prev_sub_y - (by + 1) * SCALE    # dist to bottom face
                # Cross-multiply to compare t_x/vx vs t_y/vy without division
                if t_x * vy <= t_y * vx:
                    ball.bounce_x()   # side face reached first
                else:
                    ball.bounce_y()   # top/bottom face reached first
            elif prev_py != by:
                ball.bounce_y()
            elif prev_px != bx:
                ball.bounce_x()
            else:
                ball.bounce_y()   # same pixel — default to vertical
            note = NOTE_BRICK_HI if by <= 1 else NOTE_BRICK_LO
            hal.play_tone(note, 40)

            if self._bricks.alive_count() == 0:
                self._phase       = _PHASE_LEVEL_CLEAR
                self._phase_timer = 1200
                hal.play_tone(NOTE_WIN, 200)
                hal.vibrate(duration_ms=120)
                return

        if lost:
            self._ball_lost()

    def _ball_lost(self):
        self.game.lives -= 1
        self._phase       = _PHASE_BALL_LOST
        self._phase_timer = 900
        self._flash_on    = True
        self.hal.play_tone(NOTE_LOST, 300)
        self.hal.vibrate(duration_ms=150)

    def _update_ball_lost(self, dt):
        self._phase_timer -= dt
        self._flash_on = (self._phase_timer // 120) % 2 == 0

        if self._phase_timer <= 0:
            if self.game.lives <= 0:
                self.game.states.request_switch(
                    GameOverState(self.game, self.game.score)
                )
            else:
                self._park_ball()
                self._phase = _PHASE_LAUNCH

    def _update_level_clear(self, dt):
        self._phase_timer -= dt
        self._flash_on = (self._phase_timer // 100) % 2 == 0
        if self._phase_timer <= 0:
            self.game.states.request_switch(
                PlayingState(self.game, wave=self._wave + 1)
            )

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def render(self):
        hal = self.hal

        if self._phase == _PHASE_LEVEL_CLEAR:
            # Flash all brick rows in wave colour
            if self._flash_on:
                for row in range(BRICK_ROWS):
                    for col in range(12):
                        hal.set_pixel(col, row, _DIM_BRICK[row])
            self._paddle.draw(hal)
            return

        # Bricks
        self._bricks.draw(hal)

        # Paddle
        self._paddle.draw(hal)

        # Ball — blink slowly while in launch phase
        if self._phase == _PHASE_PLAYING:
            self._ball.draw(hal)
        elif self._phase == _PHASE_LAUNCH:
            if (self._timer // 250) % 2 == 0:
                self._ball.draw(hal)

        # Red flash overlay during BALL_LOST
        if self._phase == _PHASE_BALL_LOST and self._flash_on:
            for x in range(12):
                hal.set_pixel(x, 7, (60, 0, 0))

        # Lives indicator: small dots right of centre on row 7 during LAUNCH
        if self._phase == _PHASE_LAUNCH:
            lives = self.game.lives
            for i in range(lives):
                hal.set_pixel(10 - i * 2, 7, ORANGE)


class GameOverState(GameState):
    """Shown when all lives are lost. Score displayed; A = play again, LEFT = launcher."""

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
        elif self._timer > 800 and self.hal.is_pressed(A):
            self.game.states.request_switch(PlayingState(self.game, wave=1))

    def render(self):
        hal = self.hal

        # Flashing background
        if self._blink:
            for y in range(8):
                for x in range(12):
                    hal.set_pixel(x, y, (40, 20, 0))   # dim orange tint

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

        # "GO" game-over label
        draw_char(hal, "G", 0, 6, ORANGE)
        draw_char(hal, "O", 4, 6, ORANGE)

        # Blinking "press A" prompt
        if self._blink:
            hal.set_pixel(10, 7, YELLOW)
            hal.set_pixel(11, 7, YELLOW)
