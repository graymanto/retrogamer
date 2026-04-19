# games/platformer/game.py
# MicroPython-compatible. Entry point for the Platformer.
#
# Optional constructor argument:
#   levels — a tuple/list of level dicts (same format as levels.py LEVELS).
#            Defaults to the built-in games/platformer/levels.py when None.
#            Pass a custom levels object to run a different campaign.

from lib.engine.game  import BaseGame
from lib.engine.state import StateMachine


class PlatformerGame(BaseGame):
    def __init__(self, hal, levels=None):
        self._custom_levels = levels
        super().__init__(hal)

    def on_start(self):
        self.hal.set_brightness(30)
        self.score     = 0
        self.lives     = 3
        self.level_idx = 0
        if self._custom_levels is not None:
            self.levels = self._custom_levels
        else:
            from games.platformer.levels import LEVELS
            self.levels = LEVELS
        from games.platformer.states import MenuState
        self.states = StateMachine()
        self.states.push(MenuState(self))

    def update(self, dt):
        self.states.update(dt)

    def render(self):
        self.states.render()
