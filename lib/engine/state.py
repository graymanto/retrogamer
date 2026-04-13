# lib/engine/state.py
# MicroPython-compatible. State machine for game screens.


class GameState:
    """
    Base class for a single game state (screen/phase).
    Override update() and render() per state.

    Access the HAL via self.hal and the owning game via self.game.
    To switch states: self.game.states.switch(NewState(self.game))
    """

    def __init__(self, game):
        self.game = game
        self.hal  = game.hal

    def on_enter(self):
        """Called when this state becomes active."""
        pass

    def on_exit(self):
        """Called when this state is being replaced."""
        pass

    def update(self, dt):
        """Override with state-specific logic. dt in milliseconds."""
        pass

    def render(self):
        """Override with state-specific drawing. Do not call hal.show()."""
        pass


class StateMachine:
    """
    Stack-based state machine.
    push(): overlay a state (e.g. pause menu on top of gameplay).
    pop(): return to previous state.
    switch(): replace current state (no stack growth).
    """

    def __init__(self):
        self._stack = []
        self._pending = None   # Deferred state change to avoid mid-update switch issues

    def push(self, state):
        """Push a new state onto the stack."""
        if self._stack:
            self._stack[-1].on_exit()
        self._stack.append(state)
        state.on_enter()

    def pop(self):
        """Remove the top state and return to the previous one."""
        if self._stack:
            self._stack[-1].on_exit()
            self._stack.pop()
        if self._stack:
            self._stack[-1].on_enter()

    def switch(self, state):
        """Replace the current top state (does not grow the stack)."""
        if self._stack:
            self._stack[-1].on_exit()
            self._stack[-1] = state
        else:
            self._stack.append(state)
        state.on_enter()

    def request_switch(self, state):
        """Queue a state switch to happen at the end of the current update.
        Safe to call from within update() or render()."""
        self._pending = state

    @property
    def current(self):
        """The currently active state, or None."""
        return self._stack[-1] if self._stack else None

    def update(self, dt):
        """Forward update to the current state, then apply any pending switch."""
        if self._stack:
            self._stack[-1].update(dt)
        if self._pending is not None:
            self.switch(self._pending)
            self._pending = None

    def render(self):
        """Forward render to the current state."""
        if self._stack:
            self._stack[-1].render()
