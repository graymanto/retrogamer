# lib/engine/font.py
# MicroPython-compatible. 3x5 pixel font for digits and basic symbols.
# Use draw_char() to render a single character, draw_text() for a string.

# Each glyph: list of 5 rows, each row a list of 3 values (1=on, 0=off).
_GLYPHS = {
    '0': [
        [1,1,1],
        [1,0,1],
        [1,0,1],
        [1,0,1],
        [1,1,1],
    ],
    '1': [
        [0,1,0],
        [1,1,0],
        [0,1,0],
        [0,1,0],
        [1,1,1],
    ],
    '2': [
        [1,1,1],
        [0,0,1],
        [1,1,1],
        [1,0,0],
        [1,1,1],
    ],
    '3': [
        [1,1,1],
        [0,0,1],
        [0,1,1],
        [0,0,1],
        [1,1,1],
    ],
    '4': [
        [1,0,1],
        [1,0,1],
        [1,1,1],
        [0,0,1],
        [0,0,1],
    ],
    '5': [
        [1,1,1],
        [1,0,0],
        [1,1,1],
        [0,0,1],
        [1,1,1],
    ],
    '6': [
        [1,1,1],
        [1,0,0],
        [1,1,1],
        [1,0,1],
        [1,1,1],
    ],
    '7': [
        [1,1,1],
        [0,0,1],
        [0,1,0],
        [0,1,0],
        [0,1,0],
    ],
    '8': [
        [1,1,1],
        [1,0,1],
        [1,1,1],
        [1,0,1],
        [1,1,1],
    ],
    '9': [
        [1,1,1],
        [1,0,1],
        [1,1,1],
        [0,0,1],
        [1,1,1],
    ],
    '-': [
        [0,0,0],
        [0,0,0],
        [1,1,1],
        [0,0,0],
        [0,0,0],
    ],
    ' ': [
        [0,0,0],
        [0,0,0],
        [0,0,0],
        [0,0,0],
        [0,0,0],
    ],
    'L': [
        [1,0,0],
        [1,0,0],
        [1,0,0],
        [1,0,0],
        [1,1,1],
    ],
    'R': [
        [1,1,0],
        [1,0,1],
        [1,1,0],
        [1,0,1],
        [1,0,1],
    ],
    'P': [
        [1,1,0],
        [1,0,1],
        [1,1,0],
        [1,0,0],
        [1,0,0],
    ],
    'G': [
        [1,1,1],
        [1,0,0],
        [1,0,1],
        [1,0,1],
        [1,1,1],
    ],
    'O': [
        [1,1,1],
        [1,0,1],
        [1,0,1],
        [1,0,1],
        [1,1,1],
    ],
    'N': [
        [1,0,1],
        [1,1,1],
        [1,1,1],
        [1,0,1],
        [1,0,1],
    ],
    'W': [
        [1,0,1],
        [1,0,1],
        [1,1,1],
        [1,1,1],
        [1,0,1],
    ],
    'I': [
        [1,1,1],
        [0,1,0],
        [0,1,0],
        [0,1,0],
        [1,1,1],
    ],
    'S': [
        [1,1,1],
        [1,0,0],
        [1,1,1],
        [0,0,1],
        [1,1,1],
    ],
    'E': [
        [1,1,1],
        [1,0,0],
        [1,1,0],
        [1,0,0],
        [1,1,1],
    ],
}

# Glyph width (all glyphs are 3 wide except special narrow ones)
GLYPH_W = 3
GLYPH_H = 5


def draw_char(hal, char, x, y, color):
    """Draw a single character at pixel position (x, y).
    Returns the x position after the character (x + glyph_width + 1 for gap)."""
    glyph = _GLYPHS.get(char, _GLYPHS.get(' '))
    if glyph is None:
        return x + GLYPH_W + 1
    for row in range(GLYPH_H):
        for col in range(GLYPH_W):
            if glyph[row][col]:
                nx = x + col
                ny = y + row
                if 0 <= nx < 12 and 0 <= ny < 8:
                    hal.set_pixel(nx, ny, color)
    return x + GLYPH_W + 1   # +1 for gap between chars


def draw_text(hal, text, x, y, color):
    """Draw a string of characters starting at (x, y). Returns final x position."""
    cx = x
    for char in text:
        cx = draw_char(hal, char, cx, y, color)
    return cx


def text_width(text):
    """Return the pixel width of a text string (for centering calculations)."""
    if not text:
        return 0
    return len(text) * (GLYPH_W + 1) - 1   # no trailing gap
