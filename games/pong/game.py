# games/pong/game.py
# MicroPython-compatible.

from lib.engine.game  import BaseGame
from lib.engine.state import StateMachine
from games.pong.states import MenuState


class PongGame(BaseGame):
    """Two-player (or 1P vs AI) classic pong."""

    def on_start(self):
        self.hal.set_brightness(30)
        self.states = StateMachine()
        self.states.push(MenuState(self))

    def update(self, dt):
        self.states.update(dt)

    def render(self):
        self.states.render()
