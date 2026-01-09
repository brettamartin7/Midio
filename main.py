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
import gui

# Dictionary keeping track of our active notes
global active_notes
active_notes = []
key_offset = 36
midi_out = None

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
    if midi_out:
        midi_note = note + key_offset
        if note_type == "note_on" and velocity > 0:
            midi_out.note_on(midi_note, velocity)
        elif note_type == "note_off" or (note_type == "note_on" and velocity == 0):
            midi_out.note_off(midi_note, velocity)

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

def get_midi_output_devices():
    devices = []
    count = pygame.midi.get_count()
    for i in range(count):
        try:
            info = pygame.midi.get_device_info(i)
            if info and info[3] == 1:  # is_output
                name = info[1]
                if isinstance(name, bytes):
                    name = name.decode('utf-8')
                devices.append((i, name))
        except Exception as e:
            logging.warning(f"Error getting device info for {i}: {e}")
    return devices

def set_midi_output_device(device_id):
    global midi_out
    try:
        if midi_out:
            midi_out.close()
            midi_out = None
        
        midi_out = pygame.midi.Output(device_id)
        midi_out.set_instrument(0)
        logging.info(f"Audio output set to device ID: {device_id}")
        
        # Play test note
        midi_out.note_on(60, 127)
        time.sleep(0.2)
        midi_out.note_off(60, 127)
    except Exception as e:
        logging.error(f"Failed to set MIDI output: {e}")

def open_audio_settings(parent):
    devices = get_midi_output_devices()
    options = ["OS Default"] + [f"{name} (ID: {i})" for i, name in devices]
    item, ok = QInputDialog.getItem(parent, "Audio Settings", "Select Output Device:", options, 0, False)
    if ok and item:
        if item == "OS Default":
            port = pygame.midi.get_default_output_id()
            if port != -1:
                set_midi_output_device(port)
            else:
                QMessageBox.warning(parent, "Error", "No default MIDI device found.")
        else:
            index = options.index(item) - 1
            if 0 <= index < len(devices):
                set_midi_output_device(devices[index][0])

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

        # List all available MIDI devices to help debug
        logging.info("Available MIDI Devices:")
        for i in range(pygame.midi.get_count()):
            r = pygame.midi.get_device_info(i)
            (interf, name, is_input, is_output, opened) = r
            direction = []
            if is_input: direction.append("Input")
            if is_output: direction.append("Output")
            logging.info(f"Device {i}: {name.decode('utf-8') if isinstance(name, bytes) else name} - {', '.join(direction)}")

        port = pygame.midi.get_default_output_id()
        if port != -1:
            logging.info(f"Attempting to use default MIDI output device ID: {port}")
            midi_out = pygame.midi.Output(port, 0)
            midi_out.set_instrument(0)
            logging.info("Audio initialized successfully.")
            
            # Play a test note (Middle C) to confirm audio is working
            midi_out.note_on(60, 127)
            time.sleep(0.5)
            midi_out.note_off(60, 127)
        else:
            logging.warning("No default MIDI output found.")
    except Exception as e:
        logging.warning(f"Audio initialization failed: {e}. Ensure 'pygame' is installed.")

    # GUI
    app = gui.QApplication(sys.argv)
    win = gui.Window()
    piano = win.piano
    win.btn_audio.clicked.connect(lambda: open_audio_settings(win))

    # Note Monitor thread
    logging.info("Inputs:")
    logging.info(mido.get_input_names())
    logging.info("Outputs:")
    logging.info(mido.get_output_names())
    
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
