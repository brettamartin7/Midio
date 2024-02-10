#!/usr/bin/env python3
import sys
import signal
import mido
import threading
import logging
import time
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import gui

# Dictionary keeping track of our active notes
global active_notes
active_notes = []
key_offset = 36
active_note_mutex = threading.Lock()

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
def update_active_notes(note_type: str, note: int, chord_label: QLabel, notes_label: QLabel, piano: gui.Piano):
    active_note_mutex.acquire()
    try:
        if note_type == "note_on":
            if note not in active_notes:
                active_notes.append(note)
                piano.activate_button(to_note(note))
        elif note_type == "note_off":
            if note in active_notes:
                active_notes.remove(note)
                piano.deactivate_button(to_note(note))

    finally:
        logging.info("active_notes: ")
        logging.info(active_notes)
        update_labels(chord_label, notes_label)
        active_note_mutex.release()

def update_labels(chord_label: QLabel, notes_label: QLabel):
    chord = to_chord(frozenset(active_notes))
    if chord == "Invalid chord":
        chord_label.setFont(QFont('Times', 30))
    else:
        chord_label.setFont(QFont('Times', 100))
    chord_label.setText(chord)
    notes_label.setText(''.join(to_note(key) + ' ' for key in set(active_notes)))

# Thread function, the for loop triggers when a note is pressed.
def input_monitor(chord_label: QLabel, notes_label: QLabel, piano: gui.Piano):
    logging.info("Starting input monitor...")
    try:
        with mido.open_input('MPK249 0') as input_port:
            while True:
                for msg in input_port:
                    try:
                        update_active_notes(msg.type, msg.note - key_offset, chord_label, notes_label, piano)  # Makes the first key 0
                    except Exception as e:
                        logging.warning(e)
                        print(msg)
    except OSError as oh_no:
        logging.error(oh_no)
        return

if __name__ == "__main__":
    format = "%(asctime)s %(filename)s:%(lineno)d - %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # GUI
    app = gui.QApplication(sys.argv)
    win = gui.Window()
    piano = gui.Piano(win)

    # Note Monitor thread
    logging.info("Inputs:")
    logging.info(mido.get_input_names())
    logging.info("Outputs:")
    logging.info(mido.get_output_names())
    monitor_thread = threading.Thread(target=input_monitor, daemon=True, args=(win.chord_label, win.notes_label, piano,))
    monitor_thread.start()

    # Exit
    sys.exit(app.exec_())
    logging.info("Done")
