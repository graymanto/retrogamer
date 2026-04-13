# backends/emulator_hal.py
# Desktop-only. Full Python 3 + pygame.
# Composes display, input, and audio into the HAL interface.

import time
import pygame

from lib.hal.interface import BaseHAL
from backends.emulator_display import EmulatorDisplay
from backends.emulator_input   import EmulatorInput
from backends.emulator_audio   import EmulatorAudio

TARGET_FPS = 30


class EmulatorHAL(BaseHAL):
    """HAL implementation for Mac/PC. Renders via pygame, reads keyboard/gamepad."""

    def __init__(self, cell_size=54, bezel=24):
        pygame.init()
        self._display = EmulatorDisplay(cell_size=cell_size, bezel=bezel)
        self._input   = EmulatorInput()
        self._audio   = EmulatorAudio()
        self._clock   = pygame.time.Clock()
        self._brightness = 100

    # --- Display ---

    def set_pixel(self, x, y, color):
        self._display.set_pixel(x, y, color)

    def fill(self, color):
        self._display.fill(color)

    def show(self):
        """Flush display, pump events, and cap framerate to TARGET_FPS."""
        self._display.render(self._input.get_pressed())
        self._input.pump()
        self._clock.tick(TARGET_FPS)

    def set_brightness(self, level):
        self._brightness = level
        self._display.set_brightness(level)

    # --- Input ---

    def is_pressed(self, button):
        return self._input.is_pressed(button)

    # --- Audio ---

    def play_tone(self, freq, duration_ms=None):
        self._audio.play_tone(freq, duration_ms)

    def stop_tone(self):
        self._audio.stop_tone()

    # --- Haptics (no-op on desktop) ---

    def vibrate(self, duration_ms=None):
        pass  # No haptic hardware on desktop

    def stop_vibrate(self):
        pass

    # --- Timing ---

    def ticks_ms(self):
        return int(time.monotonic() * 1000)

    def sleep_ms(self, ms):
        pygame.time.wait(ms)
