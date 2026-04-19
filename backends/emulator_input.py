# platform/emulator_input.py
# Desktop-only. Full Python 3 + pygame.
# Maps keyboard keys (and optional gamepad) to HAL button constants.

import pygame
from lib.hal import UP, DOWN, LEFT, RIGHT, A, B

# Keyboard mapping: pygame key constant -> HAL button name
KEY_MAP = {
    pygame.K_UP:    UP,
    pygame.K_DOWN:  DOWN,
    pygame.K_LEFT:  LEFT,
    pygame.K_RIGHT: RIGHT,
    pygame.K_z:     A,
    pygame.K_x:     B,
    # WASD alternative
    pygame.K_w:     UP,
    pygame.K_s:     DOWN,
    pygame.K_a:     LEFT,
    pygame.K_d:     RIGHT,
}

# Gamepad axis thresholds for D-pad simulation
AXIS_THRESHOLD = 0.5


class EmulatorInput:
    """Tracks button state from keyboard and optional gamepad."""

    def __init__(self):
        self._pressed  = set()
        self._joystick = None
        self._joy_axes = {}

        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self._joystick = pygame.joystick.Joystick(0)
            self._joystick.init()

    def pump(self):
        """Process pygame events. Must be called once per frame (inside HAL.show())."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            elif event.type == pygame.KEYDOWN:
                btn = KEY_MAP.get(event.key)
                if btn:
                    self._pressed.add(btn)

            elif event.type == pygame.KEYUP:
                btn = KEY_MAP.get(event.key)
                if btn:
                    self._pressed.discard(btn)

            elif event.type == pygame.JOYAXISMOTION:
                self._joy_axes[event.axis] = event.value
                self._update_joy_buttons()

            # D-pad on Xbox controller (and most modern gamepads) fires as hat 0.
            # Hat values: x: -1=left, 1=right; y: 1=up, -1=down (note: y is inverted vs screen).
            elif event.type == pygame.JOYHATMOTION:
                self._update_hat_buttons(event.value)

            elif event.type == pygame.JOYBUTTONDOWN:
                # Xbox: 0=A, 1=B, 2=X, 3=Y
                if event.button == 0:
                    self._pressed.add(A)
                elif event.button == 1:
                    self._pressed.add(B)

            elif event.type == pygame.JOYBUTTONUP:
                if event.button == 0:
                    self._pressed.discard(A)
                elif event.button == 1:
                    self._pressed.discard(B)

    def _update_joy_buttons(self):
        """Convert left-stick analog axis values to digital button presses."""
        x = self._joy_axes.get(0, 0.0)
        y = self._joy_axes.get(1, 0.0)

        for btn in (LEFT, RIGHT, UP, DOWN):
            self._pressed.discard(btn)

        if x < -AXIS_THRESHOLD:
            self._pressed.add(LEFT)
        elif x > AXIS_THRESHOLD:
            self._pressed.add(RIGHT)

        if y < -AXIS_THRESHOLD:
            self._pressed.add(UP)
        elif y > AXIS_THRESHOLD:
            self._pressed.add(DOWN)

    def _update_hat_buttons(self, hat_value):
        """Convert D-pad hat (x, y) to button presses. Hat y: 1=up, -1=down."""
        hx, hy = hat_value
        for btn in (LEFT, RIGHT, UP, DOWN):
            self._pressed.discard(btn)
        if hx == -1:
            self._pressed.add(LEFT)
        elif hx == 1:
            self._pressed.add(RIGHT)
        if hy == 1:
            self._pressed.add(UP)
        elif hy == -1:
            self._pressed.add(DOWN)

    def is_pressed(self, button):
        return button in self._pressed

    def get_pressed(self):
        """Return the set of currently pressed button names (for display footer)."""
        return set(self._pressed)
