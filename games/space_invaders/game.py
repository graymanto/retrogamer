# games/space_invaders/game.py
# MicroPython-compatible.

from lib.engine.game  import BaseGame
from lib.engine.state import StateMachine
from games.space_invaders.states import MenuState


class SpaceInvadersGame(BaseGame):
    """Classic Space Invaders with escalating waves."""

    def on_start(self):
        self.hal.set_brightness(30)
        self.score  = 0
        self.states = StateMachine()
        self.states.push(MenuState(self))

    def update(self, dt):
        self.states.update(dt)

    def render(self):
        self.states.render()
