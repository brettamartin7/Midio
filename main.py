#!/usr/bin/env python3
import sys
import signal
import mido
import threading
import logging
import time
import pygame
import pygame.midi
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import numpy as np
import gui

# Dictionary keeping track of our active notes
global active_notes
active_notes = []
key_offset = 36
audio_output = None

# Dictionary mapping key_number
key_note_dict = {
    0: "C",
    1: "C#/Db",
    2: "D",
    3: "D#/Eb",
    4: "E",
    5: "F",
    6: "F#/Gb",
    7: "G",
    8: "G#/Ab",
    9: "A",
    10: "A#/Bb",
    11: "B",
}

# Dictionary mapping note set to chord
note_chord_dict = {
    # Major
    frozenset({"C", "E", "G"}): "C",
    frozenset({"C#/Db", "E#", "G#/Ab"}): "C# major",
    frozenset({"D", "F#", "A"}): "D major",
    frozenset({"D#/Eb", "G", "A#/Bb"}): "Eb major",
    frozenset({"E", "G#", "B"}): "E major",
    frozenset({"F", "A", "C"}): "F major",
    frozenset({"F#/Gb", "A#/Bb", "C#/Db"}): "F# major",
    frozenset({"G", "B", "D"}): "G major",
    frozenset({"G#/Ab", "C", "D#/Eb"}): "Ab major",
    frozenset({"A", "C#/Db", "E"}): "A major",
    frozenset({"A#/Bb", "D", "F"}): "Bb major",
    frozenset({"B", "D#/Eb", "F#/Gb"}): "B major",
    # Minor
    frozenset({"C", "D#/Eb", "G"}): "C minor",
    frozenset({"C#/Db", "E", "G#/Ab"}): "C# minor",
    frozenset({"D", "F", "A"}): "D minor",
    frozenset({"D#/Eb", "F#/Gb", "Bb"}): "Eb minor",
    frozenset({"E", "G", "B"}): "E minor",
    frozenset({"F", "G#/Ab", "C"}): "F minor",
    frozenset({"F#/Gb", "A", "C#/Db"}): "F# minor",
    frozenset({"G", "A#/Bb", "D"}): "G minor",
    frozenset({"G#/Ab", "B", "D#/Eb"}): "Ab minor",
    frozenset({"A", "C", "E"}): "A minor",
    frozenset({"A#/Bb", "C#/Db", "F"}): "Bb minor",
    frozenset({"B", "D", "F#/Gb"}): "B minor"
}

# Convert a key to a note
def to_note(input_key: int):
    base_value = input_key % 12  # Convert key to base value for the note
    return key_note_dict.get(base_value, "invalid_key: {0}".format(input_key))

# Convert active notes to a chord
def to_chord(active_keys: frozenset):
    base_values = frozenset({to_note(key) for key in active_keys})
    chord = ""
    try:
        chord = note_chord_dict[base_values]
    except KeyError:
        return "Invalid chord"

    return chord

def signal_handler(sig, frame):
    print('Exiting...')
    sys.exit(0)

# Activated by the thread. Appends/removes to active_notes list and then updates the GUI
def update_active_notes(note_type: str, note: int, velocity: int, chord_label: QLabel, notes_label: QLabel, piano: gui.Piano):
    # Handle Sound
    if audio_output:
        midi_note = note + key_offset
        if note_type == "note_on" and velocity > 0:
            audio_output.note_on(midi_note, velocity)
        elif note_type == "note_off" or (note_type == "note_on" and velocity == 0):
            audio_output.note_off(midi_note, velocity)

    # Normalize note_on with velocity 0 to note_off for GUI logic
    if note_type == "note_on" and velocity == 0:
        note_type = "note_off"

    try:
        if note_type == "note_on":
            if note not in active_notes:
                active_notes.append(note)
                piano.activate_button(note)
        elif note_type == "note_off":
            if note in active_notes:
                active_notes.remove(note)
                piano.deactivate_button(note)
    except Exception as e:
        logging.error("Encountered an error in update_active_notes: " + str(e))

    update_labels(chord_label, notes_label)

def update_labels(chord_label: QLabel, notes_label: QLabel):
    chord = to_chord(frozenset(active_notes))
    if chord == "Invalid chord":
        chord_label.setFont(QFont('Arial', 30))
    else:
        chord_label.setFont(QFont('Arial', 100, QFont.Bold))
    chord_label.setText(chord)
    notes_label.setText(''.join(to_note(key) + ' ' for key in set(active_notes)))

class MidiWorker(QObject):
    note_event = pyqtSignal(str, int, int)

    def run(self):
        logging.info("Starting input monitor...")
        try:
            with mido.open_input('MPK249 Port A') as input_port:
                while True:
                    for msg in input_port:
                        try:
                            if hasattr(msg, 'note'):
                                velocity = msg.velocity if hasattr(msg, 'velocity') else 0
                                self.note_event.emit(msg.type, msg.note, velocity)
                        except Exception as e:
                            logging.warning(e)
                            print(msg)
        except OSError as oh_no:
            logging.error(oh_no)

class MidiReceiver(QObject):
    def __init__(self, chord_label, notes_label, piano):
        super().__init__()
        self.chord_label = chord_label
        self.notes_label = notes_label
        self.piano = piano

    @pyqtSlot(str, int, int)
    def on_note_event(self, note_type, note, velocity):
        update_active_notes(note_type, note - key_offset, velocity, self.chord_label, self.notes_label, self.piano)

class InternalSynth:
    def __init__(self):
        # Initialize mixer with CD quality, 16-bit, stereo, buffer 1024
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

def get_audio_devices():
    devices = [("Internal Speakers (Synth)", -1)]
    count = pygame.midi.get_count()
    for i in range(count):
        try:
            info = pygame.midi.get_device_info(i)
            if info and info[3] == 1:  # is_output
                name = info[1]
                if isinstance(name, bytes):
                    name = name.decode('utf-8')
                devices.append((name, i))
        except Exception as e:
            logging.warning(f"Error getting device info for {i}: {e}")
    return devices

def set_audio_output_device(device_name, device_id):
    global audio_output
    try:
        if audio_output:
            audio_output.close()
            audio_output = None
        
        if device_id == -1:
            audio_output = InternalSynth()
            logging.info("Audio output set to Internal Synth")
        else:
            audio_output = MidiOutputAdapter(device_id)
            logging.info(f"Audio output set to MIDI device: {device_name} (ID: {device_id})")
        
        # Play test note
        audio_output.note_on(60, 127)
        time.sleep(0.2)
        audio_output.note_off(60, 127)
    except Exception as e:
        logging.error(f"Failed to set MIDI output: {e}")

def open_audio_settings(parent):
    devices = get_audio_devices()
    options = [name for name, _ in devices]
    item, ok = QInputDialog.getItem(parent, "Audio Settings", "Select Output Device:", options, 0, False)
    if ok and item:
        index = options.index(item)
        name, dev_id = devices[index]
        set_audio_output_device(name, dev_id)

if __name__ == "__main__":
    format = "%(asctime)s %(filename)s:%(lineno)d - %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Initialize Audio
    try:
        pygame.init()
        pygame.midi.init()
        # Initialize mixer for internal synth
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        # List all available MIDI devices to help debug
        logging.info("Available MIDI Devices:")
        for i in range(pygame.midi.get_count()):
            (interf, name, is_input, is_output, opened) = pygame.midi.get_device_info(i)
            direction = []
            if is_input: direction.append("Input")
            if is_output: direction.append("Output")
            logging.info(f"Device {i}: {name.decode('utf-8') if isinstance(name, bytes) else name} - {', '.join(direction)}")

        # Default to Internal Synth
        set_audio_output_device("Internal Speakers (Synth)", -1)

    except Exception as e:
        logging.warning(f"Audio initialization failed: {e}. Ensure 'pygame' is installed.")

    # GUI
    app = gui.QApplication(sys.argv)
    win = gui.Window()
    piano = win.piano
    win.btn_audio.clicked.connect(lambda: open_audio_settings(win))
    
    thread = QThread()
    worker = MidiWorker()
    receiver = MidiReceiver(win.chord_label, win.notes_label, piano)
    
    worker.moveToThread(thread)
    worker.note_event.connect(receiver.on_note_event)
    thread.started.connect(worker.run)
    thread.start()

    # Exit
    sys.exit(app.exec_())
    logging.info("Done")
