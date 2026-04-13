# platform/emulator_display.py
# Desktop-only. Full Python 3 + pygame.
# Renders the 12x8 LED matrix as a windowed display with bezel and button indicators.

import pygame

DISPLAY_W = 12
DISPLAY_H = 8

BEZEL_COLOR    = (25,  25,  25)
SCREEN_BG      = (10,  10,  10)
INACTIVE_COLOR = (18,  18,  18)   # Very dim LED "off" appearance
LED_GAP        = 3                 # px gap between LED cells
LED_RADIUS     = 4                 # border radius for LED cells
FOOTER_HEIGHT  = 70

# Button layout in footer (label, center_x_fraction, center_y in footer)
_BUTTON_LAYOUT = [
    ("UP",    0.10, 0.25),
    ("DOWN",  0.10, 0.75),
    ("LEFT",  0.05, 0.50),
    ("RIGHT", 0.15, 0.50),
    ("A",     0.85, 0.45),
    ("B",     0.95, 0.45),
]
_BUTTON_ACTIVE_COLOR = (220, 220, 80)
_BUTTON_IDLE_COLOR   = (60,  60,  60)
_BUTTON_RADIUS       = 8

LABEL_FONT_SIZE = 14


class EmulatorDisplay:
    """Pygame-based rendering of the 12x8 LED matrix with a bezel and button strip."""

    def __init__(self, cell_size=54, bezel=24):
        self.cell_size = cell_size
        self.bezel     = bezel

        win_w = DISPLAY_W * cell_size + 2 * bezel
        win_h = DISPLAY_H * cell_size + 2 * bezel + FOOTER_HEIGHT

        self._surface = pygame.display.set_mode((win_w, win_h))
        pygame.display.set_caption("Retrogamer — ZIP96 Emulator")

        self._pixels     = [[(0, 0, 0)] * DISPLAY_W for _ in range(DISPLAY_H)]
        self._brightness = 1.0

        self._font = None
        try:
            pygame.font.init()
            self._font = pygame.font.SysFont("Arial", LABEL_FONT_SIZE, bold=True)
        except Exception:
            try:
                self._font = pygame.font.Font(None, LABEL_FONT_SIZE)
            except Exception:
                pass  # Font not available in headless mode — labels will be hidden

        self._win_w = win_w
        self._win_h = win_h

    def set_pixel(self, x, y, color):
        if 0 <= x < DISPLAY_W and 0 <= y < DISPLAY_H:
            self._pixels[y][x] = color

    def fill(self, color):
        for y in range(DISPLAY_H):
            for x in range(DISPLAY_W):
                self._pixels[y][x] = color

    def set_brightness(self, level):
        self._brightness = max(0.0, min(1.0, level / 100.0))

    def render(self, pressed_buttons=None):
        """Draw a full frame. pressed_buttons is a set of button name strings."""
        if pressed_buttons is None:
            pressed_buttons = set()

        surf = self._surface
        surf.fill(BEZEL_COLOR)

        b  = self.bezel
        cs = self.cell_size
        g  = LED_GAP
        br = self._brightness

        # Draw screen background
        screen_rect = pygame.Rect(b - g, b - g,
                                  DISPLAY_W * cs + 2 * g,
                                  DISPLAY_H * cs + 2 * g)
        pygame.draw.rect(surf, SCREEN_BG, screen_rect, border_radius=6)

        # Draw each LED cell
        for y in range(DISPLAY_H):
            for x in range(DISPLAY_W):
                r, gg, bl = self._pixels[y][x]
                if r == 0 and gg == 0 and bl == 0:
                    color = INACTIVE_COLOR
                else:
                    color = (
                        min(255, int(r  * br)),
                        min(255, int(gg * br)),
                        min(255, int(bl * br)),
                    )
                cell = pygame.Rect(
                    b + x * cs + g,
                    b + y * cs + g,
                    cs - g * 2,
                    cs - g * 2,
                )
                pygame.draw.rect(surf, color, cell, border_radius=LED_RADIUS)

        # Draw footer
        footer_y = b + DISPLAY_H * cs + b
        footer_rect = pygame.Rect(0, footer_y, self._win_w, FOOTER_HEIGHT)
        pygame.draw.rect(surf, (20, 20, 20), footer_rect)
        pygame.draw.line(surf, (50, 50, 50), (0, footer_y), (self._win_w, footer_y))

        # Draw button indicators
        for label, xf, yf in _BUTTON_LAYOUT:
            cx = int(xf * self._win_w)
            cy = footer_y + int(yf * FOOTER_HEIGHT)
            active = label in pressed_buttons
            btn_color = _BUTTON_ACTIVE_COLOR if active else _BUTTON_IDLE_COLOR
            pygame.draw.circle(surf, btn_color, (cx, cy), _BUTTON_RADIUS)
            if self._font:
                txt_surf = self._font.render(label, True, (180, 180, 180))
                txt_rect = txt_surf.get_rect(center=(cx, cy + _BUTTON_RADIUS + 9))
                surf.blit(txt_surf, txt_rect)

        pygame.display.flip()
