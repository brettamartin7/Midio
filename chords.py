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
    def short_name(self):
        return self.root + ("m" if self.quality == "minor" else "")

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

MINOR_CHORDS = (
    ChordDefinition("c_minor", "C", 0, "minor", (0, 3, 7), ("C", "Eb", "G")),
    ChordDefinition("csharp_minor", "C#", 1, "minor", (0, 3, 7), ("C#", "E", "G#")),
    ChordDefinition("d_minor", "D", 2, "minor", (0, 3, 7), ("D", "F", "A")),
    ChordDefinition("eb_minor", "Eb", 3, "minor", (0, 3, 7), ("Eb", "Gb", "Bb")),
    ChordDefinition("e_minor", "E", 4, "minor", (0, 3, 7), ("E", "G", "B")),
    ChordDefinition("f_minor", "F", 5, "minor", (0, 3, 7), ("F", "Ab", "C")),
    ChordDefinition("fsharp_minor", "F#", 6, "minor", (0, 3, 7), ("F#", "A", "C#")),
    ChordDefinition("g_minor", "G", 7, "minor", (0, 3, 7), ("G", "Bb", "D")),
    ChordDefinition("gsharp_minor", "G#", 8, "minor", (0, 3, 7), ("G#", "B", "D#")),
    ChordDefinition("a_minor", "A", 9, "minor", (0, 3, 7), ("A", "C", "E")),
    ChordDefinition("bb_minor", "Bb", 10, "minor", (0, 3, 7), ("Bb", "Db", "F")),
    ChordDefinition("b_minor", "B", 11, "minor", (0, 3, 7), ("B", "D", "F#")),
)


@dataclass(frozen=True)
class ProgressionStep:
    degree: int
    quality: str
    numeral: str


@dataclass(frozen=True)
class ProgressionDefinition:
    key: str
    name: str
    steps: tuple


PROGRESSIONS = (
    ProgressionDefinition(
        "one_four_five_one",
        "I – IV – V – I",
        (
            ProgressionStep(1, "major", "I"),
            ProgressionStep(4, "major", "IV"),
            ProgressionStep(5, "major", "V"),
            ProgressionStep(1, "major", "I"),
        ),
    ),
    ProgressionDefinition(
        "one_five_six_four",
        "I – V – vi – IV",
        (
            ProgressionStep(1, "major", "I"),
            ProgressionStep(5, "major", "V"),
            ProgressionStep(6, "minor", "vi"),
            ProgressionStep(4, "major", "IV"),
        ),
    ),
    ProgressionDefinition(
        "six_four_one_five",
        "vi – IV – I – V",
        (
            ProgressionStep(6, "minor", "vi"),
            ProgressionStep(4, "major", "IV"),
            ProgressionStep(1, "major", "I"),
            ProgressionStep(5, "major", "V"),
        ),
    ),
)


CHORDS_BY_QUALITY_AND_ROOT = {
    (chord.root_pitch_class, chord.quality): chord
    for chord in MAJOR_CHORDS + MINOR_CHORDS
}
MAJOR_SCALE_INTERVALS = (0, 2, 4, 5, 7, 9, 11)


def resolve_progression(progression, tonic):
    """Resolve Roman numeral steps into chord definitions for a major tonic."""
    chords = []
    for step in progression.steps:
        root = (tonic.root_pitch_class + MAJOR_SCALE_INTERVALS[step.degree - 1]) % 12
        chord = CHORDS_BY_QUALITY_AND_ROOT.get((root, step.quality))
        if chord is None:
            return ()
        chords.append(chord)
    return tuple(chords)
