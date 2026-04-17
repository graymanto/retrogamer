# games/tetris/game.py
# MicroPython-compatible. Entry point for Tetris.

from lib.engine.game  import BaseGame
from lib.engine.state import StateMachine


class TetrisGame(BaseGame):
    def on_start(self):
        self.hal.set_brightness(30)
        self.score = 0
        self.level = 1
        from games.tetris.states import MenuState
        self.states = StateMachine()
        self.states.push(MenuState(self))

    def update(self, dt):
        self.states.update(dt)

    def render(self):
        self.states.render()
