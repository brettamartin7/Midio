#!/usr/bin/env python3
import sys
import signal
import mido
import logging
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import gui
import theory
import audio

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
    def __init__(self, chord_label, notes_label, piano, audio_manager):
        super().__init__()
        self.chord_label = chord_label
        self.notes_label = notes_label
        self.piano = piano
        self.audio_manager = audio_manager
        self.active_notes = []

    @pyqtSlot(str, int, int)
    def on_note_event(self, note_type, note, velocity):
        # Handle Sound
        if self.audio_manager.output:
            if note_type == "note_on" and velocity > 0:
                if not self.audio_manager.muted:
                    self.audio_manager.output.note_on(note, velocity)
            elif note_type == "note_off" or (note_type == "note_on" and velocity == 0):
                self.audio_manager.output.note_off(note, velocity)

        # Normalize note_on with velocity 0 to note_off for GUI logic
        if note_type == "note_on" and velocity == 0:
            note_type = "note_off"

        # Map MIDI note to GUI key index
        gui_note = note - theory.MIDI_OFFSET

        try:
            if note_type == "note_on":
                if gui_note not in self.active_notes:
                    self.active_notes.append(gui_note)
                    self.piano.activate_button(gui_note)
            elif note_type == "note_off":
                if gui_note in self.active_notes:
                    self.active_notes.remove(gui_note)
                    self.piano.deactivate_button(gui_note)
        except Exception as e:
            logging.error("Encountered an error in on_note_event: " + str(e))

        self.update_labels()

    def update_labels(self):
        chord = theory.to_chord(frozenset(self.active_notes))
        if chord == "Invalid chord":
            self.chord_label.setFont(QFont('Arial', 30))
        else:
            self.chord_label.setFont(QFont('Arial', 100, QFont.Bold))
        self.chord_label.setText(chord)
        self.notes_label.setText(''.join(theory.to_note(key) + ' ' for key in set(self.active_notes)))

def open_audio_settings(parent, audio_manager):
    devices = audio_manager.get_devices()
    options = [name for name, _ in devices]
    item, ok = QInputDialog.getItem(parent, "Audio Settings", "Select Output Device:", options, 0, False)
    if ok and item:
        index = options.index(item)
        name, dev_id = devices[index]
        audio_manager.set_device(name, dev_id)

def toggle_mute(win, audio_manager):
    audio_manager.muted = not audio_manager.muted
    win.mute_btn.setText("🔇" if audio_manager.muted else "🔊")

def signal_handler(sig, frame):
    print('Exiting...')
    sys.exit(0)

if __name__ == "__main__":
    format = "%(asctime)s %(filename)s:%(lineno)d - %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Initialize Audio Manager
    audio_manager = audio.AudioManager()
    audio_manager.set_device("Internal Speakers (Synth)", -1)

    # GUI
    app = gui.QApplication(sys.argv)
    win = gui.Window()
    piano = win.piano
    win.btn_audio.clicked.connect(lambda: open_audio_settings(win, audio_manager))
    win.mute_btn.clicked.connect(lambda: toggle_mute(win, audio_manager))
    
    thread = QThread()
    worker = MidiWorker()
    receiver = MidiReceiver(win.chord_label, win.notes_label, piano, audio_manager)
    
    worker.moveToThread(thread)
    worker.note_event.connect(receiver.on_note_event)
    thread.started.connect(worker.run)
    thread.start()

    # Exit
    sys.exit(app.exec_())
    logging.info("Done")
