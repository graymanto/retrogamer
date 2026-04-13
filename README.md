# Retrogamer

Games and a development framework for the [Kitronik ZIP96 Retrogamer](https://kitronik.co.uk/products/5347-kitronik-zip-96-retro-gamer-for-raspberry-pi-pico), powered by a Raspberry Pi Pico.

The project includes a **pygame desktop emulator** so games can be developed and tested on any Mac or PC without needing the hardware.

---

## Hardware

The Kitronik ZIP96 Retrogamer has:

| Feature | Detail |
|---------|--------|
| Display | 12 × 8 fully-addressable RGB LED matrix (96 LEDs) |
| Buttons | Up, Down, Left, Right, A, B |
| Audio | Piezo buzzer (30–3000 Hz) |
| Haptics | Vibration motor |
| Processor | Raspberry Pi Pico (MicroPython) |

---

## Games

### Pong

Classic two-paddle pong on the LED matrix.

- **1-player** (press `Z` on menu): you control the left paddle; the right is AI.
- **2-player** (press `X` on menu): left paddle = Up/Down keys, right paddle = A/B keys.
- Ball speeds up with each rally. First to **5 goals** wins.
- Sound feedback on paddle hit, wall bounce, and score. Vibration on goal.

### Space Invaders

Arcade-faithful Space Invaders with escalating waves.

- **8 × 3 invader grid** that marches across the screen and drops each time it hits a wall.
- Row colours: Cyan (30 pts) · Green (20 pts) · Yellow (10 pts).
- Invaders speed up as their numbers dwindle.
- Invaders shoot back. Player fires one bullet at a time.
- Waves escalate: each cleared wave starts the grid one row lower and faster.

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
│   │   ├── game.py          # BaseGame: 30fps game loop, DISPLAY_W/H constants
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
    ├── pong/
    │   ├── game.py          # PongGame(BaseGame)
    │   ├── ball.py          # Ball sprite + bounce logic
    │   ├── paddle.py        # Paddle sprite
    │   ├── ai.py            # Simple AI paddle controller
    │   └── states.py        # MenuState · PlayingState · GameOverState
    └── space_invaders/
        ├── game.py          # SpaceInvadersGame(BaseGame)
        ├── invader.py       # InvaderGrid: 2D bool array, march/hit/shoot logic
        ├── player.py        # Player ship with move-repeat input
        ├── bullet.py        # Timer-based bullet (player and invader)
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

## Desktop Setup (Mac / PC)

### Prerequisites

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) — the Python package and project manager used by this project.

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

`uv sync` automatically downloads Python 3.12 and installs all dependencies (pygame) into an isolated virtual environment. No system Python or manual `pip install` required.

### Run

```bash
uv run python run_emulator.py pong
uv run python run_emulator.py space_invaders
```

### Controls

| Key | Action |
|-----|--------|
| Arrow keys | Up / Down / Left / Right |
| `Z` | A button |
| `X` | B button |
| Gamepad left stick / D-pad | Directions |
| Gamepad button 0 / 1 | A / B |

**Pong menu:** `Z` = start 1-player (vs AI) · `X` = start 2-player

**Space Invaders:** Left/Right to move · `Z` to fire · `Z` on game-over screen to restart

---

## Deploying to the Raspberry Pi Pico

### Prerequisites

- MicroPython firmware installed on the Pico ([download](https://micropython.org/download/RPI_PICO/))
- [`mpremote`](https://docs.micropython.org/en/latest/reference/mpremote.html) installed: `pip install mpremote`
- The [Kitronik ZIP96Pico library](https://github.com/KitronikLtd/Kitronik-Pico-ZIP96-MicroPython) (`ZIP96Pico.py`) copied to the root of the Pico

### Deploy

Connect the Pico via USB, then from the repo root:

```bash
# Copy shared libraries and games
mpremote fs cp -r lib/   :lib/
mpremote fs cp -r games/ :games/

# Copy the hardware HAL
mpremote mkdir :backends
mpremote fs cp backends/hardware_hal.py :backends/hardware_hal.py

# Copy and launch the entry point
mpremote fs cp run_hardware.py :run_hardware.py
mpremote reset
```

To choose which game runs on boot, edit `run_hardware.py` before copying:

```python
GAME = "pong"           # or "space_invaders"
```

---

## Adding a New Game

1. Create `games/mygame/` with at minimum `game.py` (subclass `BaseGame`) and `states.py`.
2. Add it to `run_emulator.py`:
   ```python
   elif game_name == "mygame":
       from games.mygame.game import MyGame
       game = MyGame(hal)
   ```
3. Add it to `run_hardware.py` the same way.

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
