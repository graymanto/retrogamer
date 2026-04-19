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

# Gamepad axis threshold for left-stick digital conversion
AXIS_THRESHOLD = 0.5

_DIRECTIONS = (LEFT, RIGHT, UP, DOWN)


class EmulatorInput:
    """Tracks button state from keyboard and optional gamepad.

    Keyboard and gamepad directions are tracked in separate sets and merged
    in is_pressed(), so a neutral hat/axis event can't wipe out a held key.
    """

    def __init__(self):
        self._kb_pressed   = set()   # keyboard-sourced buttons
        self._joy_dirs     = set()   # gamepad direction buttons (hat + left stick)
        self._joy_face     = set()   # gamepad face buttons (A, B)
        self._joy_axes     = {}
        self._joystick     = None

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
                    self._kb_pressed.add(btn)

            elif event.type == pygame.KEYUP:
                btn = KEY_MAP.get(event.key)
                if btn:
                    self._kb_pressed.discard(btn)

            elif event.type == pygame.JOYAXISMOTION:
                self._joy_axes[event.axis] = event.value
                self._update_axis_dirs()

            # D-pad on Xbox controller (and most modern gamepads) fires as hat 0.
            # Hat values: x: -1=left, 1=right; y: 1=up, -1=down (y is inverted vs screen).
            elif event.type == pygame.JOYHATMOTION:
                self._update_hat_dirs(event.value)

            elif event.type == pygame.JOYBUTTONDOWN:
                # Xbox layout: 0=A, 1=B, 2=X, 3=Y
                if event.button == 0:
                    self._joy_face.add(A)
                elif event.button == 1:
                    self._joy_face.add(B)

            elif event.type == pygame.JOYBUTTONUP:
                if event.button == 0:
                    self._joy_face.discard(A)
                elif event.button == 1:
                    self._joy_face.discard(B)

    def _update_axis_dirs(self):
        """Convert left-stick analog axes to digital direction buttons."""
        x = self._joy_axes.get(0, 0.0)
        y = self._joy_axes.get(1, 0.0)
        dirs = set()
        if x < -AXIS_THRESHOLD:
            dirs.add(LEFT)
        elif x > AXIS_THRESHOLD:
            dirs.add(RIGHT)
        if y < -AXIS_THRESHOLD:
            dirs.add(UP)
        elif y > AXIS_THRESHOLD:
            dirs.add(DOWN)
        # Only replace axis-sourced directions; hat and keyboard are unaffected.
        self._joy_dirs = (self._joy_dirs - set(_DIRECTIONS)) | dirs

    def _update_hat_dirs(self, hat_value):
        """Convert D-pad hat (x, y) to direction buttons. Hat y: 1=up, -1=down."""
        hx, hy = hat_value
        dirs = set()
        if hx == -1:
            dirs.add(LEFT)
        elif hx == 1:
            dirs.add(RIGHT)
        if hy == 1:
            dirs.add(UP)
        elif hy == -1:
            dirs.add(DOWN)
        # Replace hat-sourced directions only; axis and keyboard are unaffected.
        self._joy_dirs = dirs

    def is_pressed(self, button):
        return (button in self._kb_pressed or
                button in self._joy_dirs or
                button in self._joy_face)

    def get_pressed(self):
        """Return the merged set of currently pressed button names (for display footer)."""
        return self._kb_pressed | self._joy_dirs | self._joy_face
