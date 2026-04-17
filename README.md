# Retrogamer

Games and a development framework for the [Kitronik ZIP96 Retrogamer](https://kitronik.co.uk/products/5347-kitronik-zip-96-retro-gamer-for-raspberry-pi-pico), powered by a Raspberry Pi Pico.

The project includes a **pygame desktop emulator** so games can be developed and tested on any Mac or PC without needing the hardware.

---

## Hardware

The Kitronik ZIP96 Retrogamer has:

| Feature | Detail |
|---------|--------|
| Display | 12 × 8 fully-addressable RGB LED matrix (96 LEDs) |
| Buttons | Up, Down, Left, Right, A (mapped to `Z`), B (mapped to `X`) |
| Audio | Piezo buzzer (30–3000 Hz) |
| Haptics | Vibration motor |
| Processor | Raspberry Pi Pico (MicroPython) |

---

## Games

A boot launcher lets you scroll through games with Left/Right and launch with A (`Z`).

### Pong

Classic two-paddle Pong on the LED matrix.

- **1-player** (`Z` on menu): you control the left paddle; the right is AI-controlled.
- **2-player** (`X` on menu): left paddle = Up/Down, right paddle = A(`Z`)/B(`X`).
- Ball speeds up with each rally. First to **5 goals** wins.
- Sound on paddle hit, wall bounce, and score. Vibration on goal.

| Context | Button | Action |
|---------|--------|--------|
| Menu | `Z` | Start 1-player vs AI |
| Menu | `X` | Start 2-player |
| Menu | Left | Back to launcher |
| Game | Up / Down | Move left paddle |
| Game (2P) | `Z` / `X` | Move right paddle |
| Game Over | `Z` | Play again |
| Game Over | Left | Back to launcher |

---

### Space Invaders

Arcade-faithful Space Invaders with escalating waves.

- **8 × 3 invader grid** marches across and drops each time it hits a wall.
- Row colours: Cyan (30 pts) · Green (20 pts) · Yellow (10 pts).
- Invaders speed up as their numbers dwindle.
- Invaders shoot back. Player fires one bullet at a time.
- Each cleared wave starts one row lower and faster.

| Context | Button | Action |
|---------|--------|--------|
| Menu | `Z` | Start game |
| Menu | Left | Back to launcher |
| Game | Left / Right | Move ship |
| Game | `Z` | Fire |
| Game Over | `Z` | Play again |
| Game Over | Left | Back to launcher |

---

### Snake

Classic Snake — eat food, grow longer, don't hit yourself.

- Speed increases with every 3 points scored.
- Score displayed on game-over screen.

| Context | Button | Action |
|---------|--------|--------|
| Menu | `Z` | Start game |
| Menu | Left | Back to launcher |
| Game | Up / Down / Left / Right | Steer snake |
| Game Over | `Z` | Play again |
| Game Over | Left | Back to launcher |

---

### Breakout

Classic Breakout with waves, lives, and increasing ball speed.

- **4 rows of bricks**: Red (3 pts) · Orange (2 pts) · Yellow (1 pt) · Green (1 pt).
- Score is multiplied by the current wave number.
- Ball speeds up with every paddle hit (gently). Each new wave adds a base speed bonus.
- **3 lives** — shown as dots during the launch phase.
- Clear all bricks to advance to the next wave.

| Context | Button | Action |
|---------|--------|--------|
| Menu | `Z` | Start game |
| Menu | Left | Back to launcher |
| Game | Left / Right | Move paddle |
| Game | `Z` | Launch ball |
| Game Over | `Z` | Play again |
| Game Over | Left | Back to launcher |

---

### Simon Says

Classic Simon Says memory sequence game.

- Four coloured quadrants fill the display: Red (top-left), Blue (top-right), Green (bottom-left), Yellow (bottom-right).
- Watch the sequence, then repeat it. One new element is added each round.
- Wrong press ends the game. Score = rounds fully completed.

| Context | Button | Action |
|---------|--------|--------|
| Menu | Down | Start game |
| Menu | Up | Back to launcher |
| Game | Left | Press Red zone (top-left) |
| Game | Right | Press Blue zone (top-right) |
| Game | `Z` | Press Green zone (bottom-left) |
| Game | `X` | Press Yellow zone (bottom-right) |
| Game Over | Down | Play again |
| Game Over | Up | Back to launcher |

---

### Frogger

Guide the frog from the bottom bank to the top, crossing two lanes of traffic and three lanes of river.

- **Road lanes** (rows 5–6): cars scroll left and right — don't get hit.
- **River lanes** (rows 1–3): logs scroll left and right — stay on a log or drown.
- Reach the top row to score. The frog resets to the start for another crossing.
- **3 lives.** Score = successful crossings.
- **5 levels** of increasing speed, unlocked every 3 crossings. A brief level-up flash announces each new level. Level progress persists across deaths within a game.

| Context | Button | Action |
|---------|--------|--------|
| Menu | Down | Start game |
| Menu | Up | Back to launcher |
| Game | Up / Down / Left / Right | Hop one cell |
| Game Over | Down | Play again |
| Game Over | Up | Back to launcher |

---

### Flappy Bird

Guide the bird through an endless stream of pipes by tapping to flap.

- Bird falls continuously under gravity — tap `A` or `B` to flap upward.
- Pipes have a 3-row gap; passing through scores 1 point.
- Pipes speed up every 5 points scored (up to a cap).
- Hit a pipe or fly off the top or bottom of the screen to die.

| Context | Button | Action |
|---------|--------|--------|
| Menu | `A` or Down | Start game |
| Menu | Up | Back to launcher |
| Game | `A` or `B` | Flap |
| Game Over | Down | Play again |
| Game Over | Up | Back to launcher |

---

### Tetris

Classic Tetris on a 6-wide playfield with a sidebar showing the next piece.

- All 7 tetrominoes (I, O, T, S, Z, J, L) with full rotation.
- Hold Down to soft-drop; press `B` to hard-drop instantly.
- Clear lines to score — more lines at once scores more. Score is multiplied by the current level.
- Speed increases every 5 lines cleared.
- Game ends when a new piece cannot be placed at its spawn position.

| Context | Button | Action |
|---------|--------|--------|
| Menu | `Z` or Down | Start game |
| Menu | Left | Back to launcher |
| Game | Left / Right | Move piece |
| Game | `Z` or Up | Rotate piece |
| Game | Down | Soft drop |
| Game | `X` | Hard drop |
| Game Over | `Z` or Down | Play again |
| Game Over | Left | Back to launcher |

---

## Desktop Setup (Mac / PC)

### Prerequisites

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) — the Python package manager used by this project.

**Mac / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Install

```bash
git clone https://github.com/YOUR_USERNAME/retrogamer.git
cd retrogamer
uv sync
```

`uv sync` downloads Python 3.12 and installs all dependencies (pygame) into an isolated virtual environment. No system Python or manual `pip install` required.

### Run

```bash
# Boot launcher (scroll with Left/Right, launch with Z)
uv run python run_emulator.py

# Launch a specific game directly
uv run python run_emulator.py pong
uv run python run_emulator.py space_invaders
uv run python run_emulator.py snake
uv run python run_emulator.py breakout
uv run python run_emulator.py simon
uv run python run_emulator.py frogger
uv run python run_emulator.py flappy
uv run python run_emulator.py tetris
```

### Emulator controls

| Key | Maps to |
|-----|---------|
| Arrow keys | Up / Down / Left / Right |
| `Z` | A button |
| `X` | B button |
| Gamepad left stick / D-pad | Directions |
| Gamepad buttons 0 / 1 | A / B |

---

## Deploying to the Raspberry Pi Pico

### Prerequisites

- MicroPython firmware installed on the Pico ([download](https://micropython.org/download/RPI_PICO/))
- [`mpremote`](https://docs.micropython.org/en/latest/reference/mpremote.html) installed: `pip install mpremote`
- The [Kitronik ZIP96Pico library](https://github.com/KitronikLtd/Kitronik-Pico-ZIP96-MicroPython) (`ZIP96Pico.py`) copied to the root of the Pico

### Deploy

Connect the Pico via USB, then from the repo root:

```bash
# Copy shared libraries and all games
mpremote fs cp -r lib/   :lib/
mpremote fs cp -r games/ :games/

# Copy the hardware HAL
mpremote mkdir :backends
mpremote fs cp backends/hardware_hal.py :backends/hardware_hal.py

# Copy and launch the entry point
mpremote fs cp run_hardware.py :run_hardware.py
mpremote reset
```

The device boots into the launcher automatically. Scroll with Left/Right, launch a game with A.

---

## Project Structure

```
retrogamer/
├── run_emulator.py          # Desktop entry point
├── run_hardware.py          # Pico entry point (deploy this to the device)
├── pyproject.toml           # uv project file
├── LICENSE
│
├── lib/                     # Shared libraries — MicroPython-compatible
│   ├── hal/
│   │   ├── __init__.py      # Button constants: UP DOWN LEFT RIGHT A B
│   │   └── interface.py     # BaseHAL duck-typed interface
│   ├── engine/
│   │   ├── colors.py        # Color constants + dim() / blend() helpers
│   │   ├── font.py          # 3×5 pixel font for digits and letters
│   │   ├── game.py          # BaseGame: 30 fps game loop, DISPLAY_W/H constants
│   │   ├── sprite.py        # Sprite with integer fixed-point physics + AABB collision
│   │   └── state.py         # StateMachine (stack-based) + GameState base class
│   └── utils/
│       └── math_helpers.py  # clamp(), sign(), lerp_int() — no math import needed
│
├── backends/                # Platform-specific — never imported by lib/ or games/
│   ├── emulator_hal.py      # EmulatorHAL: pygame window, keyboard, sound
│   ├── emulator_display.py  # 12×8 LED grid with bezel and button footer strip
│   ├── emulator_input.py    # Keyboard (arrows / Z / X) + gamepad → HAL buttons
│   ├── emulator_audio.py    # Sine-wave synthesis via stdlib array (no numpy)
│   └── hardware_hal.py      # HardwareHAL: wraps KitronikZIP96 (MicroPython only)
│
└── games/
    ├── launcher/
    │   └── game.py          # Boot carousel — scroll games, press A to launch
    ├── pong/
    │   ├── game.py          # PongGame(BaseGame)
    │   ├── ball.py          # Ball sprite + bounce/angle logic
    │   ├── paddle.py        # Paddle sprite
    │   ├── ai.py            # Simple AI paddle controller
    │   └── states.py        # MenuState · PlayingState · GameOverState
    ├── space_invaders/
    │   ├── game.py          # SpaceInvadersGame(BaseGame)
    │   ├── invader.py       # InvaderGrid: 2D bool array, march/hit/shoot logic
    │   ├── player.py        # Player ship with move-repeat input
    │   ├── bullet.py        # Timer-based bullet (player and invader)
    │   └── states.py        # MenuState · PlayingState · GameOverState
    ├── snake/
    │   ├── game.py          # SnakeGame(BaseGame)
    │   └── states.py        # MenuState · PlayingState · GameOverState
    ├── breakout/
    │   ├── game.py          # BreakoutGame(BaseGame)
    │   ├── ball.py          # Ball sprite + paddle bounce + speed ramp
    │   ├── paddle.py        # Paddle sprite
    │   ├── bricks.py        # BrickGrid: 4×12 grid with point values per row
    │   └── states.py        # MenuState · PlayingState · GameOverState
    ├── simon/
    │   ├── game.py          # SimonGame(BaseGame)
    │   └── states.py        # MenuState · PlayingState · GameOverState
    ├── frogger/
    │   ├── game.py          # FroggerGame(BaseGame)
    │   └── states.py        # MenuState · PlayingState · GameOverState
    ├── flappy/
    │   ├── game.py          # FlappyGame(BaseGame)
    │   └── states.py        # MenuState · PlayingState · GameOverState
    └── tetris/
        ├── game.py          # TetrisGame(BaseGame)
        └── states.py        # MenuState · PlayingState · GameOverState
```

### Architecture

The project uses a strict three-layer design so game code is identical on hardware and desktop:

```
Game code  (lib/ + games/)   — MicroPython-compatible Python
     ↓ calls
BaseHAL interface            — duck-typed, no platform imports
     ↓ implemented by
EmulatorHAL  (Mac/PC)   |   HardwareHAL  (Raspberry Pi Pico)
```

**Game code never imports from `backends/`.** The HAL is injected at startup by the entry point. Swapping hardware for the emulator requires zero changes to game logic.

**Integer fixed-point physics** (`SCALE = 256`): all positions and velocities are stored as integers (real_value × 256). This avoids floats entirely, keeping the engine fast and MicroPython-friendly.

---

## Adding a New Game

1. Create `games/mygame/` with `__init__.py`, `game.py` (subclass `BaseGame`), and `states.py`.
2. Add a factory function and entry to `GAME_REGISTRY` in `games/launcher/game.py`:
   ```python
   def _make_mygame(hal):
       from games.mygame.game import MyGame
       return MyGame(hal)

   GAME_REGISTRY = [
       ...
       ("MG", CYAN, _make_mygame),   # two-char label, colour, factory
   ]
   ```
3. Add a direct-launch shortcut to `run_emulator.py` for development convenience.

Game code may use anything in `lib/` freely. It must not import from `backends/`. The HAL is always available as `self.hal` inside `BaseGame` and `GameState`.

### MicroPython Compatibility Rules

All code in `lib/` and `games/` must remain MicroPython-compatible:

| Avoid | Use instead |
|-------|-------------|
| `from typing import ...` | Delete — duck typing only |
| `@dataclass` | Plain `__init__` |
| `import math` | `lib/utils/math_helpers.py` |
| `time.time()` | `self.hal.ticks_ms()` |
| `pathlib.Path` | String paths |
| Walrus operator `:=` | Separate assignment |
| `match` / `case` | `if` / `elif` chain |
| `Enum` | String or integer constants |
| F-string format specs `{x:.2f}` | Simple `str(x)` or `f"{x}"` |

---

## License

MIT — see [LICENSE](LICENSE).
