# AGENTS.md

## Project overview

Midio is a Python desktop application that monitors MIDI note input, plays notes through an internal synthesizer or MIDI output, and displays active notes and recognized chords in a PyQt GUI. It's primary purpose is to provide a lightweight
environment to play a MIDI keyboard, and teach the user how to play the piano. This is a personal project, not released
to anyone else.

## Repository map

- `main.py` — application startup, device selection dialogs, audio controls, and wiring between components.
- `midi_input.py` — MIDI input worker and note event delivery.
- `controller.py` — active note tracking and coordination of audio playback and display updates.
- `audio.py` — internal synthesized audio, MIDI output, and audio device management.
- `gui.py` — PyQt window, piano keyboard, and note/chord display.
- `theory.py` — MIDI note conversion and chord recognition.
- `scripts/run.sh` — convenience launcher using the repository's `main-env` environment.
- `README.md` — project summary and listed dependencies.

## Environment and running

Activate the existing virtual environment before running Python commands:

```bash
source main-env/bin/activate
```

Run the application from the repository root with:

```bash
python3 main.py
```

The application opens a GUI and may access MIDI and audio devices. Avoid launching it during ordinary code inspection or changes; run it only when needed to test behavior. When testing is finished, exit the application cleanly.

## Validation

There is no documented automated test or lint command in the repository. For changes that can be checked without hardware, prefer focused static checks or direct checks of the affected logic. If a change requires the GUI or MIDI/audio devices, run the application only for that test and close it afterward.

## Change guidance

- Keep documentation and commands consistent with the current repository layout and dependencies.
- Follow the existing separation between application startup, MIDI input, note coordination, audio output, GUI, and music theory logic where practical.
- Do not assume a particular MIDI device is available; device availability depends on the user's setup.
