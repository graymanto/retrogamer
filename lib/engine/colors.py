# lib/engine/colors.py
# MicroPython-compatible. Color tuples as constants.
# Games import from here for consistency across platforms.

BLACK   = (0,   0,   0)
WHITE   = (255, 255, 255)
RED     = (255, 0,   0)
GREEN   = (0,   200, 0)
BLUE    = (0,   0,   255)
YELLOW  = (255, 200, 0)
CYAN    = (0,   220, 255)
MAGENTA = (255, 0,   200)
ORANGE  = (255, 100, 0)
PURPLE  = (160, 0,   255)

DIM_WHITE  = (40,  40,  40)
DIM_RED    = (60,  0,   0)
DIM_GREEN  = (0,   60,  0)
DIM_BLUE   = (0,   0,   60)
DIM_CYAN   = (0,   60,  80)
DIM_YELLOW = (60,  50,  0)


def dim(color, factor_num, factor_den=100):
    """Return color scaled by factor_num/factor_den. Result clamped to 0-255."""
    r, g, b = color
    return (
        r * factor_num // factor_den,
        g * factor_num // factor_den,
        b * factor_num // factor_den,
    )


def blend(c1, c2, t_num, t_den=100):
    """Linear blend between c1 and c2. t_num/t_den=0 -> c1, =t_den -> c2."""
    r = c1[0] + (c2[0] - c1[0]) * t_num // t_den
    g = c1[1] + (c2[1] - c1[1]) * t_num // t_den
    b = c1[2] + (c2[2] - c1[2]) * t_num // t_den
    return (r, g, b)


def add(c1, c2):
    """Additive blend, clamped to 255."""
    r = min(255, c1[0] + c2[0])
    g = min(255, c1[1] + c2[1])
    b = min(255, c1[2] + c2[2])
    return (r, g, b)
