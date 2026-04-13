#!/usr/bin/env python3
# run_emulator.py
# Desktop entry point. Full Python 3. NOT deployed to the Pico.
#
# Usage:
#   python run_emulator.py pong
#   python run_emulator.py space_invaders
#
# Controls:
#   Arrow keys  → Up / Down / Left / Right
#   Z           → A button
#   X           → B button
#   Gamepad     → axes + buttons 0/1 also mapped

import sys
import os

# Add repo root to path so lib/ and games/ are importable
sys.path.insert(0, os.path.dirname(__file__))

from backends.emulator_hal import EmulatorHAL


def main():
    game_name = sys.argv[1] if len(sys.argv) > 1 else "pong"

    hal = EmulatorHAL(cell_size=54, bezel=24)

    if game_name == "pong":
        from games.pong.game import PongGame
        game = PongGame(hal)

    elif game_name in ("space_invaders", "si", "invaders"):
        from games.space_invaders.game import SpaceInvadersGame
        game = SpaceInvadersGame(hal)

    else:
        print("Unknown game: " + game_name)
        print("Available: pong, space_invaders")
        sys.exit(1)

    game.run()


if __name__ == "__main__":
    main()
