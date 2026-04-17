#!/usr/bin/env bash
# deploy.sh — Copy all game files to the Raspberry Pi Pico via mpremote.
#
# Usage:
#   ./deploy.sh                          # auto-detect port
#   ./deploy.sh /dev/cu.usbmodem1101     # specify port explicitly
#
# Requires: pip install mpremote

set -euo pipefail

PORT=${1:-}

# ── Helpers ───────────────────────────────────────────────────────────────────

mp() {
    if [ -n "$PORT" ]; then
        mpremote connect "$PORT" "$@"
    else
        mpremote "$@"
    fi
}

mkdir_remote() {
    # Silently ignore "already exists" errors
    mp fs mkdir ":$1" 2>/dev/null || true
}

cp_file() {
    echo "  $1"
    mp fs cp "$1" ":$1"
}

# ── Preflight ─────────────────────────────────────────────────────────────────

if ! command -v mpremote &>/dev/null; then
    echo "ERROR: mpremote not found."
    echo "Install it with:  pip install mpremote"
    exit 1
fi

echo "=== Retrogamer deploy ==="
[ -n "$PORT" ] && echo "Port: $PORT" || echo "Port: auto-detect"
echo ""

# ── Create directory tree ─────────────────────────────────────────────────────

echo "Creating directories..."
mkdir_remote lib
mkdir_remote lib/hal
mkdir_remote lib/engine
mkdir_remote lib/utils
mkdir_remote backends
mkdir_remote games
mkdir_remote games/launcher
mkdir_remote games/pong
mkdir_remote games/space_invaders
mkdir_remote games/snake
mkdir_remote games/breakout
mkdir_remote games/simon
mkdir_remote games/frogger
mkdir_remote games/flappy
mkdir_remote games/tetris

# ── Copy files ────────────────────────────────────────────────────────────────

echo ""
echo "Copying lib/..."
for f in \
    lib/hal/__init__.py \
    lib/hal/interface.py \
    lib/engine/__init__.py \
    lib/engine/colors.py \
    lib/engine/font.py \
    lib/engine/game.py \
    lib/engine/sprite.py \
    lib/engine/state.py \
    lib/utils/__init__.py \
    lib/utils/math_helpers.py
do
    cp_file "$f"
done

echo ""
echo "Copying backends/..."
cp_file backends/hardware_hal.py

echo ""
echo "Copying games/..."
for f in \
    games/__init__.py \
    games/launcher/__init__.py \
    games/launcher/game.py \
    games/pong/__init__.py \
    games/pong/game.py \
    games/pong/states.py \
    games/pong/ball.py \
    games/pong/paddle.py \
    games/pong/ai.py \
    games/space_invaders/__init__.py \
    games/space_invaders/game.py \
    games/space_invaders/states.py \
    games/space_invaders/invader.py \
    games/space_invaders/player.py \
    games/space_invaders/bullet.py \
    games/snake/__init__.py \
    games/snake/game.py \
    games/snake/states.py \
    games/breakout/__init__.py \
    games/breakout/game.py \
    games/breakout/states.py \
    games/breakout/ball.py \
    games/breakout/paddle.py \
    games/breakout/bricks.py \
    games/simon/__init__.py \
    games/simon/game.py \
    games/simon/states.py \
    games/frogger/__init__.py \
    games/frogger/game.py \
    games/frogger/states.py \
    games/flappy/__init__.py \
    games/flappy/game.py \
    games/flappy/states.py \
    games/tetris/__init__.py \
    games/tetris/game.py \
    games/tetris/states.py
do
    cp_file "$f"
done

echo ""
echo "Copying entry point as main.py (MicroPython runs this on boot)..."
mp fs cp run_hardware.py :main.py

# ── Reset ─────────────────────────────────────────────────────────────────────

echo ""
echo "Resetting Pico..."
mp reset

echo ""
echo "=== Deploy complete ==="
