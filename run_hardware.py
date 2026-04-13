# run_hardware.py
# MicroPython entry point — copy this to the Raspberry Pi Pico.
# Edit GAME below to select which game to run.
#
# Deploy (using mpremote):
#   mpremote fs cp -r lib/     :lib/
#   mpremote fs cp -r games/   :games/
#   mpremote fs cp backends/hardware_hal.py :backends/hardware_hal.py
#   mpremote fs cp run_hardware.py :run_hardware.py
#   mpremote reset

import sys
sys.path.insert(0, '/lib')
sys.path.insert(0, '/games')
sys.path.insert(0, '/backends')

# ---- Select game to run ----
GAME = "pong"   # Change to "space_invaders" as needed
# ----------------------------

from backends.hardware_hal import HardwareHAL

hal = HardwareHAL()

if GAME == "pong":
    from games.pong.game import PongGame
    game = PongGame(hal)
elif GAME == "space_invaders":
    from games.space_invaders.game import SpaceInvadersGame
    game = SpaceInvadersGame(hal)

game.run()
