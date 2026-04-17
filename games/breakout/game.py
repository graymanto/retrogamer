# games/breakout/game.py
# MicroPython-compatible.

from lib.engine.game  import BaseGame
from lib.engine.state import StateMachine
from games.breakout.states import MenuState


class BreakoutGame(BaseGame):
    """Classic Breakout with escalating waves, speed, and scoring."""

    def on_start(self):
        self.hal.set_brightness(30)
        self.score = 0
        self.lives = 3
        self.states = StateMachine()
        self.states.push(MenuState(self))

    def update(self, dt):
        self.states.update(dt)

    def render(self):
        self.states.render()
