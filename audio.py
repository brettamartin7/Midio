import pygame
import pygame.midi
import numpy as np
import logging
import time

class InternalSynth:
    def __init__(self):
        # Initialize mixer with CD quality, 16-bit, stereo, buffer 512
        # We ensure mixer is initialized in AudioManager, but we can set channels here
        pygame.mixer.set_num_channels(32)
        self.sounds = {}
        self.channels = {}

    def get_sound(self, note):
        if note not in self.sounds:
            # Generate a simple sine wave with decay (Pluck/Piano-ish)
            freq = 440.0 * (2.0 ** ((note - 69.0) / 12.0))
            duration = 2.0
            sample_rate = 44100
            n_samples = int(sample_rate * duration)
            t = np.linspace(0, duration, n_samples, False)
            
            # Synthesis: Fundamental + Harmonics with exponential decay
            wave = np.sin(2 * np.pi * freq * t) * np.exp(-3 * t)
            wave += 0.5 * np.sin(2 * np.pi * freq * 2 * t) * np.exp(-4 * t)
            wave += 0.25 * np.sin(2 * np.pi * freq * 3 * t) * np.exp(-5 * t)
            
            # Normalize and convert to 16-bit int
            wave = (wave * 32767 / np.max(np.abs(wave))).astype(np.int16)
            stereo = np.column_stack((wave, wave))
            
            self.sounds[note] = pygame.sndarray.make_sound(stereo)
        return self.sounds[note]

    def note_on(self, note, velocity):
        sound = self.get_sound(note)
        sound.set_volume(velocity / 127.0)
        # Play and store channel to control later
        self.channels[note] = sound.play()

    def note_off(self, note, velocity):
        if note in self.channels and self.channels[note]:
            self.channels[note].fadeout(300)

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

    def close(self):
        self.midi_out.close()

class AudioManager:
    def __init__(self):
        self.muted = False
        self.output = None
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
        
        # Play test note
        self.output.note_on(60, 127)
        time.sleep(0.2)
        self.output.note_off(60, 127)

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
