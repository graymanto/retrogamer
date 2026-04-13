# lib/utils/math_helpers.py
# MicroPython-compatible. Pure integer arithmetic helpers.
# Do not import the math module — use these instead.


def clamp(value, lo, hi):
    """Clamp value to the range [lo, hi]."""
    if value < lo:
        return lo
    if value > hi:
        return hi
    return value


def sign(value):
    """Return 1 if value > 0, -1 if value < 0, 0 if value == 0."""
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def lerp_int(a, b, t_num, t_den):
    """Integer linear interpolation: a + (b-a) * t_num // t_den"""
    return a + (b - a) * t_num // t_den


def abs_val(value):
    """Absolute value (avoids importing abs from builtins on constrained targets)."""
    return value if value >= 0 else -value
