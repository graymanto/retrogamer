# lib/engine/game.py
# MicroPython-compatible. No typing, no dataclasses, no match/case.

DISPLAY_W = 12
DISPLAY_H = 8
TARGET_FPS = 30
FRAME_MS   = 1000 // TARGET_FPS   # ~33ms per frame


class BaseGame:
    """
    Base class for all games. Subclass and override on_start(), update(), render().

    The HAL is dependency-injected so game code is platform-agnostic.
    Do NOT call hal.show() inside render() — the game loop does that once per frame.

    Usage:
        game = MyGame(hal)
        game.run()
    """

    def __init__(self, hal):
        self.hal    = hal
        self.width  = DISPLAY_W
        self.height = DISPLAY_H
        self._running = False

    def on_start(self):
        """Called once before the game loop begins. Override for initialisation."""
        pass

    def update(self, dt):
        """Called each frame with elapsed time in milliseconds since last frame.
        Override with game logic."""
        pass

    def render(self):
        """Called each frame after update(). Draw using self.hal.set_pixel() etc.
        Do NOT call self.hal.show() here — BaseGame.run() does that."""
        pass

    def run(self):
        """Start the game loop. Blocks until quit() is called."""
        self.on_start()
        self._running = True
        last_ms = self.hal.ticks_ms()

        while self._running:
            now = self.hal.ticks_ms()
            dt  = now - last_ms

            if dt < FRAME_MS:
                self.hal.sleep_ms(1)
                continue

            # Cap dt so a slow frame doesn't cause physics explosions
            if dt > 200:
                dt = 200
            last_ms = now

            self.hal.fill((0, 0, 0))  # Clear display each frame
            self.update(dt)
            self.render()
            self.hal.show()

    def quit(self):
        """Signal the game loop to stop after the current frame."""
        self._running = False
