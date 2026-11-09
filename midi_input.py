"""MIDI input monitoring."""

import logging

import mido
from PyQt5.QtCore import QObject, pyqtSignal


class MidiWorker(QObject):
    """Read note events from the configured MIDI input device."""

    note_event = pyqtSignal(str, int, int)

    def __init__(self, input_name="MPK249 Port A"):
        super().__init__()
        self.input_name = input_name

    def run(self):
        logging.info("Starting input monitor for device %s", self.input_name)
        try:
            with mido.open_input(self.input_name) as input_port:
                for message in input_port:
                    if hasattr(message, "note"):
                        velocity = getattr(message, "velocity", 0)
                        self.note_event.emit(
                            message.type,
                            message.note,
                            velocity,
                        )
        except OSError:
            logging.exception("Unable to open MIDI input %s", self.input_name)
