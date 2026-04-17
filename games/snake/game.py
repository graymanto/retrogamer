# games/snake/game.py
# MicroPython-compatible.

from lib.engine.game  import BaseGame
from lib.engine.state import StateMachine
from games.snake.states import MenuState


class SnakeGame(BaseGame):
    """Classic snake with wraparound grid, escalating speed, and scoring."""

    def on_start(self):
        self.hal.set_brightness(30)
        self.states = StateMachine()
        self.states.push(MenuState(self))

    def update(self, dt):
        self.states.update(dt)

    def render(self):
        self.states.render()
