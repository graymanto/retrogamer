# run_hardware.py
# MicroPython entry point — copy this to the Raspberry Pi Pico.
#
# Deploy (using mpremote):
#   mpremote fs cp -r lib/       :lib/
#   mpremote fs cp -r games/     :games/
#   mpremote fs cp backends/hardware_hal.py :backends/hardware_hal.py
#   mpremote fs cp run_hardware.py :run_hardware.py
#   mpremote reset

import sys
sys.path.insert(0, '/lib')
sys.path.insert(0, '/games')
sys.path.insert(0, '/backends')

from backends.hardware_hal import HardwareHAL
from games.launcher.game   import LauncherGame, GAME_REGISTRY

hal = HardwareHAL()

while True:
    launcher = LauncherGame(hal)
    launcher.run()
    game = GAME_REGISTRY[launcher.selected][2](hal)
    game.run()
