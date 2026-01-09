MIDI_OFFSET = 36

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
    try:
        return note_chord_dict[base_values]
    except KeyError:
        return "Invalid chord"