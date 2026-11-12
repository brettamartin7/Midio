#!/usr/bin/env python3
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import logging


APP_STYLE = """
QWidget#Window { background-color: #090b1d; color: #f3f1ff; }
QFrame#SideMenu { background-color: #10122b; border-right: 1px solid #29244d; }
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


class Piano(QWidget):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.setObjectName("PianoWidget")
        self.keys = {}
        self.draw_keys(4)
        main_window.layout.addWidget(self, 0, Qt.AlignHCenter)

    def draw_keys(self, num_octaves):
        for key in self.keys.values():
            key.deleteLater()
        self.keys = {}

        white_key_x = 20
        num_keys = num_octaves * 12
        black_notes = [1, 3, 6, 8, 10]

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
                white_key_x += 40
            btn.setCursor(Qt.PointingHandCursor)
            self.keys[i] = btn
            btn.show()

        for i in range(num_keys):
            if (i % 12) in black_notes:
                self.keys[i].raise_()

        self.setFixedSize(white_key_x + 20, 245)

    def activate_button(self, note):
        try:
            if note in self.keys:
                self.keys[note].setDisabled(True)
        except Exception as e:
            logging.warning(e)

    def deactivate_button(self, note):
        try:
            if note in self.keys:
                self.keys[note].setDisabled(False)
        except Exception as e:
            logging.warning(e)


class Window(QWidget):
    audio_preset_selected = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.setObjectName("Window")
        self.setStyleSheet(APP_STYLE)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.side_menu = QFrame(self)
        self.side_menu.setObjectName("SideMenu")
        self.side_menu.setFixedWidth(0)
        self.side_menu_layout = QVBoxLayout(self.side_menu)
        self.side_menu_layout.setContentsMargins(14, 24, 14, 24)
        self.side_menu_layout.setSpacing(8)
        self.side_menu_layout.setAlignment(Qt.AlignTop)

        menu_title = QLabel("STUDIO SETTINGS")
        menu_title.setStyleSheet("color:#8d83ba; font-size:10px; font-weight:bold; letter-spacing:2px; padding:0 10px 10px;")
        self.side_menu_layout.addWidget(menu_title)
        menu_btn_style = """
        QPushButton { color:#d9d5f3; background:transparent; text-align:left; padding:12px 10px;
            font-size:13px; border:1px solid transparent; border-radius:8px; }
        QPushButton:hover { color:#fff; background:#211d42; border-color:#443969; }
        """
        self.btn_presets = QToolButton()
        self.btn_presets.setText("Audio Presets")
        self.btn_presets.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.btn_presets.setArrowType(Qt.DownArrow)
        self.btn_presets.setPopupMode(QToolButton.InstantPopup)
        self.btn_presets.setStyleSheet("QToolButton { color:#d9d5f3; background:transparent; text-align:left; padding:12px 10px; font-size:13px; border:1px solid transparent; border-radius:8px; } QToolButton:hover { color:#fff; background:#211d42; border-color:#443969; } QToolButton::menu-indicator { image:none; }")
        self.preset_menu = QMenu(self.btn_presets)
        self.btn_presets.setMenu(self.preset_menu)
        self.btn_midi = QPushButton("MIDI Input Device")
        self.btn_audio = QPushButton("Audio Settings")
        self.btn_octaves = QPushButton("Octaves Shown")
        self.side_menu_layout.addWidget(self.btn_presets)
        for button in (self.btn_midi, self.btn_audio, self.btn_octaves):
            button.setStyleSheet(menu_btn_style)
            self.side_menu_layout.addWidget(button)
        self.btn_octaves.clicked.connect(self.select_octaves)
        self.main_layout.addWidget(self.side_menu)

        self.content_widget = QWidget(self)
        self.content_widget.setObjectName("Content")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(38, 25, 38, 28)
        self.content_layout.setSpacing(20)

        self.header_layout = QHBoxLayout()
        self.header_layout.setSpacing(15)
        self.hamburger = QPushButton("☰")
        self.hamburger.setFixedSize(42, 42)
        self.hamburger.setCursor(Qt.PointingHandCursor)
        self.hamburger.setStyleSheet("QPushButton{color:#b8a8ff;font-size:21px;background:#15152f;border:1px solid #37315e;border-radius:12px;} QPushButton:hover{color:#ff75d8;border-color:#ff75d8;}")
        self.hamburger.clicked.connect(self.toggle_menu)
        self.header_layout.addWidget(self.hamburger)

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

        self.mute_btn = QPushButton("🔊")
        self.mute_btn.setFixedSize(46, 42)
        self.mute_btn.setCursor(Qt.PointingHandCursor)
        self.mute_btn.setToolTip("Toggle audio")
        self.mute_btn.setStyleSheet("QPushButton{color:#d8d2f2;font-size:19px;background:#15152f;border:1px solid #37315e;border-radius:12px;} QPushButton:hover{color:#80f6ff;border-color:#80f6ff;}")
        self.header_layout.addWidget(self.mute_btn)
        self.content_layout.addLayout(self.header_layout)

        self.display_frame = QFrame(self.content_widget)
        self.display_frame.setObjectName("DisplayFrame")
        self.display_frame.setStyleSheet("QFrame#DisplayFrame{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #171632,stop:0.55 #11142d,stop:1 #1b1234);border:1px solid #39315f;border-radius:20px;}")
        self.display_frame.setMinimumHeight(300)
        self.display_layout = QVBoxLayout(self.display_frame)
        self.display_layout.setContentsMargins(28, 25, 28, 25)
        self.display_layout.setSpacing(7)

        display_kicker = QLabel("NOW PLAYING")
        display_kicker.setAlignment(Qt.AlignCenter)
        display_kicker.setStyleSheet("color:#ff75d8;font-size:10px;font-weight:bold;letter-spacing:3px;border:none;")
        self.display_layout.addWidget(display_kicker)

        self.chord_label = QLabel("Ready")
        self.chord_label.setFont(QFont("Arial", 72, QFont.Bold))
        self.chord_label.setAlignment(Qt.AlignCenter)
        self.chord_label.setStyleSheet("color:#f4eaff;border:none;")

        self.notes_label = QLabel("PLAY A CHORD TO BEGIN")
        self.notes_label.setFont(QFont("Arial", 15))
        self.notes_label.setAlignment(Qt.AlignCenter)
        self.notes_label.setStyleSheet("color:#9b91c5;border:none;letter-spacing:2px;")
        self.display_layout.addStretch(1)
        self.display_layout.addWidget(self.chord_label)
        self.display_layout.addWidget(self.notes_label)
        self.display_layout.addStretch(1)
        self.content_layout.addWidget(self.display_frame, 1)

        keyboard_header = QHBoxLayout()
        keyboard_title = QLabel("KEYBOARD")
        keyboard_title.setStyleSheet("color:#a59dc9;font-size:10px;font-weight:bold;letter-spacing:3px;")
        keyboard_hint = QLabel("MIDI NOTE ACTIVITY")
        keyboard_hint.setStyleSheet("color:#625d83;font-size:9px;letter-spacing:2px;")
        keyboard_header.addWidget(keyboard_title)
        keyboard_header.addStretch()
        keyboard_header.addWidget(keyboard_hint)
        self.content_layout.addLayout(keyboard_header)

        self.main_layout.addWidget(self.content_widget)
        self.layout = self.content_layout
        self.piano = Piano(self)

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
            self.btn_presets.setText(f"Audio Presets  ·  {selected_name}")

    def _choose_audio_preset(self, preset_key, preset_name):
        self.btn_presets.setText(f"Audio Presets  ·  {preset_name}")
        self.audio_preset_selected.emit(preset_key)

    def update_note_display(self, active_notes, note_text, chord):
        active_notes = set(active_notes)
        for key in self.piano.keys:
            if key in active_notes:
                self.piano.activate_button(key)
            else:
                self.piano.deactivate_button(key)

        if chord == "Invalid chord":
            self.chord_label.setFont(QFont("Arial", 30, QFont.Bold))
            self.chord_label.setStyleSheet("color:#ff75a8;border:none;")
        else:
            self.chord_label.setFont(QFont("Arial", 72, QFont.Bold))
            self.chord_label.setStyleSheet("color:#f4eaff;border:none;")
        self.chord_label.setText(chord)
        self.notes_label.setText(note_text.upper() if note_text else "PLAY A CHORD TO BEGIN")

    def select_octaves(self):
        num, ok = QInputDialog.getInt(self, "Octaves Shown", "Select number of octaves (1-6):", 4, 1, 6, 1)
        if ok:
            self.piano.draw_keys(num)
            self.adjustSize()

    def toggle_menu(self):
        width = self.side_menu.width()
        end_width = 250 if width == 0 else 0

        self.anim = QPropertyAnimation(self.side_menu, b"minimumWidth")
        self.anim.setDuration(300)
        self.anim.setStartValue(width)
        self.anim.setEndValue(end_width)
        self.anim.setEasingCurve(QEasingCurve.InOutQuart)
        self.anim.start()

        self.anim2 = QPropertyAnimation(self.side_menu, b"maximumWidth")
        self.anim2.setDuration(300)
        self.anim2.setStartValue(width)
        self.anim2.setEndValue(end_width)
        self.anim2.setEasingCurve(QEasingCurve.InOutQuart)
        self.anim2.start()
