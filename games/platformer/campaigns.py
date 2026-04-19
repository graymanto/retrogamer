# games/platformer/campaigns.py
# Managed by tools/screen_editor.py — do not edit by hand.
# Use the CAMPAIGNS panel in the screen editor to add or remove campaigns.
#
# _REGISTRY is the authoritative list read and written by the editor.
# ENTRIES is consumed by games/launcher/game.py at boot.
#
# Each _REGISTRY row: [label, color_name, levels_module_basename]
#   label            — 2-char string shown in the launcher carousel
#   color_name       — one of MAGENTA CYAN YELLOW GREEN ORANGE PURPLE RED
#   levels_module    — filename without .py, inside games/platformer/

_REGISTRY = [
    ['PL', 'MAGENTA', 'levels'],
]

from lib.engine.colors import MAGENTA, CYAN, YELLOW, GREEN, ORANGE, PURPLE, RED

_COLORS = {
    'MAGENTA': MAGENTA,
    'CYAN':    CYAN,
    'YELLOW':  YELLOW,
    'GREEN':   GREEN,
    'ORANGE':  ORANGE,
    'PURPLE':  PURPLE,
    'RED':     RED,
}


def _make_factory(mod_name):
    """Return a factory function that loads a PlatformerGame from mod_name."""
    def _factory(hal):
        from games.platformer.game import PlatformerGame
        _ns = {}
        exec('from games.platformer.' + mod_name + ' import LEVELS as _L', _ns)
        return PlatformerGame(hal, levels=_ns['_L'])
    return _factory


ENTRIES = [
    (r[0], _COLORS.get(r[1], MAGENTA), _make_factory(r[2]))
    for r in _REGISTRY
]
