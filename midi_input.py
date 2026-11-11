"""MIDI input monitoring."""

import logging

import mido
from PyQt5.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot


class MidiWorker(QObject):
    """Read note events from the configured MIDI input device."""

    note_event = pyqtSignal(str, int, int)
    stop_requested = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, input_name="MPK249 Port A"):
        super().__init__()
        self.input_name = input_name
        self.input_port = None
        self.stop_requested.connect(self.stop_monitor)
        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(5)
        self.poll_timer.timeout.connect(self.poll_input)

    @pyqtSlot()
    def start_monitor(self):
        logging.info("Starting input monitor for device %s", self.input_name)
        try:
            self.input_port = mido.open_input(self.input_name)
        except Exception:
            logging.exception("Unable to open MIDI input %s", self.input_name)
            self.finished.emit()
            return
        self.poll_timer.start()

    @pyqtSlot()
    def poll_input(self):
        if self.input_port is None:
            return
        try:
            for message in self.input_port.iter_pending():
                if hasattr(message, "note"):
                    velocity = getattr(message, "velocity", 0)
                    self.note_event.emit(message.type, message.note, velocity)
        except Exception:
            logging.exception("Error reading MIDI input %s", self.input_name)
            self.stop_monitor()

    @pyqtSlot()
    def stop_monitor(self):
        self.poll_timer.stop()
        if self.input_port is not None:
            try:
                self.input_port.close()
            except Exception:
                logging.exception("Error closing MIDI input %s", self.input_name)
            finally:
                self.input_port = None
        self.finished.emit()
