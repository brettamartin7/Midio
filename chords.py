"""Chord definitions used by the library and its keyboard voicings."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ChordDefinition:
    key: str
    root: str
    root_pitch_class: int
    quality: str
    intervals: tuple
    note_names: tuple

    @property
    def name(self):
        return f"{self.root} {self.quality.title()}"

    @property
    def pitch_classes(self):
        return frozenset(
            (self.root_pitch_class + interval) % 12
            for interval in self.intervals
        )

    def voicing_indices(self, key_count):
        """Choose a close-position voicing that fits the visible keyboard."""
        intervals = tuple(self.intervals)
        rotations = tuple(
            intervals[index:] + tuple(value + 12 for value in intervals[:index])
            for index in range(len(intervals))
        )
        center = (key_count - 1) / 2

        for rotation in rotations:
            first_pitch_class = (self.root_pitch_class + rotation[0]) % 12
            offsets = tuple(value - rotation[0] for value in rotation)
            candidates = []
            for first_note in range(key_count):
                if first_note % 12 != first_pitch_class:
                    continue
                voicing = tuple(first_note + offset for offset in offsets)
                if max(voicing) < key_count:
                    candidates.append(voicing)
            if candidates:
                return min(
                    candidates,
                    key=lambda voicing: abs(sum(voicing) / len(voicing) - center),
                )

        return ()


MAJOR_CHORDS = (
    ChordDefinition("c", "C", 0, "major", (0, 4, 7), ("C", "E", "G")),
    ChordDefinition("db", "Db", 1, "major", (0, 4, 7), ("Db", "F", "Ab")),
    ChordDefinition("d", "D", 2, "major", (0, 4, 7), ("D", "F#", "A")),
    ChordDefinition("eb", "Eb", 3, "major", (0, 4, 7), ("Eb", "G", "Bb")),
    ChordDefinition("e", "E", 4, "major", (0, 4, 7), ("E", "G#", "B")),
    ChordDefinition("f", "F", 5, "major", (0, 4, 7), ("F", "A", "C")),
    ChordDefinition("fsharp", "F#", 6, "major", (0, 4, 7), ("F#", "A#", "C#")),
    ChordDefinition("g", "G", 7, "major", (0, 4, 7), ("G", "B", "D")),
    ChordDefinition("ab", "Ab", 8, "major", (0, 4, 7), ("Ab", "C", "Eb")),
    ChordDefinition("a", "A", 9, "major", (0, 4, 7), ("A", "C#", "E")),
    ChordDefinition("bb", "Bb", 10, "major", (0, 4, 7), ("Bb", "D", "F")),
    ChordDefinition("b", "B", 11, "major", (0, 4, 7), ("B", "D#", "F#")),
)
