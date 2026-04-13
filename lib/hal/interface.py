# lib/hal/interface.py
# MicroPython-compatible. No ABC, no typing imports.
# Duck-typed interface — both HardwareHAL and EmulatorHAL must implement all methods.

class BaseHAL:
    """
    Hardware abstraction layer interface.
    Game code only ever calls these methods, never importing platform specifics.
    """

    # --- Display ---

    def set_pixel(self, x, y, color):
        """Set pixel at (x:0-11, y:0-7) to color=(r,g,b). Does not flush."""
        raise NotImplementedError

    def fill(self, color):
        """Fill entire 12x8 display with color=(r,g,b). Does not flush."""
        raise NotImplementedError

    def show(self):
        """Flush pixel buffer to display. On emulator also pumps events."""
        raise NotImplementedError

    def set_brightness(self, level):
        """Set display brightness 0-100."""
        raise NotImplementedError

    # --- Input ---

    def is_pressed(self, button):
        """Return bool. button is one of the constants in lib/hal/__init__.py."""
        raise NotImplementedError

    # --- Audio ---

    def play_tone(self, freq, duration_ms=None):
        """Play tone at freq Hz. If duration_ms given, play for that long then stop.
        If duration_ms is None, plays indefinitely until stop_tone() called."""
        raise NotImplementedError

    def stop_tone(self):
        """Stop any playing tone."""
        raise NotImplementedError

    # --- Haptics ---

    def vibrate(self, duration_ms=None):
        """Activate vibration motor. If duration_ms given, stop after that duration."""
        raise NotImplementedError

    def stop_vibrate(self):
        """Stop vibration motor."""
        raise NotImplementedError

    # --- Timing ---

    def ticks_ms(self):
        """Return current time in milliseconds.
        Use for dt calculation in the game loop.
        Avoids game code importing platform-specific time modules."""
        raise NotImplementedError

    def sleep_ms(self, ms):
        """Sleep for ms milliseconds. Yields CPU on desktop, blocks on hardware."""
        raise NotImplementedError
