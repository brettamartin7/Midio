from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
import time

import numpy as np
import pygame
import pygame.midi


@dataclass(frozen=True)
class SynthPreset:
    key: str
    name: str
    partials: tuple
    attack: float
    decay: float
    sustain: float
    release_ms: int
    gm_program: int
    strategy: "SoundStrategy"
    loop: bool = False


class SoundStrategy(ABC):
    """Strategy interface for rendering a preset into a playable note."""

    @abstractmethod
    def render(self, note, preset, sample_rate, duration):
        raise NotImplementedError


class HarmonicSoundStrategy(SoundStrategy):
    def render(self, note, preset, sample_rate, duration):
        frequency = 440.0 * (2.0 ** ((note - 69.0) / 12.0))
        sample_count = int(sample_rate * duration)
        t = np.arange(sample_count, dtype=np.float32) / sample_rate
        wave = np.zeros(sample_count, dtype=np.float32)

        for ratio, amplitude in preset.partials:
            wave += amplitude * np.sin(2 * np.pi * frequency * ratio * t)

        attack = max(preset.attack, 0.001)
        decay = max(preset.decay, 0.001)
        attack_env = np.minimum(t / attack, 1.0)
        decay_env = preset.sustain + (1.0 - preset.sustain) * np.exp(
            -np.maximum(t - attack, 0.0) / decay
        )
        envelope = np.where(t < attack, attack_env, decay_env)
        wave *= envelope

        peak = np.max(np.abs(wave))
        if peak:
            wave = wave / peak
        samples = (wave * 32767).astype(np.int16)
        stereo = np.column_stack((samples, samples))
        return pygame.sndarray.make_sound(stereo)


class BellSoundStrategy(HarmonicSoundStrategy):
    """Give higher inharmonic partials the faster decay of a struck bell."""

    def render(self, note, preset, sample_rate, duration):
        frequency = 440.0 * (2.0 ** ((note - 69.0) / 12.0))
        sample_count = int(sample_rate * duration)
        t = np.arange(sample_count, dtype=np.float32) / sample_rate
        wave = np.zeros(sample_count, dtype=np.float32)

        for ratio, amplitude in preset.partials:
            partial_decay = max(preset.decay / (ratio ** 0.7), 0.02)
            wave += amplitude * np.sin(
                2 * np.pi * frequency * ratio * t
            ) * np.exp(-t / partial_decay)

        attack = max(preset.attack, 0.001)
        wave *= np.minimum(t / attack, 1.0)
        peak = np.max(np.abs(wave))
        if peak:
            wave = wave / peak
        samples = (wave * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(np.column_stack((samples, samples)))


class GrandPianoSoundStrategy(SoundStrategy):
    """Approximate piano strings with stretched, detuned partials and a hammer transient."""

    def render(self, note, preset, sample_rate, duration):
        frequency = 440.0 * (2.0 ** ((note - 69.0) / 12.0))
        sample_count = int(sample_rate * duration)
        t = np.arange(sample_count, dtype=np.float32) / sample_rate
        left = np.zeros(sample_count, dtype=np.float32)
        right = np.zeros(sample_count, dtype=np.float32)

        # Higher piano strings are stiffer, so their partials sit slightly sharp
        # of exact integer multiples. The effect naturally grows in the high range.
        stiffness = min(0.00025 + (frequency / 6000.0) ** 2 * 0.003, 0.012)
        for harmonic, amplitude in preset.partials:
            stretched_ratio = harmonic * np.sqrt(1.0 + stiffness * harmonic ** 2)
            partial_decay = max(preset.decay / (harmonic ** 0.72), 0.12)
            envelope = np.exp(-t / partial_decay)

            # Two slightly detuned strings create the gentle beating of a piano.
            detune = 0.0012
            left += amplitude * np.sin(
                2 * np.pi * frequency * stretched_ratio * (1.0 - detune) * t
            ) * envelope
            right += amplitude * np.sin(
                2 * np.pi * frequency * stretched_ratio * (1.0 + detune) * t
            ) * envelope

        attack = max(preset.attack, 0.001)
        attack_envelope = np.minimum(t / attack, 1.0)
        left *= attack_envelope
        right *= attack_envelope

        # A short, quiet broadband transient suggests the hammer striking the strings.
        rng = np.random.default_rng(note)
        hammer = rng.standard_normal(sample_count).astype(np.float32)
        hammer *= 0.018 * np.exp(-t / 0.0035)
        left += hammer
        right += hammer

        peak = max(np.max(np.abs(left)), np.max(np.abs(right)))
        if peak:
            left /= peak
            right /= peak
        stereo = np.column_stack((left, right))
        return pygame.sndarray.make_sound((stereo * 32767).astype(np.int16))


class SynthwaveSoundStrategy(HarmonicSoundStrategy):
    """Render a wide, detuned saw-like lead for synthwave sounds."""

    def render(self, note, preset, sample_rate, duration):
        frequency = 440.0 * (2.0 ** ((note - 69.0) / 12.0))
        sample_count = int(sample_rate * duration)
        t = np.arange(sample_count, dtype=np.float32) / sample_rate
        left = np.zeros(sample_count, dtype=np.float32)
        right = np.zeros(sample_count, dtype=np.float32)

        for ratio, amplitude in preset.partials:
            left += amplitude * np.sin(2 * np.pi * frequency * 0.996 * ratio * t)
            right += amplitude * np.sin(2 * np.pi * frequency * 1.004 * ratio * t)

        attack = max(preset.attack, 0.001)
        decay = max(preset.decay, 0.001)
        attack_env = np.minimum(t / attack, 1.0)
        decay_env = preset.sustain + (1.0 - preset.sustain) * np.exp(
            -np.maximum(t - attack, 0.0) / decay
        )
        envelope = np.where(t < attack, attack_env, decay_env)
        left *= envelope
        right *= envelope

        peak = max(np.max(np.abs(left)), np.max(np.abs(right)))
        if peak:
            left /= peak
            right /= peak
        stereo = np.column_stack((left, right))
        return pygame.sndarray.make_sound((stereo * 32767).astype(np.int16))


HARMONIC_STRATEGY = HarmonicSoundStrategy()
BELL_STRATEGY = BellSoundStrategy()
SYNTHWAVE_STRATEGY = SynthwaveSoundStrategy()
GRAND_PIANO_STRATEGY = GrandPianoSoundStrategy()

PRESETS = {
    "retro_pluck": SynthPreset(
        "retro_pluck", "Retro Pluck", ((1, 1.0), (2, 0.48), (3, 0.22)),
        0.004, 0.24, 0.015, 180, 4, HARMONIC_STRATEGY,
    ),
    "warm_keys": SynthPreset(
        "warm_keys", "Warm Keys", ((1, 1.0), (2, 0.24), (3, 0.08)),
        0.012, 0.8, 0.24, 280, 0, HARMONIC_STRATEGY, True,
    ),
    "grand_piano": SynthPreset(
        "grand_piano", "Grand Piano",
        ((1, 1.0), (2, 0.58), (3, 0.36), (4, 0.24), (5, 0.16),
         (6, 0.11), (7, 0.075), (8, 0.052)),
        0.004, 2.2, 0.0, 300, 0, GRAND_PIANO_STRATEGY,
    ),
    "glass_bell": SynthPreset(
        "glass_bell", "Glass Bell", ((1, 1.0), (2.71, 0.38), (5.4, 0.14)),
        0.002, 1.7, 0.0, 500, 10, BELL_STRATEGY,
    ),
    "dream_pad": SynthPreset(
        "dream_pad", "Dream Pad", ((1, 1.0), (2, 0.2), (3, 0.07)),
        0.65, 1.0, 0.66, 900, 89, HARMONIC_STRATEGY, True,
    ),
    "heavy_synthwave": SynthPreset(
        "heavy_synthwave", "Heavy Synthwave",
        ((1, 1.0), (2, 0.62), (3, 0.43), (4, 0.31), (5, 0.24),
         (6, 0.19), (7, 0.15), (8, 0.12)),
        0.018, 0.7, 0.72, 550, 81, SYNTHWAVE_STRATEGY, True,
    ),
}


class InternalSynth:
    def __init__(self):
        pygame.mixer.set_num_channels(32)
        self.sounds = {}
        self.channels = {}
        self.preset = PRESETS["retro_pluck"]

    def get_sound(self, note):
        cache_key = (self.preset.key, note)
        if cache_key not in self.sounds:
            duration = 6.0 if self.preset.loop else 4.0
            sample_rate = 44100
            self.sounds[cache_key] = self.preset.strategy.render(
                note, self.preset, sample_rate, duration
            )
        return self.sounds[cache_key]

    def set_preset(self, preset):
        if preset.key == self.preset.key:
            return
        for channel in self.channels.values():
            if channel:
                channel.fadeout(self.preset.release_ms)
        self.channels.clear()
        self.sounds.clear()
        self.preset = preset

    def note_on(self, note, velocity):
        sound = self.get_sound(note)
        sound.set_volume(velocity / 127.0)
        self.channels[note] = sound.play(loops=-1 if self.preset.loop else 0)

    def note_off(self, note, velocity):
        channel = self.channels.pop(note, None)
        if channel:
            channel.fadeout(self.preset.release_ms)

    def close(self):
        pygame.mixer.stop()

class MidiOutputAdapter:
    def __init__(self, device_id):
        self.midi_out = pygame.midi.Output(device_id)
        self.midi_out.set_instrument(0)

    def note_on(self, note, velocity):
        self.midi_out.note_on(note, velocity)

    def note_off(self, note, velocity):
        self.midi_out.note_off(note, velocity)

    def set_preset(self, preset):
        self.midi_out.set_instrument(preset.gm_program)

    def close(self):
        self.midi_out.close()

class AudioManager:
    def __init__(self):
        self.muted = False
        self.output = None
        self.preset = PRESETS["retro_pluck"]
        try:
            pygame.init()
            pygame.midi.init()
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            logging.info("Audio system initialized.")
        except Exception as e:
            logging.warning(f"Audio initialization failed: {e}")

    def get_speakers(self):
        devices = [("Internal Speakers (Synth)", -1)]
        count = pygame.midi.get_count()
        for i in range(count):
            try:
                info = pygame.midi.get_device_info(i)
                if info and info[3] == 1:  # is_output
                    name = info[1].decode('utf-8') if isinstance(info[1], bytes) else info[1]
                    devices.append((name, i))
            except Exception as e:
                logging.warning(f"Error getting device info for {i}: {e}")
        return devices

    def set_device(self, name, device_id):
        if self.output:
            self.output.close()
        
        if device_id == -1:
            self.output = InternalSynth()
            logging.info("Audio output set to Internal Synth")
        else:
            self.output = MidiOutputAdapter(device_id)
            logging.info(f"Audio output set to MIDI device: {name} (ID: {device_id})")

        self.output.set_preset(self.preset)
        
        # Play test note
        self.output.note_on(60, 127)
        time.sleep(0.2)
        self.output.note_off(60, 127)

    def set_preset(self, preset_key):
        try:
            preset = PRESETS[preset_key]
        except KeyError as exc:
            raise ValueError(f"Unknown audio preset: {preset_key}") from exc

        self.preset = preset
        if isinstance(self.output, InternalSynth):
            self.output.set_preset(preset)
        elif isinstance(self.output, MidiOutputAdapter):
            self.output.set_preset(preset)
        logging.info("Audio preset selected: %s", preset.name)

    def close(self):
        """Release audio and MIDI resources during application shutdown."""
        if self.output:
            try:
                self.output.close()
            except Exception:
                logging.exception("Error closing audio output")
            finally:
                self.output = None

        try:
            if pygame.mixer.get_init():
                pygame.mixer.stop()
                pygame.mixer.quit()
        except pygame.error:
            logging.exception("Error shutting down audio mixer")

        try:
            if pygame.midi.get_init():
                pygame.midi.quit()
        except pygame.error:
            logging.exception("Error shutting down MIDI output")

        pygame.quit()
