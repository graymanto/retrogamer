#!/usr/bin/env python3
# run_emulator.py
# Desktop entry point. Full Python 3. NOT deployed to the Pico.
#
# Usage:
#   python run_emulator.py              — launcher (default)
#   python run_emulator.py pong         — launch Pong directly
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
    hal = EmulatorHAL(cell_size=54, bezel=24)

    if len(sys.argv) < 2:
        # Default: run the launcher, loop back after each game exits
        from games.launcher.game import LauncherGame, GAME_REGISTRY
        while True:
            launcher = LauncherGame(hal)
            launcher.run()
            game = GAME_REGISTRY[launcher.selected][2](hal)
            game.run()

    else:
        # Direct launch for development convenience
        game_name = sys.argv[1]
        if game_name == "pong":
            from games.pong.game import PongGame
            PongGame(hal).run()

        elif game_name in ("space_invaders", "si", "invaders"):
            from games.space_invaders.game import SpaceInvadersGame
            SpaceInvadersGame(hal).run()

        elif game_name in ("snake", "sn"):
            from games.snake.game import SnakeGame
            SnakeGame(hal).run()

        elif game_name in ("breakout", "br"):
            from games.breakout.game import BreakoutGame
            BreakoutGame(hal).run()

        elif game_name in ("simon", "ss"):
            from games.simon.game import SimonGame
            SimonGame(hal).run()

        elif game_name in ("frogger", "fr"):
            from games.frogger.game import FroggerGame
            FroggerGame(hal).run()

        elif game_name in ("flappy", "fb"):
            from games.flappy.game import FlappyGame
            FlappyGame(hal).run()

        elif game_name in ("tetris", "te"):
            from games.tetris.game import TetrisGame
            TetrisGame(hal).run()

        elif game_name in ("platformer", "pl"):
            from games.platformer.game import PlatformerGame
            levels = None
            if "--levels" in sys.argv:
                lvl_path = sys.argv[sys.argv.index("--levels") + 1]
                with open(lvl_path) as _f:
                    _ns = {}
                    exec(_f.read(), _ns)
                    levels = _ns.get("LEVELS")
            PlatformerGame(hal, levels=levels).run()

        else:
            print("Unknown game: " + game_name)
            print("Available: pong, space_invaders, snake, breakout, simon, frogger, flappy, tetris, platformer")
            sys.exit(1)


if __name__ == "__main__":
    main()
