# games/pong/states.py
# MicroPython-compatible. All pong game states.

from lib.engine.state  import GameState
from lib.engine.colors import RED, BLUE, WHITE, DIM_WHITE, BLACK, YELLOW, GREEN
from lib.engine.font   import draw_text, draw_char, text_width
from lib.engine.sprite import SCALE
from lib.hal           import UP, DOWN, LEFT, RIGHT, A, B

from games.pong.ball   import Ball
from games.pong.paddle import Paddle
from games.pong.ai     import PaddleAI

WIN_SCORE = 5

# Paddle colours
LEFT_COLOR  = RED
RIGHT_COLOR = BLUE

# Note frequencies (Hz)
NOTE_PADDLE  = 480
NOTE_WALL    = 220
NOTE_SCORE   = 880
NOTE_WIN     = 1046


class MenuState(GameState):
    """Pong title / mode selection screen."""

    def __init__(self, game):
        super().__init__(game)
        self._timer  = 0
        self._blink  = True
        # Animated demo paddles
        self._lp_y   = 2
        self._rp_y   = 4
        self._ball_x = 6
        self._ball_y = 3
        self._bvx    = 1
        self._bvy    = 1
        self._anim_t = 0

    def on_enter(self):
        self._timer = 0

    def update(self, dt):
        self._timer  += dt
        self._anim_t += dt
        self._blink   = (self._timer // 400) % 2 == 0

        # Animate demo ball every 120ms
        if self._anim_t >= 120:
            self._anim_t = 0
            self._ball_x += self._bvx
            self._ball_y += self._bvy
            if self._ball_x <= 1:
                self._ball_x = 1
                self._bvx    = 1
            if self._ball_x >= 10:
                self._ball_x = 10
                self._bvx    = -1
            if self._ball_y <= 0:
                self._ball_y = 0
                self._bvy    = 1
            if self._ball_y >= 7:
                self._ball_y = 7
                self._bvy    = -1
            # Demo AI paddles
            if self._ball_y < self._lp_y + 1 and self._lp_y > 0:
                self._lp_y -= 1
            elif self._ball_y > self._lp_y + 1 and self._lp_y < 6:
                self._lp_y += 1
            if self._ball_y < self._rp_y + 1 and self._rp_y > 0:
                self._rp_y -= 1
            elif self._ball_y > self._rp_y + 1 and self._rp_y < 6:
                self._rp_y += 1

        # Button presses
        if self.hal.is_pressed(LEFT):
            self.game.quit()   # return to launcher
        elif self.hal.is_pressed(A):
            self.game.states.request_switch(PlayingState(self.game, two_player=False))
        elif self.hal.is_pressed(B):
            self.game.states.request_switch(PlayingState(self.game, two_player=True))

    def render(self):
        hal = self.hal

        # Demo paddles
        hal.set_pixel(0, self._lp_y,     LEFT_COLOR)
        hal.set_pixel(0, self._lp_y + 1, LEFT_COLOR)
        hal.set_pixel(11, self._rp_y,     RIGHT_COLOR)
        hal.set_pixel(11, self._rp_y + 1, RIGHT_COLOR)

        # Demo ball
        hal.set_pixel(self._ball_x, self._ball_y, WHITE)

        # Centre divider
        for row in range(0, 8, 2):
            hal.set_pixel(5, row, DIM_WHITE)
            hal.set_pixel(6, row, DIM_WHITE)

        # "PONG" title at top (centred)
        draw_text(hal, "P", 1, 1, YELLOW)
        draw_text(hal, "O", 5, 1, YELLOW)
        draw_text(hal, "N", 9, 1, YELLOW)

        # Mode prompt (blink)
        if self._blink:
            hal.set_pixel(4, 7, RED)     # A = 1P
            hal.set_pixel(5, 7, RED)
            hal.set_pixel(6, 7, BLUE)    # B = 2P
            hal.set_pixel(7, 7, BLUE)


class PlayingState(GameState):
    """Main pong gameplay state."""

    # Phase constants
    _PHASE_PLAYING  = 0
    _PHASE_GOAL     = 1   # celebration after a score
    _PHASE_NEWGAME  = 2   # brief pause before ball relaunch

    def __init__(self, game, two_player=False):
        super().__init__(game)
        self._two_player = two_player

    def on_enter(self):
        self._ball       = Ball()
        self._left_pad   = Paddle(0, LEFT_COLOR)
        self._right_pad  = Paddle(11, RIGHT_COLOR)
        self._scores     = [0, 0]   # [left, right]
        self._phase      = self._PHASE_NEWGAME
        self._phase_timer = 600     # ms
        self._last_scorer = 0       # 0=left, 1=right
        self._flash_on   = False

        if not self._two_player:
            self._ai = PaddleAI(self._right_pad, reaction_delay_ms=90)
        else:
            self._ai = None

    def update(self, dt):
        if self._phase == self._PHASE_PLAYING:
            self._update_playing(dt)
        elif self._phase == self._PHASE_GOAL:
            self._update_goal(dt)
        elif self._phase == self._PHASE_NEWGAME:
            self._update_newgame(dt)

    def _update_playing(self, dt):
        hal = self.hal

        # Left paddle (UP/DOWN)
        if hal.is_pressed(UP):
            self._left_pad.move_up(dt)
        elif hal.is_pressed(DOWN):
            self._left_pad.move_down(dt)

        # Right paddle (A=up, B=down in 1P mode replaced by AI)
        if self._two_player:
            if hal.is_pressed(A):
                self._right_pad.move_up(dt)
            elif hal.is_pressed(B):
                self._right_pad.move_down(dt)
        else:
            if self._ai:
                self._ai.update(dt, self._ball)

        # Move ball
        self._ball.update(dt)

        # Wall bounces
        wall_hit = self._ball.check_wall_bounce()
        if wall_hit:
            hal.play_tone(NOTE_WALL, 60)

        # Paddle collisions — use directional threshold instead of AABB so a
        # fast ball that tunnels past the paddle column in one frame is still caught.
        ball = self._ball
        if (ball.vel.x < 0 and
                ball.pixel_x <= self._left_pad.pixel_x and
                ball.pixel_y < self._left_pad.pixel_y + self._left_pad.height and
                ball.pixel_y + ball.height > self._left_pad.pixel_y):
            ball.bounce_x(paddle_center_y=self._left_pad.center_y)
            ball.pos.x = (self._left_pad.pixel_x + 1) * SCALE
            hal.play_tone(NOTE_PADDLE, 40)

        elif (ball.vel.x > 0 and
                ball.pixel_x >= self._right_pad.pixel_x and
                ball.pixel_y < self._right_pad.pixel_y + self._right_pad.height and
                ball.pixel_y + ball.height > self._right_pad.pixel_y):
            ball.bounce_x(paddle_center_y=self._right_pad.center_y)
            ball.pos.x = (self._right_pad.pixel_x - 1) * SCALE
            hal.play_tone(NOTE_PADDLE, 40)

        # Scoring
        if self._ball.is_off_left():
            self._score(1)   # right player scores
        elif self._ball.is_off_right():
            self._score(0)   # left player scores

    def _score(self, scorer):
        """A player scored. scorer: 0=left, 1=right."""
        self._scores[scorer] += 1
        self._last_scorer  = scorer
        self._phase        = self._PHASE_GOAL
        self._phase_timer  = 1800   # ms
        self._flash_on     = True
        self.hal.play_tone(NOTE_SCORE, 200)
        self.hal.vibrate(duration_ms=150)

    def _update_goal(self, dt):
        self._phase_timer -= dt
        self._flash_on = (self._phase_timer // 150) % 2 == 0

        if self._phase_timer <= 0:
            if max(self._scores) >= WIN_SCORE:
                self.game.states.request_switch(
                    GameOverState(self.game, self._scores)
                )
            else:
                # Relaunch ball toward the player who just conceded
                direction = 1 if self._last_scorer == 1 else -1
                self._ball.reset(direction=direction)
                self._phase       = self._PHASE_NEWGAME
                self._phase_timer = 500

    def _update_newgame(self, dt):
        self._phase_timer -= dt
        if self._phase_timer <= 0:
            self._phase = self._PHASE_PLAYING

    def render(self):
        hal  = self.hal
        ball = self._ball

        # Centre divider (dashed)
        for row in range(0, 8, 2):
            hal.set_pixel(5, row, DIM_WHITE)
            hal.set_pixel(6, row, DIM_WHITE)

        if self._phase == self._PHASE_GOAL:
            # Flash the scoring side, show score
            winner_color = LEFT_COLOR if self._last_scorer == 0 else RIGHT_COLOR
            if self._flash_on:
                half = 6 if self._last_scorer == 0 else 6
                for y in range(8):
                    for x in range(0, 6) if self._last_scorer == 0 else range(6, 12):
                        hal.set_pixel(x, y, winner_color)

            # Show scores using pixel font
            left_s  = str(self._scores[0])
            right_s = str(self._scores[1])
            draw_char(hal, left_s,  1, 1, LEFT_COLOR)
            draw_text(hal, "-",     5, 1, WHITE)
            draw_char(hal, right_s, 8, 1, RIGHT_COLOR)
            return

        # Normal play rendering
        self._left_pad.draw(hal)
        self._right_pad.draw(hal)

        # Draw ball (blink during newgame countdown)
        if self._phase == self._PHASE_PLAYING:
            ball.draw(hal)
        elif self._phase == self._PHASE_NEWGAME:
            if (self._phase_timer // 100) % 2 == 0:
                ball.draw(hal)


class GameOverState(GameState):
    """Displayed when a player wins."""

    def __init__(self, game, scores):
        super().__init__(game)
        self._scores  = scores
        self._timer   = 0
        self._blink   = True

    def on_enter(self):
        self._timer = 0
        winner = 0 if self._scores[0] > self._scores[1] else 1
        self._winner       = winner
        self._winner_color = LEFT_COLOR if winner == 0 else RIGHT_COLOR
        self.hal.play_tone(NOTE_WIN, 300)

    def update(self, dt):
        self._timer += dt
        self._blink  = (self._timer // 350) % 2 == 0

        if self._timer > 500 and self.hal.is_pressed(LEFT):
            self.game.quit()   # return to launcher
        elif self._timer > 500 and self.hal.is_pressed(A):
            self.game.states.request_switch(MenuState(self.game))

    def render(self):
        hal   = self.hal
        color = self._winner_color

        # Flash winner's half
        if self._blink:
            rng = range(0, 6) if self._winner == 0 else range(6, 12)
            for y in range(8):
                for x in rng:
                    hal.set_pixel(x, y, color)

        # Show final scores
        left_s  = str(self._scores[0])
        right_s = str(self._scores[1])
        draw_char(hal, left_s,  1, 1, LEFT_COLOR)
        draw_text(hal, "-",     5, 1, WHITE)
        draw_char(hal, right_s, 8, 1, RIGHT_COLOR)

        # "W" for winner side
        if self._blink:
            wx = 1 if self._winner == 0 else 8
            draw_char(hal, "W", wx, 6, color)
