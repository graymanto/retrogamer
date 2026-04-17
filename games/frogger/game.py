# games/frogger/game.py
# MicroPython-compatible.

from lib.engine.game  import BaseGame
from lib.engine.state import StateMachine
from games.frogger.states import MenuState


class FroggerGame(BaseGame):
    """Classic Frogger — guide the frog across traffic and river to safety."""

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
