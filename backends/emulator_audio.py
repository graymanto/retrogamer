# backends/emulator_audio.py
# Desktop-only. Full Python 3 + pygame.
# Synthesizes tones using stdlib array module (no numpy dependency).
# Gracefully degrades to silent no-op if pygame.mixer is unavailable.

import array
import math

SAMPLE_RATE  = 22050   # Hz — lower rate keeps buffer sizes small
AMPLITUDE    = 16000   # 16-bit signed range is -32768 to 32767
MAX_CHANNELS = 4       # mixer channels for simultaneous sounds

try:
    import pygame
    import pygame.mixer as _mixer
    _MIXER_OK = True
except (ImportError, NotImplementedError):
    _MIXER_OK = False


class EmulatorAudio:
    """Sine-wave tone synthesis via pygame.mixer using stdlib array.
    Falls back to a silent no-op if the mixer is unavailable (headless mode)."""

    def __init__(self):
        self._available = False
        if not _MIXER_OK:
            return

        # Initialise mono 16-bit mixer
        try:
            _mixer.init(
                frequency=SAMPLE_RATE,
                size=-16,        # signed 16-bit
                channels=1,      # mono
                buffer=256,
            )
        except Exception:
            return   # Mixer not available (e.g. dummy audio driver)

        try:
            _mixer.set_num_channels(MAX_CHANNELS)
            self._tone_channel = _mixer.Channel(0)
            self._sfx_channel  = _mixer.Channel(1)
            self._tone_cache   = {}
            self._available    = True
        except Exception:
            pass

    def play_tone(self, freq, duration_ms=None):
        """Play a sine-wave tone.
        If duration_ms is None, loops indefinitely until stop_tone()."""
        if not self._available:
            return
        freq = int(freq)
        if freq <= 0:
            return

        if duration_ms is not None:
            sound = self._make_tone(freq, duration_ms)
            self._sfx_channel.play(sound, loops=0)
        else:
            # Use a cached 500ms loop for indefinite play
            if freq not in self._tone_cache:
                self._tone_cache[freq] = self._make_tone(freq, 500)
            self._tone_channel.play(self._tone_cache[freq], loops=-1)

    def stop_tone(self):
        """Stop the indefinitely-looping tone channel."""
        if self._available:
            self._tone_channel.stop()

    def _make_tone(self, freq, duration_ms):
        """Generate a sine wave Sound object using stdlib array."""
        n_samples = SAMPLE_RATE * duration_ms // 1000
        if n_samples == 0:
            n_samples = 1

        buf = array.array('h', [0] * n_samples)
        two_pi_f_over_sr = 2.0 * math.pi * freq / SAMPLE_RATE

        # Apply a simple fade-in/out envelope (10% of samples) to avoid clicks
        fade_samples = max(1, n_samples // 10)

        for i in range(n_samples):
            val = int(AMPLITUDE * math.sin(two_pi_f_over_sr * i))
            # Fade in
            if i < fade_samples:
                val = val * i // fade_samples
            # Fade out
            elif i >= n_samples - fade_samples:
                val = val * (n_samples - i) // fade_samples
            buf[i] = val

        return _mixer.Sound(buffer=buf)
