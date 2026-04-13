# backends/hardware_hal.py
# MicroPython only — deployed to Raspberry Pi Pico alongside game code.
# Wraps the KitronikZIP96 hardware API.

import utime
from ZIP96Pico import KitronikZIP96  # noqa: MicroPython-only import

from lib.hal import UP, DOWN, LEFT, RIGHT, A, B
from lib.hal.interface import BaseHAL


class HardwareHAL(BaseHAL):
    """HAL implementation for the Kitronik ZIP96 Retrogamer hardware."""

    def __init__(self):
        self._gamer = KitronikZIP96()
        self._gamer.Screen.setBrightness(10)  # Sane default brightness

        self._button_map = {
            UP:    self._gamer.Up,
            DOWN:  self._gamer.Down,
            LEFT:  self._gamer.Left,
            RIGHT: self._gamer.Right,
            A:     self._gamer.A,
            B:     self._gamer.B,
        }

        self._vibrating = False

    # --- Display ---

    def set_pixel(self, x, y, color):
        self._gamer.Screen.setLEDMatrix(x, y, color)

    def fill(self, color):
        self._gamer.Screen.fill(color)

    def show(self):
        self._gamer.Screen.show()

    def set_brightness(self, level):
        self._gamer.Screen.setBrightness(level)

    # --- Input ---

    def is_pressed(self, button):
        btn = self._button_map.get(button)
        return btn.pressed() if btn else False

    # --- Audio ---

    def play_tone(self, freq, duration_ms=None):
        if duration_ms is not None:
            self._gamer.Buzzer.playTone_Length(int(freq), int(duration_ms))
        else:
            self._gamer.Buzzer.playTone(int(freq))

    def stop_tone(self):
        self._gamer.Buzzer.stopTone()

    # --- Haptics ---

    def vibrate(self, duration_ms=None):
        self._gamer.Vibrate.vibrate()
        if duration_ms is not None:
            utime.sleep_ms(int(duration_ms))
            self._gamer.Vibrate.stop()

    def stop_vibrate(self):
        self._gamer.Vibrate.stop()

    # --- Timing ---

    def ticks_ms(self):
        return utime.ticks_ms()

    def sleep_ms(self, ms):
        utime.sleep_ms(int(ms))
