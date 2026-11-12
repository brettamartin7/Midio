#!/usr/bin/env python3
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import logging

from chords import MAJOR_CHORDS, PROGRESSIONS, resolve_progression


APP_STYLE = """
QWidget#Window { background-color: #090b1d; color: #f3f1ff; }
QWidget#Content { background-color: transparent; }
QLabel { background: transparent; }
QPushButton { font-family: 'Arial'; }
QInputDialog, QMessageBox { background-color: #11132d; color: #f3f1ff; }
QLineEdit, QListView, QComboBox, QSpinBox {
    background-color: #171936; color: #f3f1ff; border: 1px solid #484274;
    border-radius: 7px; padding: 7px;
}
QMenu { background-color:#11132d; color:#e9e5ff; border:1px solid #484274; padding:5px; }
QMenu::item { padding:8px 24px 8px 10px; border-radius:5px; }
QMenu::item:selected { background-color:#29234c; color:#ffffff; }
QMenu::item:checked { color:#80f6ff; }
QDialog { background-color:#10122b; color:#f3f1ff; }
"""

BLACK_KEY_STYLE = """
QPushButton#black_key {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #393451, stop:1 #17152a);
    border: 1px solid #625982; border-top: 2px solid #8d7ba7;
    border-bottom-left-radius: 6px; border-bottom-right-radius: 6px;
}
QPushButton#black_key:disabled {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff71d2, stop:1 #a32dca);
    border: 1px solid #ffb5eb;
}
"""

WHITE_KEY_STYLE = """
QPushButton#white_key {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #fffaff, stop:1 #c9c5dc);
    border: 1px solid #918ba8; border-bottom: 5px solid #8b86a3;
    border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;
}
QPushButton#white_key:disabled {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #80f6ff, stop:1 #38acd5);
    border: 1px solid #d4ffff; border-bottom: 5px solid #2785b8;
}
"""

WHITE_KEY_LABEL_STYLE = """
QLabel {
    color: rgba(61, 53, 96, 155);
    background: transparent;
    border: none;
    font-family: Arial;
    font-size: 10px;
    font-weight: bold;
}
"""

WHITE_KEY_SUGGESTED_STYLE = """
QPushButton#white_key {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffe4fb, stop:1 #d779dc);
    border: 1px solid #ff9be7; border-bottom: 5px solid #ad54ba;
    border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;
}
"""

BLACK_KEY_SUGGESTED_STYLE = """
QPushButton#black_key {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #cb55d7, stop:1 #78248e);
    border: 1px solid #ff9be7; border-top: 2px solid #ffc2f0;
    border-bottom-left-radius: 6px; border-bottom-right-radius: 6px;
}
"""


class Piano(QWidget):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.setObjectName("PianoWidget")
        self.keys = {}
        self.note_labels = {}
        self.active_notes = set()
        self.target_notes = set()
        self.draw_keys(4)
        main_window.layout.addWidget(self, 0, Qt.AlignHCenter)

    def draw_keys(self, num_octaves):
        for key in self.keys.values():
            key.deleteLater()
        self.keys = {}
        self.note_labels = {}

        white_key_x = 20
        num_keys = num_octaves * 12
        black_notes = [1, 3, 6, 8, 10]
        white_note_names = {0: "C", 2: "D", 4: "E", 5: "F", 7: "G", 9: "A", 11: "B"}

        for i in range(num_keys):
            if (i % 12) in black_notes:
                btn = QPushButton(self)
                btn.setGeometry(QRect(white_key_x - 20, 35, 31, 111))
                btn.setStyleSheet(BLACK_KEY_STYLE)
                btn.setObjectName("black_key")
            else:
                btn = QPushButton(self)
                btn.setGeometry(QRect(white_key_x, 35, 41, 181))
                btn.setStyleSheet(WHITE_KEY_STYLE)
                btn.setObjectName("white_key")
                note_label = QLabel(white_note_names[i % 12], btn)
                note_label.setAlignment(Qt.AlignCenter)
                note_label.setGeometry(0, 148, 41, 22)
                note_label.setStyleSheet(WHITE_KEY_LABEL_STYLE)
                note_label.setAttribute(Qt.WA_TransparentForMouseEvents)
                note_label.show()
                self.note_labels[i] = note_label
                white_key_x += 40
            btn.setCursor(Qt.PointingHandCursor)
            self.keys[i] = btn
            btn.show()

        for i in range(num_keys):
            if (i % 12) in black_notes:
                self.keys[i].raise_()

        self.setFixedSize(white_key_x + 20, 245)
        self._refresh_keys()

    def set_active_notes(self, notes):
        self.active_notes = set(notes)
        self._refresh_keys()

    def set_target_notes(self, notes):
        self.target_notes = set(notes)
        self._refresh_keys()

    def _refresh_keys(self):
        for note, key in self.keys.items():
            is_black = note % 12 in (1, 3, 6, 8, 10)
            if note in self.active_notes:
                style = BLACK_KEY_STYLE if is_black else WHITE_KEY_STYLE
                key.setStyleSheet(style)
                key.setDisabled(True)
            else:
                key.setDisabled(False)
                if note in self.target_notes:
                    style = BLACK_KEY_SUGGESTED_STYLE if is_black else WHITE_KEY_SUGGESTED_STYLE
                else:
                    style = BLACK_KEY_STYLE if is_black else WHITE_KEY_STYLE
                key.setStyleSheet(style)

            label = self.note_labels.get(note)
            if label:
                label.setStyleSheet(
                    "QLabel{color:rgba(255,245,255,220);background:transparent;border:none;font-family:Arial;font-size:10px;font-weight:bold;}"
                    if note in self.target_notes or note in self.active_notes
                    else WHITE_KEY_LABEL_STYLE
                )

    def activate_button(self, note):
        self.active_notes.add(note)
        self._refresh_keys()

    def deactivate_button(self, note):
        self.active_notes.discard(note)
        self._refresh_keys()


class Window(QWidget):
    audio_preset_selected = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.setObjectName("Window")
        self.setStyleSheet(APP_STYLE)
        self.selected_chord = None
        self.progression_tonic = None
        self.selected_progression = None
        self.progression_chords = ()
        self.progression_step = 0
        self.progression_status_override = ""
        self.library_mode = "chords"
        self.current_active_notes = set()
        self.current_note_text = ""
        self.current_chord = "Invalid chord"

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.settings_dialog = QDialog(self)
        self.settings_dialog.setWindowTitle("Studio Settings")
        self.settings_dialog.setFixedWidth(340)
        settings_layout = QVBoxLayout(self.settings_dialog)
        settings_layout.setContentsMargins(24, 22, 24, 20)
        settings_layout.setSpacing(12)
        settings_title = QLabel("DEVICE ROUTING")
        settings_title.setStyleSheet("color:#ff75d8;font-size:10px;font-weight:bold;letter-spacing:2px;")
        settings_layout.addWidget(settings_title)
        self.btn_midi = QPushButton("MIDI Input Device")
        self.btn_audio = QPushButton("Audio Output Device")
        device_button_style = "QPushButton{color:#e9e5ff;background:#191a39;text-align:left;padding:12px;border:1px solid #37315e;border-radius:8px;} QPushButton:hover{background:#242047;border-color:#8172be;}"
        for button in (self.btn_midi, self.btn_audio):
            button.setStyleSheet(device_button_style)
            settings_layout.addWidget(button)
        settings_layout.addStretch()
        done_button = QPushButton("Done")
        done_button.setStyleSheet("QPushButton{color:#11132d;background:#80f6ff;padding:9px 18px;border:0;border-radius:8px;font-weight:bold;} QPushButton:hover{background:#a5fbff;}")
        done_button.clicked.connect(self.settings_dialog.accept)
        settings_layout.addWidget(done_button, 0, Qt.AlignRight)

        self.content_widget = QWidget(self)
        self.content_widget.setObjectName("Content")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(38, 25, 38, 28)
        self.content_layout.setSpacing(20)

        self.header_layout = QHBoxLayout()
        self.header_layout.setSpacing(12)

        brand = QVBoxLayout()
        brand.setSpacing(1)
        title = QLabel("MIDIO")
        title.setFont(QFont("Arial", 17, QFont.Bold))
        title.setStyleSheet("color:#faf7ff; letter-spacing:4px;")
        subtitle = QLabel("SYNTH SESSION  /  LIVE INPUT")
        subtitle.setStyleSheet("color:#817ba7;font-size:9px;font-weight:bold;letter-spacing:2px;")
        brand.addWidget(title)
        brand.addWidget(subtitle)
        self.header_layout.addLayout(brand)
        self.header_layout.addStretch()

        octave_label = QLabel("OCTAVES")
        octave_label.setStyleSheet("color:#817ba7;font-size:9px;font-weight:bold;letter-spacing:1px;")
        self.header_layout.addWidget(octave_label)
        self.octave_selector = QComboBox()
        self.octave_selector.addItems([str(octaves) for octaves in range(1, 7)])
        self.octave_selector.setCurrentText("4")
        self.octave_selector.setFixedWidth(62)
        self.octave_selector.setToolTip("Number of piano octaves shown")
        self.header_layout.addWidget(self.octave_selector)

        self.btn_presets = QToolButton()
        self.btn_presets.setText("Audio Presets")
        self.btn_presets.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.btn_presets.setArrowType(Qt.DownArrow)
        self.btn_presets.setPopupMode(QToolButton.InstantPopup)
        self.btn_presets.setMinimumWidth(195)
        self.btn_presets.setCursor(Qt.PointingHandCursor)
        self.btn_presets.setStyleSheet("QToolButton{color:#e9e5ff;background:#15152f;text-align:left;padding:10px 12px;font-size:12px;border:1px solid #37315e;border-radius:10px;} QToolButton:hover{color:#fff;border-color:#8172be;background:#1b1a3b;} QToolButton::menu-indicator{image:none;}")
        self.preset_menu = QMenu(self.btn_presets)
        self.btn_presets.setMenu(self.preset_menu)
        self.header_layout.addWidget(self.btn_presets)

        self.mute_btn = QPushButton()
        self.mute_btn.setFixedSize(44, 42)
        self.mute_btn.setCursor(Qt.PointingHandCursor)
        self.mute_btn.setIconSize(QSize(22, 22))
        self.mute_btn.setStyleSheet("QPushButton{color:#d8d2f2;font-size:19px;background:#15152f;border:1px solid #37315e;border-radius:12px;} QPushButton:hover{color:#80f6ff;border-color:#80f6ff;}")
        self.set_muted(False)
        self.header_layout.addWidget(self.mute_btn)

        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(44, 42)
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.setToolTip("MIDI and audio device settings")
        self.settings_btn.setStyleSheet("QPushButton{color:#b8a8ff;font-size:20px;background:#15152f;border:1px solid #37315e;border-radius:12px;} QPushButton:hover{color:#ff75d8;border-color:#ff75d8;}")
        self.settings_btn.clicked.connect(self.open_settings)
        self.header_layout.addWidget(self.settings_btn)
        self.content_layout.addLayout(self.header_layout)

        self.display_frame = QFrame(self.content_widget)
        self.display_frame.setObjectName("DisplayFrame")
        self.display_frame.setStyleSheet("QFrame#DisplayFrame{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #171632,stop:0.55 #11142d,stop:1 #1b1234);border:1px solid #39315f;border-radius:20px;}")
        self.display_frame.setMinimumHeight(300)
        self.display_layout = QVBoxLayout(self.display_frame)
        self.display_layout.setContentsMargins(28, 25, 28, 25)
        self.display_layout.setSpacing(7)

        self.display_kicker = QLabel("NOW PLAYING")
        self.display_kicker.setAlignment(Qt.AlignCenter)
        self.display_kicker.setStyleSheet("color:#ff75d8;font-size:10px;font-weight:bold;letter-spacing:3px;border:none;")
        self.display_layout.addWidget(self.display_kicker)

        self.chord_label = QLabel("Ready")
        self.chord_label.setFont(QFont("Arial", 72, QFont.Bold))
        self.chord_label.setAlignment(Qt.AlignCenter)
        self.chord_label.setStyleSheet("color:#f4eaff;border:none;")

        self.notes_label = QLabel("PLAY A CHORD TO BEGIN")
        self.notes_label.setFont(QFont("Arial", 15))
        self.notes_label.setAlignment(Qt.AlignCenter)
        self.notes_label.setStyleSheet("color:#9b91c5;border:none;letter-spacing:2px;")
        self.live_chord_label = QLabel("")
        self.live_chord_label.setAlignment(Qt.AlignCenter)
        self.live_chord_label.setStyleSheet("color:#80f6ff;border:none;font-size:10px;font-weight:bold;letter-spacing:2px;")
        self.display_layout.addStretch(1)
        self.display_layout.addWidget(self.chord_label)
        self.display_layout.addWidget(self.notes_label)
        self.display_layout.addWidget(self.live_chord_label)
        self.display_layout.addStretch(1)

        activity_layout = QHBoxLayout()
        activity_layout.setSpacing(16)
        activity_layout.addWidget(self.display_frame, 1)

        self.chord_library_frame = QFrame(self.content_widget)
        self.chord_library_frame.setObjectName("ChordLibrary")
        self.chord_library_frame.setFixedWidth(258)
        self.chord_library_frame.setMinimumHeight(300)
        self.chord_library_frame.setStyleSheet("QFrame#ChordLibrary{background:#11132d;border:1px solid #39315f;border-radius:18px;}")
        library_layout = QVBoxLayout(self.chord_library_frame)
        library_layout.setContentsMargins(16, 16, 16, 16)
        library_layout.setSpacing(9)

        library_header = QHBoxLayout()
        library_title = QLabel("CHORD LIBRARY")
        library_title.setStyleSheet("color:#ff75d8;font-size:10px;font-weight:bold;letter-spacing:2px;border:none;")
        self.clear_chord_button = QToolButton()
        self.clear_chord_button.setText("CLEAR")
        self.clear_chord_button.setCursor(Qt.PointingHandCursor)
        self.clear_chord_button.setStyleSheet("QToolButton{color:#817ba7;background:transparent;border:none;font-size:9px;font-weight:bold;letter-spacing:1px;} QToolButton:hover{color:#80f6ff;}")
        self.clear_chord_button.clicked.connect(self.clear_chord_selection)
        library_header.addWidget(library_title)
        library_header.addStretch()
        library_header.addWidget(self.clear_chord_button)
        library_layout.addLayout(library_header)

        tabs_layout = QHBoxLayout()
        tabs_layout.setSpacing(6)
        tab_style = "QPushButton{color:#817ba7;background:#191a39;border:1px solid #37315e;border-radius:7px;padding:7px 4px;font-size:9px;font-weight:bold;letter-spacing:1px;} QPushButton:checked{color:#fff;background:#29234c;border-color:#8172be;} QPushButton:hover{color:#fff;}"
        self.chords_tab = QPushButton("CHORDS")
        self.progressions_tab = QPushButton("PROGRESSIONS")
        for tab in (self.chords_tab, self.progressions_tab):
            tab.setCheckable(True)
            tab.setCursor(Qt.PointingHandCursor)
            tab.setStyleSheet(tab_style)
            tabs_layout.addWidget(tab)
        self.chords_tab.setChecked(True)
        self.chords_tab.clicked.connect(lambda: self.set_library_mode("chords"))
        self.progressions_tab.clicked.connect(self.toggle_progressions_view)
        library_layout.addLayout(tabs_layout)

        self.library_stack = QStackedWidget()
        self.chords_page = QWidget()
        chords_page_layout = QVBoxLayout(self.chords_page)
        chords_page_layout.setContentsMargins(0, 0, 0, 0)
        chords_page_layout.setSpacing(8)
        library_subtitle = QLabel("MAJOR TRIADS")
        library_subtitle.setStyleSheet("color:#625d83;font-size:9px;font-weight:bold;letter-spacing:2px;border:none;")
        chords_page_layout.addWidget(library_subtitle)

        chord_grid = QGridLayout()
        chord_grid.setContentsMargins(0, 0, 0, 0)
        chord_grid.setHorizontalSpacing(7)
        chord_grid.setVerticalSpacing(7)
        chord_button_style = "QPushButton{color:#c9c2e5;background:#191a39;border:1px solid #37315e;border-radius:8px;font-size:12px;font-weight:bold;padding:8px 2px;} QPushButton:hover{color:#fff;background:#262047;border-color:#8172be;} QPushButton:checked{color:#fff;background:#55275f;border:1px solid #ff75d8;}"
        self.chord_button_group = QButtonGroup(self)
        self.chord_button_group.setExclusive(True)
        self.chord_buttons = {}
        for index, chord_definition in enumerate(MAJOR_CHORDS):
            button = QPushButton(chord_definition.root)
            button.setCheckable(True)
            button.setCursor(Qt.PointingHandCursor)
            button.setToolTip(chord_definition.name)
            button.setAccessibleName(chord_definition.name)
            button.setStyleSheet(chord_button_style)
            self.chord_button_group.addButton(button)
            self.chord_buttons[chord_definition.key] = button
            button.clicked.connect(
                lambda checked=False, chord=chord_definition: self.select_chord(chord)
            )
            chord_grid.addWidget(button, index // 3, index % 3)
        chords_page_layout.addLayout(chord_grid)
        chords_page_layout.addStretch()
        self.library_stack.addWidget(self.chords_page)

        self.progressions_page = QWidget()
        progression_page_layout = QVBoxLayout(self.progressions_page)
        progression_page_layout.setContentsMargins(0, 0, 0, 0)
        progression_page_layout.setSpacing(7)
        key_row = QHBoxLayout()
        self.progression_key_label = QLabel("KEY · SELECT A CHORD")
        self.progression_key_label.setStyleSheet("color:#817ba7;font-size:9px;font-weight:bold;letter-spacing:1px;border:none;")
        self.change_key_button = QToolButton()
        self.change_key_button.setText("CHANGE")
        self.change_key_button.setCursor(Qt.PointingHandCursor)
        self.change_key_button.setStyleSheet("QToolButton{color:#80f6ff;background:transparent;border:none;font-size:9px;font-weight:bold;}")
        self.change_key_button.clicked.connect(lambda: self.set_library_mode("chords"))
        key_row.addWidget(self.progression_key_label)
        key_row.addStretch()
        key_row.addWidget(self.change_key_button)
        progression_page_layout.addLayout(key_row)

        self.progression_button_group = QButtonGroup(self)
        self.progression_button_group.setExclusive(True)
        self.progression_buttons = {}
        progression_button_style = "QPushButton{color:#c9c2e5;background:#191a39;text-align:left;border:1px solid #37315e;border-radius:7px;padding:8px;font-size:10px;font-weight:bold;} QPushButton:hover{color:#fff;background:#262047;border-color:#8172be;} QPushButton:checked{color:#fff;background:#55275f;border-color:#ff75d8;} QPushButton:disabled{color:#514d70;background:#14152d;border-color:#292644;}"
        for progression in PROGRESSIONS:
            button = QPushButton(progression.name)
            button.setCheckable(True)
            button.setCursor(Qt.PointingHandCursor)
            button.setStyleSheet(progression_button_style)
            button.setEnabled(False)
            button.clicked.connect(
                lambda checked=False, item=progression: self.select_progression(item)
            )
            self.progression_button_group.addButton(button)
            self.progression_buttons[progression.key] = button
            progression_page_layout.addWidget(button)

        self.progression_steps_layout = QHBoxLayout()
        self.progression_steps_layout.setSpacing(4)
        progression_page_layout.addLayout(self.progression_steps_layout)
        step_controls = QHBoxLayout()
        self.previous_step_button = QPushButton("‹ Previous")
        self.next_step_button = QPushButton("Next ›")
        step_button_style = "QPushButton{color:#c9c2e5;background:#191a39;border:1px solid #37315e;border-radius:7px;padding:6px;font-size:9px;font-weight:bold;} QPushButton:hover{color:#fff;border-color:#8172be;} QPushButton:disabled{color:#514d70;background:#14152d;border-color:#292644;}"
        self.previous_step_button.setStyleSheet(step_button_style)
        self.next_step_button.setStyleSheet(step_button_style)
        self.previous_step_button.clicked.connect(lambda: self.set_progression_step(self.progression_step - 1))
        self.next_step_button.clicked.connect(lambda: self.set_progression_step(self.progression_step + 1))
        step_controls.addWidget(self.previous_step_button)
        step_controls.addWidget(self.next_step_button)
        progression_page_layout.addLayout(step_controls)
        progression_page_layout.addStretch()
        self.library_stack.addWidget(self.progressions_page)
        library_layout.addWidget(self.library_stack, 1)

        activity_layout.addWidget(self.chord_library_frame)
        self.content_layout.addLayout(activity_layout, 1)

        self.main_layout.addWidget(self.content_widget)
        self.layout = self.content_layout
        self.piano = Piano(self)
        self.octave_selector.currentTextChanged.connect(self.select_octaves)
        self._update_progression_ui()

        self.resize(1250, 700)
        self.setMinimumSize(760, 560)
        self.show()

    def setNote(self, input_note):
        self.chord_label.setText(input_note)

    def set_audio_presets(self, presets, selected_key):
        self.preset_menu.clear()
        self.preset_actions = QActionGroup(self)
        self.preset_actions.setExclusive(True)
        selected_name = None

        for key, preset in presets.items():
            action = QAction(preset.name, self.preset_menu)
            action.setCheckable(True)
            action.setChecked(key == selected_key)
            self.preset_actions.addAction(action)
            self.preset_menu.addAction(action)
            action.triggered.connect(
                lambda checked=False, preset_key=key, name=preset.name:
                    self._choose_audio_preset(preset_key, name)
            )
            if key == selected_key:
                selected_name = preset.name

        if selected_name:
            self.btn_presets.setText(f"{selected_name}")

    def _choose_audio_preset(self, preset_key, preset_name):
        self.btn_presets.setText(preset_name)
        self.audio_preset_selected.emit(preset_key)

    def set_muted(self, muted):
        self.mute_btn.setText("")
        self.mute_btn.setIcon(self._audio_icon(muted))
        label = "Unmute audio" if muted else "Mute audio"
        self.mute_btn.setToolTip(label)
        self.mute_btn.setAccessibleName(label)

    @staticmethod
    def _audio_icon(muted):
        pixmap = QPixmap(48, 48)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        color = QColor("#ff75d8" if muted else "#c8bcff")
        pen = QPen(color, 3.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)

        speaker = QPainterPath()
        speaker.moveTo(8, 19)
        speaker.lineTo(14, 19)
        speaker.lineTo(23, 12)
        speaker.lineTo(23, 36)
        speaker.lineTo(14, 29)
        speaker.lineTo(8, 29)
        speaker.closeSubpath()
        painter.fillPath(speaker, color)
        painter.setBrush(Qt.NoBrush)

        if muted:
            painter.drawLine(29, 19, 39, 29)
            painter.drawLine(39, 19, 29, 29)
        else:
            wave = QPainterPath()
            wave.moveTo(28, 18)
            wave.cubicTo(33, 21, 33, 27, 28, 30)
            painter.drawPath(wave)
            wave = QPainterPath()
            wave.moveTo(32, 13)
            wave.cubicTo(41, 19, 41, 29, 32, 35)
            painter.drawPath(wave)

        painter.end()
        return QIcon(pixmap)

    def update_note_display(self, active_notes, note_text, chord):
        self.current_active_notes = set(active_notes)
        self.current_note_text = note_text
        self.current_chord = chord

        if (
            self.library_mode == "progressions"
            and self.progression_chords
            and self.progression_step < len(self.progression_chords)
        ):
            target = self.progression_chords[self.progression_step]
            active_pitch_classes = {note % 12 for note in self.current_active_notes}
            if active_pitch_classes == target.pitch_classes:
                if self.progression_step + 1 < len(self.progression_chords):
                    self.progression_step += 1
                    next_chord = self.progression_chords[self.progression_step]
                    self.progression_status_override = (
                        f"CHORD MATCH  ·  NEXT {next_chord.short_name}"
                    )
                    self._render_progression_steps()
                else:
                    self.progression_status_override = "PROGRESSION COMPLETE"
            else:
                self.progression_status_override = ""

        self._refresh_chord_display()

    def select_chord(self, chord_definition):
        old_tonic = self.progression_tonic
        self.progression_tonic = chord_definition
        self.progression_status_override = ""
        tonic_changed = (
            old_tonic is None or old_tonic.root_pitch_class != chord_definition.root_pitch_class
        )

        if self.selected_chord and self.selected_chord.key == chord_definition.key:
            self.selected_chord = None
            self.chord_button_group.setExclusive(False)
            self.chord_buttons[chord_definition.key].setChecked(False)
            self.chord_button_group.setExclusive(True)
        else:
            self.selected_chord = chord_definition

        if tonic_changed and self.selected_progression:
            self.progression_step = 0
            self.progression_status_override = ""
        self._update_progression_ui()

    def clear_chord_selection(self):
        self.progression_status_override = ""
        if self.library_mode == "progressions":
            self.selected_progression = None
            self.progression_chords = ()
            self.progression_button_group.setExclusive(False)
            for button in self.progression_buttons.values():
                button.setChecked(False)
            self.progression_button_group.setExclusive(True)
            self.progression_step = 0
            self._render_progression_steps()
        else:
            self.selected_chord = None
            self.chord_button_group.setExclusive(False)
            for button in self.chord_buttons.values():
                button.setChecked(False)
            self.chord_button_group.setExclusive(True)
        self._refresh_chord_display()

    def toggle_progressions_view(self):
        target_mode = "chords" if self.library_mode == "progressions" else "progressions"
        self.set_library_mode(target_mode)

    def set_library_mode(self, mode):
        self.library_mode = mode
        self.chords_tab.setChecked(mode == "chords")
        self.progressions_tab.setChecked(mode == "progressions")
        self.library_stack.setCurrentWidget(
            self.chords_page if mode == "chords" else self.progressions_page
        )
        self.progression_status_override = ""
        self.clear_chord_button.setText(
            "CLEAR GUIDE" if mode == "progressions" else "CLEAR TARGET"
        )
        self._refresh_chord_display()

    def select_progression(self, progression):
        if not self.progression_tonic:
            return
        self.selected_progression = progression
        self.progression_chords = resolve_progression(
            progression, self.progression_tonic
        )
        self.progression_step = 0
        self.progression_status_override = ""
        button = self.progression_buttons[progression.key]
        button.setChecked(True)
        self._render_progression_steps()
        self._refresh_chord_display()

    def set_progression_step(self, step):
        if not self.progression_chords:
            return
        self.progression_step = max(
            0, min(step, len(self.progression_chords) - 1)
        )
        self.progression_status_override = ""
        self._render_progression_steps()
        self._refresh_chord_display()

    def _update_progression_ui(self):
        self.clear_chord_button.setText(
            "CLEAR GUIDE" if self.library_mode == "progressions" else "CLEAR TARGET"
        )
        has_tonic = self.progression_tonic is not None
        if has_tonic:
            self.progression_key_label.setText(
                f"KEY  ·  {self.progression_tonic.root} MAJOR"
            )
        else:
            self.progression_key_label.setText("KEY  ·  SELECT A CHORD")
        for button in self.progression_buttons.values():
            button.setEnabled(has_tonic)

        if self.selected_progression and has_tonic:
            self.progression_chords = resolve_progression(
                self.selected_progression, self.progression_tonic
            )
        else:
            self.progression_chords = ()
        self._render_progression_steps()
        self._refresh_chord_display()

    def _render_progression_steps(self):
        if hasattr(self, "progression_step_group"):
            self.progression_step_group.setExclusive(False)
            for button in self.progression_step_group.buttons():
                self.progression_step_group.removeButton(button)
            self.progression_step_group.deleteLater()
        while self.progression_steps_layout.count():
            item = self.progression_steps_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.progression_step_buttons = []
        if not self.progression_chords or not self.selected_progression:
            self.previous_step_button.setEnabled(False)
            self.next_step_button.setEnabled(False)
            return

        self.progression_step_group = QButtonGroup(self)
        self.progression_step_group.setExclusive(True)
        step_style = "QPushButton{color:#b4acca;background:#171832;border:1px solid #37315e;border-radius:6px;padding:5px 1px;font-size:9px;font-weight:bold;} QPushButton:checked{color:#fff;background:#55275f;border-color:#ff75d8;} QPushButton:hover{border-color:#8172be;}"
        for index, (step, chord) in enumerate(
            zip(self.selected_progression.steps, self.progression_chords)
        ):
            button = QPushButton(f"{step.numeral}\n{chord.short_name}")
            button.setCheckable(True)
            button.setChecked(index == self.progression_step)
            button.setToolTip(chord.name)
            button.setStyleSheet(step_style)
            self.progression_step_group.addButton(button)
            button.clicked.connect(
                lambda checked=False, step_index=index: self.set_progression_step(step_index)
            )
            self.progression_step_buttons.append(button)
            self.progression_steps_layout.addWidget(button, 1)

        self.previous_step_button.setEnabled(self.progression_step > 0)
        self.next_step_button.setEnabled(
            self.progression_step < len(self.progression_chords) - 1
        )

    def _visible_target_chord(self):
        if self.library_mode == "progressions":
            if (
                self.progression_chords
                and self.progression_step < len(self.progression_chords)
            ):
                return self.progression_chords[self.progression_step]
            return None
        return self.selected_chord

    def _refresh_chord_display(self):
        self.piano.set_active_notes(self.current_active_notes)
        target = self._visible_target_chord()
        target_notes = (
            target.voicing_indices(len(self.piano.keys)) if target else ()
        )
        self.piano.set_target_notes(target_notes)

        if self.library_mode == "progressions" and not self.progression_tonic:
            self.display_kicker.setText("PROGRESSION GUIDE")
            self.chord_label.setFont(QFont("Arial", 36, QFont.Bold))
            self.chord_label.setStyleSheet("color:#f4eaff;border:none;")
            self.chord_label.setText("Choose a key")
            self.notes_label.setStyleSheet("color:#9b91c5;border:none;letter-spacing:2px;")
            self.notes_label.setText("SELECT A MAJOR CHORD IN CHORDS")
            self.live_chord_label.clear()
            return

        if self.library_mode == "progressions" and not self.selected_progression:
            self.display_kicker.setText(
                f"KEY  ·  {self.progression_tonic.root.upper()} MAJOR"
            )
            self.chord_label.setFont(QFont("Arial", 34, QFont.Bold))
            self.chord_label.setStyleSheet("color:#f4eaff;border:none;")
            self.chord_label.setText("Choose a progression")
            self.notes_label.setStyleSheet("color:#9b91c5;border:none;letter-spacing:2px;")
            self.notes_label.setText("SELECT A PATTERN TO BEGIN")
            self.live_chord_label.clear()
            return

        if target:
            if self.library_mode == "progressions":
                degree = self.selected_progression.steps[self.progression_step].numeral
                self.display_kicker.setText(
                    f"{self.selected_progression.name}  ·  STEP {self.progression_step + 1}/4  ·  {degree}"
                )
            else:
                self.display_kicker.setText("CHORD TARGET")
            self.chord_label.setFont(QFont("Arial", 72, QFont.Bold))
            self.chord_label.setStyleSheet("color:#f4eaff;border:none;")
            self.chord_label.setText(target.name)
            self.notes_label.setStyleSheet("color:#ffb8ec;border:none;letter-spacing:2px;")
            self.notes_label.setText(
                "NOTES TO PLAY  ·  " + "  ·  ".join(target.note_names)
            )

            active_pitch_classes = {
                note % 12 for note in self.current_active_notes
            }
            if self.progression_status_override:
                status = self.progression_status_override
            elif target.pitch_classes == active_pitch_classes:
                status = "CHORD COMPLETE"
            elif self.current_active_notes:
                heard = self.current_chord
                if heard == "Invalid chord":
                    heard = self.current_note_text.upper()
                status = f"PLAYING  ·  {heard}"
            else:
                status = "FOLLOW THE HIGHLIGHTED KEYS"
            self.live_chord_label.setText(status)
            return

        self.display_kicker.setText("NOW PLAYING")
        self.live_chord_label.clear()
        if self.current_chord == "Invalid chord":
            self.chord_label.setFont(QFont("Arial", 30, QFont.Bold))
            self.chord_label.setStyleSheet("color:#ff75a8;border:none;")
        else:
            self.chord_label.setFont(QFont("Arial", 72, QFont.Bold))
            self.chord_label.setStyleSheet("color:#f4eaff;border:none;")
        self.chord_label.setText(self.current_chord)
        self.notes_label.setStyleSheet("color:#9b91c5;border:none;letter-spacing:2px;")
        self.notes_label.setText(
            self.current_note_text.upper()
            if self.current_note_text
            else "PLAY A CHORD TO BEGIN"
        )

    def select_octaves(self, value):
        self.piano.draw_keys(int(value))
        self._refresh_chord_display()

    def open_settings(self):
        self.settings_dialog.exec_()
