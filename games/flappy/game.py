# games/flappy/game.py
# MicroPython-compatible. FlappyGame entry point.

from lib.engine.game  import BaseGame
from lib.engine.state import StateMachine


class FlappyGame(BaseGame):

    def on_start(self):
        self.hal.set_brightness(30)
        self.score = 0
        from games.flappy.states import MenuState
        self.states = StateMachine()
        self.states.push(MenuState(self))

    def update(self, dt):
        self.states.update(dt)

    def render(self):
        self.states.render()
