#!/usr/bin/env python3
import logging
import signal
import sys

import mido
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication, QInputDialog

import audio
import gui
from controller import NoteController
from midi_input import MidiWorker


def open_audio_settings(parent, audio_manager):
    devices = audio_manager.get_speakers()
    options = [name for name, _ in devices]
    item, ok = QInputDialog.getItem(
        parent, "Audio Settings", "Select Output Device:", options, 0, False
    )
    if ok and item:
        index = options.index(item)
        name, device_id = devices[index]
        audio_manager.set_device(name, device_id)


def select_midi_input(parent):
    options = mido.get_input_names()
    item, ok = QInputDialog.getItem(
        parent, "MIDI Input", "Select MIDI Input:", options, 0, False
    )
    if ok and item:
        name = options.index(item)
        logging.info("MIDI Input selected: %s", name)


def toggle_mute(window, audio_manager):
    audio_manager.muted = not audio_manager.muted
    window.set_muted(audio_manager.muted)


def main():
    logging.basicConfig(
        format="%(asctime)s %(filename)s:%(lineno)d - %(message)s",
        level=logging.INFO,
        datefmt="%H:%M:%S",
    )
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)

    app = QApplication(sys.argv)

    audio_manager = audio.AudioManager()
    audio_manager.set_device("Internal Speakers (Synth)", -1)

    window = gui.Window()
    window.set_audio_presets(audio.PRESETS, audio_manager.preset.key)
    window.audio_preset_selected.connect(audio_manager.set_preset)
    controller = NoteController(audio_manager)

    window.btn_audio.clicked.connect(
        lambda: open_audio_settings(window.settings_dialog, audio_manager)
    )
    window.btn_midi.clicked.connect(
        lambda: select_midi_input(window.settings_dialog)
    )
    window.mute_btn.clicked.connect(
        lambda: toggle_mute(window, audio_manager)
    )

    thread = QThread()
    worker = MidiWorker()
    worker.moveToThread(thread)
    worker.note_event.connect(controller.on_note_event)
    controller.notes_changed.connect(window.update_note_display)
    worker.finished.connect(thread.quit)
    thread.started.connect(worker.start_monitor)
    thread.start()

    try:
        return app.exec_()
    finally:
        if thread.isRunning():
            worker.stop_requested.emit()
            if not thread.wait(5000):
                logging.warning("MIDI worker did not stop promptly; waiting for shutdown")
                thread.quit()
                thread.wait()
        audio_manager.close()


if __name__ == "__main__":
    sys.exit(main())
