# games/space_invaders/states.py
# MicroPython-compatible. All Space Invaders game states.

import random

from lib.engine.state  import GameState
from lib.engine.colors import GREEN, CYAN, YELLOW, RED, WHITE, BLACK, DIM_WHITE, ORANGE
from lib.engine.font   import draw_char, draw_text, text_width
from lib.hal           import UP, DOWN, LEFT, RIGHT, A, B

from games.space_invaders.invader import InvaderGrid
from games.space_invaders.player  import Player
from games.space_invaders.bullet  import Bullet

# Tone frequencies
NOTE_FIRE    = 800
NOTE_HIT     = 200
NOTE_EXPLODE = 100
NOTE_WIN_1   = 523
NOTE_WIN_2   = 659
NOTE_WIN_3   = 784

# Bullet colors
PLAYER_BULLET_COLOR  = YELLOW
INVADER_BULLET_COLOR = RED

MAX_INVADER_BULLETS = 2


class MenuState(GameState):
    """Space Invaders title screen."""

    def __init__(self, game):
        super().__init__(game)
        self._timer   = 0
        self._blink   = True
        self._wave    = 0   # animation wave counter
        self._inv_x   = 2   # demo invader x

    def on_enter(self):
        self._timer = 0

    def update(self, dt):
        self._timer += dt
        self._blink  = (self._timer // 400) % 2 == 0
        self._wave   = (self._timer // 300) % 4

        if self.hal.is_pressed(LEFT):
            self.game.quit()   # return to launcher
        elif self.hal.is_pressed(A):
            self.game.states.request_switch(PlayingState(self.game))

    def render(self):
        hal = self.hal

        # Show a mini invader formation (3x2 block)
        inv_colors = [CYAN, GREEN, YELLOW]
        for row in range(3):
            color = inv_colors[row]
            for col in range(6):
                px = 3 + col
                py = 1 + row
                # Animate: shift by wave for march effect
                if (col + self._wave) % 2 == 0:
                    hal.set_pixel(px, py, color)

        # "S I" hint at bottom
        draw_text(hal, "S", 0, 5, GREEN)
        draw_text(hal, "I", 4, 5, CYAN)

        # Press A prompt
        if self._blink:
            hal.set_pixel(10, 7, YELLOW)
            hal.set_pixel(11, 7, YELLOW)


class PlayingState(GameState):
    """Main Space Invaders gameplay."""

    _PHASE_PLAYING  = 0
    _PHASE_EXPLODE  = 1    # Player was hit
    _PHASE_WIN      = 2    # Wave cleared
    _PHASE_GAMEOVER = 3

    def __init__(self, game, wave=1):
        super().__init__(game)
        self._wave = wave

    def on_enter(self):
        # Start invaders lower on later waves (harder)
        start_y = min(self._wave - 1, 2)
        self._invaders       = InvaderGrid(cols=8, rows=3, start_x=2, start_y=start_y)
        self._player         = Player()
        self._player_bullet  = None    # one bullet at a time
        self._inv_bullets    = []      # list of Bullet
        self._score          = self.game.score
        self._phase          = self._PHASE_PLAYING
        self._phase_timer    = 0
        self._explode_frame  = 0
        self._win_timer      = 0

        # Brief invincibility after starting (so first frame input doesn't fire)
        self._start_timer = 200

    def update(self, dt):
        if self._phase == self._PHASE_PLAYING:
            self._update_playing(dt)
        elif self._phase == self._PHASE_EXPLODE:
            self._update_explode(dt)
        elif self._phase == self._PHASE_WIN:
            self._update_win(dt)

    def _update_playing(self, dt):
        hal = self.hal

        if self._start_timer > 0:
            self._start_timer -= dt
            return

        # Player movement
        self._player.handle_input(hal, dt)

        # Player fire (A button, one bullet at a time)
        if hal.is_pressed(A):
            if self._player_bullet is None or not self._player_bullet.active:
                self._player_bullet = Bullet(
                    self._player.x, self._player.y - 1,
                    dy=-1,
                    color=PLAYER_BULLET_COLOR,
                    speed_ms=70,
                )
                hal.play_tone(NOTE_FIRE, 50)

        # Update player bullet
        if self._player_bullet and self._player_bullet.active:
            self._player_bullet.update(dt)
            # Check invader hit
            if self._player_bullet.active:
                pts = self._invaders.check_hit(
                    self._player_bullet.x, self._player_bullet.y
                )
                if pts:
                    self._score += pts
                    self.game.score = self._score
                    self._player_bullet.active = False
                    hal.play_tone(NOTE_HIT, 80)
                    # Check wave clear
                    if self._invaders.alive_count() == 0:
                        self._phase       = self._PHASE_WIN
                        self._phase_timer = 1500
                        hal.play_tone(NOTE_WIN_1, 200)

        # Update invader grid (march + sounds)
        tones = self._invaders.update(dt, hal)
        for freq in tones:
            hal.play_tone(freq, 60)

        # Check if invaders reached player row
        if self._invaders.has_reached_player(self._player.y):
            self._start_explode()
            return

        # Invader shooting — only spawn bullets that have at least 2 clear pixels
        # of travel before reaching the player.  When invaders are very close to
        # the bottom the player is already about to lose via has_reached_player();
        # spawning a bullet 1 pixel above the player gives no meaningful reaction time.
        new_shots = self._invaders.update_shooting(dt)
        for sx, sy in new_shots:
            bullet_y = sy + 1
            if bullet_y >= self._player.y - 1:
                continue   # Too close — bullet would be on or adjacent to player
            if len(self._inv_bullets) < MAX_INVADER_BULLETS:
                self._inv_bullets.append(
                    Bullet(sx, bullet_y, dy=1,
                           color=INVADER_BULLET_COLOR, speed_ms=220)
                )

        # Update invader bullets
        active_bullets = []
        for blt in self._inv_bullets:
            blt.update(dt)
            if blt.active:
                # Check player hit
                if blt.x == self._player.x and blt.y == self._player.y:
                    self._start_explode()
                    return
                active_bullets.append(blt)
        self._inv_bullets = active_bullets

    def _start_explode(self):
        self._phase       = self._PHASE_EXPLODE
        self._phase_timer = 1200
        self._player.active = False
        self.hal.play_tone(NOTE_EXPLODE, 300)
        self.hal.vibrate(duration_ms=200)

    def _update_explode(self, dt):
        self._phase_timer -= dt
        self._explode_frame = int((1200 - self._phase_timer) // 80) % 4
        if self._phase_timer <= 0:
            self.game.states.request_switch(GameOverState(self.game, self._score))

    def _update_win(self, dt):
        self._phase_timer -= dt
        if self._phase_timer <= 0:
            # Next wave (faster)
            self.game.states.request_switch(
                PlayingState(self.game, wave=self._wave + 1)
            )

    def render(self):
        hal = self.hal

        if self._phase == self._PHASE_PLAYING or self._phase == self._PHASE_WIN:
            self._invaders.draw(hal)
            self._player.draw(hal)

            if self._player_bullet and self._player_bullet.active:
                self._player_bullet.draw(hal)

            for blt in self._inv_bullets:
                blt.draw(hal)

            # Show score as dots in top-left corner if space allows
            # (only when invaders haven't reached row 0)
            if self._invaders.y > 0:
                score_dots = min(5, self._score // 10)
                for i in range(score_dots):
                    hal.set_pixel(i, 0, DIM_WHITE)

        elif self._phase == self._PHASE_EXPLODE:
            self._invaders.draw(hal)
            # Explosion animation (expanding cross)
            ex = self._player.x
            frame = self._explode_frame
            exp_pixels = [
                [(ex, 7)],
                [(ex - 1, 7), (ex + 1, 7), (ex, 6)],
                [(ex - 2, 7), (ex + 2, 7), (ex - 1, 6), (ex + 1, 6), (ex, 5)],
                [(ex - 1, 7), (ex + 1, 7)],
            ]
            colors = [WHITE, YELLOW, ORANGE, RED]
            if frame < len(exp_pixels):
                for px, py in exp_pixels[frame]:
                    if 0 <= px < 12 and 0 <= py < 8:
                        hal.set_pixel(px, py, colors[frame])


class GameOverState(GameState):
    """Displayed when the player is destroyed."""

    def __init__(self, game, score):
        super().__init__(game)
        self._score = score
        self._timer = 0
        self._blink = True

    def on_enter(self):
        self._timer = 0
        self.game.score = 0   # Reset score for next game

    def update(self, dt):
        self._timer += dt
        self._blink  = (self._timer // 400) % 2 == 0

        if self._timer > 800 and self.hal.is_pressed(LEFT):
            self.game.quit()   # return to launcher
        elif self._timer > 800 and self.hal.is_pressed(A):
            self.game.states.request_switch(MenuState(self.game))

    def render(self):
        hal   = self.hal

        # Flash red background
        if self._blink:
            for y in range(8):
                for x in range(12):
                    hal.set_pixel(x, y, (40, 0, 0))

        # Show score (up to 2 digits)
        s = str(self._score)
        if len(s) == 1:
            draw_char(hal, s, 4, 1, YELLOW)
        else:
            draw_char(hal, s[0], 1, 1, YELLOW)
            draw_char(hal, s[1], 5, 1, YELLOW)
            if len(s) > 2:
                draw_char(hal, s[2], 9, 1, YELLOW)

        # "GO" game-over hint
        draw_text(hal, "G", 0, 6, RED)
        draw_text(hal, "O", 4, 6, RED)

        # Press A prompt
        if self._blink:
            hal.set_pixel(10, 7, YELLOW)
            hal.set_pixel(11, 7, YELLOW)
