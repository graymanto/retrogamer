# Retrogamer

Games and a development framework for the [Kitronik ZIP96 Retrogamer](https://kitronik.co.uk/products/5347-kitronik-zip-96-retro-gamer-for-raspberry-pi-pico), powered by a Raspberry Pi Pico.

The project includes a **pygame desktop emulator** so games can be developed and tested on any Mac or PC without needing the hardware, and a **graphical level editor** for designing custom Platformer campaigns.

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

A boot launcher lets you scroll through games with Left/Right and launch with A.

### Pong

Classic two-paddle Pong on the LED matrix.

- **1-player** (A on menu): you control the left paddle; the right is AI-controlled.
- **2-player** (B on menu): left paddle = Up/Down, right paddle = A/B.
- Ball speeds up with each rally. First to **5 goals** wins.
- Sound on paddle hit, wall bounce, and score. Vibration on goal.

| Context | Button | Action |
|---------|--------|--------|
| Menu | A | Start 1-player vs AI |
| Menu | B | Start 2-player |
| Menu | Left | Back to launcher |
| Game | Up / Down | Move left paddle |
| Game (2P) | A / B | Move right paddle |
| Game Over | A | Play again |
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
| Menu | A | Start game |
| Menu | Left | Back to launcher |
| Game | Left / Right | Move ship |
| Game | A | Fire |
| Game Over | A | Play again |
| Game Over | Left | Back to launcher |

---

### Snake

Classic Snake — eat food, grow longer, don't hit yourself.

- Speed increases with every 3 points scored.
- Score displayed on game-over screen.

| Context | Button | Action |
|---------|--------|--------|
| Menu | A | Start game |
| Menu | Left | Back to launcher |
| Game | Up / Down / Left / Right | Steer snake |
| Game Over | A | Play again |
| Game Over | Left | Back to launcher |

---

### Breakout

Classic Breakout with waves, lives, and increasing ball speed.

- **4 rows of bricks**: Red (3 pts) · Orange (2 pts) · Yellow (1 pt) · Green (1 pt).
- Score is multiplied by the current wave number.
- Ball speeds up with every paddle hit. Each new wave adds a base speed bonus.
- **3 lives** — shown as dots during the launch phase.
- Clear all bricks to advance to the next wave.

| Context | Button | Action |
|---------|--------|--------|
| Menu | A | Start game |
| Menu | Left | Back to launcher |
| Game | Left / Right | Move paddle |
| Game | A | Launch ball |
| Game Over | A | Play again |
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
| Game | A | Press Green zone (bottom-left) |
| Game | B | Press Yellow zone (bottom-right) |
| Game Over | Down | Play again |
| Game Over | Up | Back to launcher |

---

### Frogger

Guide the frog from the bottom bank to the top, crossing two lanes of traffic and three lanes of river.

- **Road lanes** (rows 5–6): cars scroll left and right — don't get hit.
- **River lanes** (rows 1–3): logs scroll left and right — stay on a log or drown.
- Reach the top row to score. The frog resets to the start for another crossing.
- **3 lives.** Score = successful crossings.
- **5 levels** of increasing speed, unlocked every 3 crossings.

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

- Bird falls continuously under gravity — tap A or B to flap upward.
- Pipes have a 3-row gap; passing through scores 1 point.
- Pipes speed up every 5 points scored (up to a cap).
- Hit a pipe or fly off the screen to die.

| Context | Button | Action |
|---------|--------|--------|
| Menu | A or Down | Start game |
| Menu | Up | Back to launcher |
| Game | A or B | Flap |
| Game Over | Down | Play again |
| Game Over | Up | Back to launcher |

---

### Tetris

Classic Tetris on a 6-wide playfield with a sidebar showing the next piece.

- All 7 tetrominoes (I, O, T, S, Z, J, L) with full rotation.
- Hold Down to soft-drop; press B to hard-drop instantly.
- Clear lines to score — more lines at once scores more. Score multiplied by current level.
- Speed increases every 5 lines cleared.

| Context | Button | Action |
|---------|--------|--------|
| Menu | A or Down | Start game |
| Menu | Left | Back to launcher |
| Game | Left / Right | Move piece |
| Game | A or Up | Rotate piece |
| Game | Down | Soft drop |
| Game | B | Hard drop |
| Game Over | A or Down | Play again |
| Game Over | Left | Back to launcher |

---

### Platformer

A scrolling platformer engine that also supports **auto-scroll / Geometry Dash mode**. Multiple level campaigns can be created with the [Level Editor](#level-editor) and deployed independently to the device — each appears as its own entry in the launcher carousel.

- Tile types: platforms, hazards (instant death), coins (+1 score), and an exit tile.
- **Normal mode** (`scroll: 0`): walk left/right and jump freely to reach the exit.
- **Auto-scroll mode** (`scroll: N`): the world scrolls at N pixels/second; jump to survive.
- **3 lives** shown as dots along the top edge.
- Three built-in levels ship with the project.

| Context | Button | Action |
|---------|--------|--------|
| Menu | A or Down | Start game |
| Menu | Left | Back to launcher |
| Game (normal) | Left / Right | Walk |
| Game (normal) | Up or A | Jump |
| Game (auto-scroll) | Up or A | Jump |
| Game Over | A or Down | Play again |
| Game Over | Left | Back to launcher |

---

## Level Editor

`tools/screen_editor.py` is a desktop pygame application for designing Platformer levels. It runs on Mac/PC — no hardware required.

```bash
# Edit the built-in levels (games/platformer/levels.py)
uv run python tools/screen_editor.py

# Create or edit a custom campaign (gitignored — stays on your machine)
uv run python tools/screen_editor.py --file games/platformer/custom_world1.py

# Open a specific level index within a file
uv run python tools/screen_editor.py --file games/platformer/custom_world1.py --level 2
```

### Editor layout

```
┌────────────────────────────────────────────┬──────────────┐
│                                            │  Tile        │
│           12 × 8 paint grid                │  palette     │
│         (each cell = one LED pixel)        │  + controls  │
│                                            │              │
└──────────────────────── scrollbar ─────────┴──────────────┘
         [ Add Level ]  [ Delete Level ]  [ CAMPAIGNS ]
```

### Editor controls

| Input | Action |
|-------|--------|
| Left-click / drag | Paint selected tile |
| Right-click / drag | Erase (paint sky) |
| Scroll wheel | Scroll level horizontally |
| `1` – `6` | Select tile from palette |
| `S` | Save levels file |
| Left / Right arrow | Scroll level one column |
| PgUp / PgDn | Previous / next level |

### Tile palette

| Key | Tile | Description |
|-----|------|-------------|
| `1` | Sky | Empty / background |
| `2` | Platform | Solid — player lands on and is blocked by these |
| `3` | Hazard | Passable but lethal on contact |
| `4` | Coin | Collectible — +1 score each |
| `5` | Exit | Completes the level (normal mode only) |
| `6` | Spawn | Where the player starts — treated as solid |

### Level width and scroll speed

Use the **Add Col / Remove Col** buttons in the panel to make a level wider than the 12-column viewport (up to any width). The **scroll speed** control sets auto-scroll mode:

- `0` — normal platformer (player walks freely)
- `≥ 1` — auto-scroll at that many pixels per second (Geometry Dash style)

### Deploying a custom campaign

Click **CAMPAIGNS** in the editor to open the campaign manager. Enter a 2-character label, choose a colour, and click **Deploy**. The editor updates `games/platformer/campaigns.py` and `deploy.sh` automatically — the campaign appears in the hardware launcher on next deploy.

Custom campaign files must follow the naming convention `custom_*.py` inside `games/platformer/` so they are gitignored (private to your machine) but importable by MicroPython on the Pico.

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

`uv sync` downloads Python 3.12 and installs pygame into an isolated virtual environment — no system Python or manual `pip install` needed.

### Run

```bash
# Boot launcher (scroll with Left/Right, launch with A)
uv run python run_emulator.py

# Launch a specific game directly for development
uv run python run_emulator.py pong
uv run python run_emulator.py space_invaders
uv run python run_emulator.py snake
uv run python run_emulator.py breakout
uv run python run_emulator.py simon
uv run python run_emulator.py frogger
uv run python run_emulator.py flappy
uv run python run_emulator.py tetris
uv run python run_emulator.py platformer

# Run the level editor
uv run python tools/screen_editor.py
```

### Emulator controls

The emulator accepts keyboard input and USB gamepads simultaneously.

#### Keyboard

| Key | Maps to |
|-----|---------|
| Arrow keys | Up / Down / Left / Right |
| `Z` | A button |
| `X` | B button |
| `W` `A` `S` `D` | Up / Left / Down / Right (alternative) |

#### Xbox controller (or any standard gamepad)

| Control | Maps to |
|---------|---------|
| D-pad | Up / Down / Left / Right |
| Left stick | Up / Down / Left / Right |
| A button | A |
| B button | B |

Plug the controller in before launching. Multiple input sources work simultaneously — keyboard and controller can be used at the same time.

---

## Deploying to the Raspberry Pi Pico

### Prerequisites

- MicroPython firmware installed on the Pico ([download](https://micropython.org/download/RPI_PICO/))
- [`mpremote`](https://docs.micropython.org/en/latest/reference/mpremote.html) installed: `pip install mpremote`
- The [Kitronik ZIP96Pico library](https://github.com/KitronikLtd/Kitronik-Pico-ZIP96-MicroPython) (`ZIP96Pico.py`) copied to the root of the Pico

### Deploy

Connect the Pico via USB, then from the repo root:

```bash
# Auto-detect port
./deploy.sh

# Or specify the port explicitly
./deploy.sh /dev/cu.usbmodem1101
```

`deploy.sh` creates the full directory tree on the Pico, copies all game files, and resets the device. It also copies any campaign level files registered via the level editor.

The device boots into the launcher automatically on reset. Scroll with Left/Right, launch a game with A.

---

## Project Structure

```
retrogamer/
├── run_emulator.py          # Desktop entry point
├── run_hardware.py          # Pico entry point (deployed as main.py)
├── deploy.sh                # One-command deploy to Pico via mpremote
├── pyproject.toml           # uv project file (Python 3.12 + pygame)
│
├── lib/                     # Shared libraries — MicroPython-compatible
│   ├── hal/
│   │   ├── __init__.py      # Button constants: UP DOWN LEFT RIGHT A B
│   │   └── interface.py     # BaseHAL duck-typed interface
│   ├── engine/
│   │   ├── colors.py        # Color constants + dim() / blend() helpers
│   │   ├── font.py          # 3×5 pixel font (digits and capital letters)
│   │   ├── game.py          # BaseGame: 30 fps game loop, DISPLAY_W/H constants
│   │   ├── sprite.py        # Sprite: integer fixed-point physics + AABB collision
│   │   └── state.py         # StateMachine (stack-based) + GameState base class
│   └── utils/
│       └── math_helpers.py  # clamp(), sign(), lerp_int() — no math import needed
│
├── backends/                # Platform-specific — never imported by lib/ or games/
│   ├── emulator_hal.py      # EmulatorHAL: wires display, input, and audio together
│   ├── emulator_display.py  # 12×8 LED grid rendered in a pygame window with bezel
│   ├── emulator_input.py    # Keyboard + Xbox controller / gamepad → HAL buttons
│   ├── emulator_audio.py    # Sine-wave tone synthesis (no numpy required)
│   └── hardware_hal.py      # HardwareHAL: wraps KitronikZIP96 (MicroPython only)
│
├── games/
│   ├── launcher/
│   │   └── game.py          # Boot carousel — scroll games, press A to launch
│   ├── pong/                # PongGame: 1P vs AI or 2P, score to 5
│   ├── space_invaders/      # SpaceInvadersGame: escalating waves, invaders fire back
│   ├── snake/               # SnakeGame: grow, don't self-collide, speed escalates
│   ├── breakout/            # BreakoutGame: 4 brick rows, waves, speed ramp
│   ├── simon/               # SimonGame: 4-button sequence memory
│   ├── frogger/             # FroggerGame: road + river, 5 speed levels
│   ├── flappy/              # FlappyGame: endless pipes, gravity, tap to flap
│   ├── tetris/              # TetrisGame: 6-wide playfield, all 7 tetrominoes
│   └── platformer/
│       ├── game.py          # PlatformerGame(BaseGame) — accepts a levels argument
│       ├── states.py        # MenuState · PlayingState · GameOverState + physics
│       ├── levels.py        # Built-in campaign (3 levels, edited via screen editor)
│       └── campaigns.py     # Campaign registry — managed by tools/screen_editor.py
│
└── tools/
    └── screen_editor.py     # Desktop level editor: paint tiles, set scroll, deploy campaigns
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
4. Add the game files to `deploy.sh` so they are copied to the Pico.

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
