#!/usr/bin/env python3
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import logging


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

        self.main_layout.addWidget(self.content_widget)
        self.layout = self.content_layout
        self.piano = Piano(self)
        self.octave_selector.currentTextChanged.connect(self.select_octaves)

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

    def select_octaves(self, value):
        self.piano.draw_keys(int(value))

    def open_settings(self):
        self.settings_dialog.exec_()
