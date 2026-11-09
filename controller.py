"""Coordinate MIDI note state, audio output, and GUI display updates."""

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

import theory


class NoteController(QObject):
    notes_changed = pyqtSignal(object, str, str)

    def __init__(self, audio_manager):
        super().__init__()
        self.audio_manager = audio_manager
        self.active_notes = set()

    @pyqtSlot(str, int, int)
    def on_note_event(self, note_type, note, velocity):
        is_note_on = note_type == "note_on" and velocity > 0
        is_note_off = note_type == "note_off" or (
            note_type == "note_on" and velocity == 0
        )

        if is_note_on:
            if self.audio_manager.output and not self.audio_manager.muted:
                self.audio_manager.output.note_on(note, velocity)
            self.active_notes.add(note - theory.MIDI_OFFSET)
        elif is_note_off:
            if self.audio_manager.output:
                self.audio_manager.output.note_off(note, velocity)
            self.active_notes.discard(note - theory.MIDI_OFFSET)
        else:
            return

        active_notes = sorted(self.active_notes)
        note_text = " ".join(theory.to_note(key) for key in active_notes)
        chord = theory.to_chord(frozenset(self.active_notes))
        self.notes_changed.emit(active_notes, note_text, chord)
