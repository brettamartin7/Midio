#!/usr/bin/env python3
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import logging

blackKeyStyleSheet = \
    """
#black_key {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #444, stop:1 #111);
    border: 1px solid #000;
    border-bottom-left-radius: 6px;
    border-bottom-right-radius: 6px;
}
#black_key:disabled {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #00cec9, stop:1 #00b894);
    border: 1px solid #00b894;
}
"""

whiteKeyStyleSheet = \
    """
#white_key {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #fff, stop:1 #eee);
    border: 1px solid #999;
    border-bottom-left-radius: 8px;
    border-bottom-right-radius: 8px;
}
#white_key:disabled {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #81ecec, stop:1 #00cec9);
    border: 1px solid #00cec9;
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

        for i in range(num_keys):
            # 0=C, 1=C#, 2=D, 3=D#, 4=E, 5=F, 6=F#, 7=G, 8=G#, 9=A, 10=A#, 11=B
            is_black = (i % 12) in [1, 3, 6, 8, 10]
            
            if is_black:
                # Black keys are positioned relative to the gap between white keys.
                # Based on previous logic: x = current_white_x - 20
                btn = QPushButton(self)
                btn.setGeometry(QRect(white_key_x - 20, 30, 31, 111))
                btn.setStyleSheet(blackKeyStyleSheet)
                btn.setObjectName("black_key")
                self.keys[i] = btn
                btn.show()
            else:
                btn = QPushButton(self)
                btn.setGeometry(QRect(white_key_x, 30, 41, 181))
                btn.setStyleSheet(whiteKeyStyleSheet)
                btn.setObjectName("white_key")
                self.keys[i] = btn
                btn.show()
                white_key_x += 40

        # Raise black keys so they appear on top
        for i in range(num_keys):
            if (i % 12) in [1, 3, 6, 8, 10]:
                self.keys[i].raise_()

        self.setFixedSize(white_key_x + 20, 250)

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
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)

        self.setStyleSheet("background-color: #2d3436;")

        # Main Layout
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Side Menu
        self.side_menu = QFrame(self)
        self.side_menu.setStyleSheet("background-color: #1e272e; border-right: 1px solid #636e72;")
        self.side_menu.setFixedWidth(0)
        self.side_menu_layout = QVBoxLayout(self.side_menu)
        self.side_menu_layout.setContentsMargins(10, 20, 10, 20)
        self.side_menu_layout.setAlignment(Qt.AlignTop)

        menu_btn_style = "QPushButton { color: #dfe6e9; background-color: transparent; text-align: left; padding: 12px; font-size: 16px; border: none; border-radius: 5px; } QPushButton:hover { background-color: #2d3436; }"

        self.btn_modes = QPushButton("Modes")
        self.btn_modes.setStyleSheet(menu_btn_style)
        self.side_menu_layout.addWidget(self.btn_modes)

        self.btn_midi = QPushButton("MIDI Keyboard")
        self.btn_midi.setStyleSheet(menu_btn_style)
        self.side_menu_layout.addWidget(self.btn_midi)

        self.btn_audio = QPushButton("Audio Settings")
        self.btn_audio.setStyleSheet(menu_btn_style)
        self.side_menu_layout.addWidget(self.btn_audio)

        self.btn_octaves = QPushButton("Octaves Shown")
        self.btn_octaves.setStyleSheet(menu_btn_style)
        self.btn_octaves.clicked.connect(self.select_octaves)
        self.side_menu_layout.addWidget(self.btn_octaves)

        self.main_layout.addWidget(self.side_menu)

        # Content Area
        self.content_widget = QWidget(self)
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(30, 30, 30, 30)
        self.content_layout.setSpacing(30)

        # Header
        self.header_layout = QHBoxLayout()
        self.hamburger = QPushButton("☰")
        self.hamburger.setFixedSize(40, 40)
        self.hamburger.setCursor(Qt.PointingHandCursor)
        self.hamburger.setStyleSheet("QPushButton { color: #dfe6e9; font-size: 24px; background-color: transparent; border: none; } QPushButton:hover { color: #81ecec; }")
        self.hamburger.clicked.connect(self.toggle_menu)
        self.header_layout.addWidget(self.hamburger)
        self.header_layout.addStretch()

        self.mute_btn = QPushButton("🔊")
        self.mute_btn.setFixedSize(40, 40)
        self.mute_btn.setCursor(Qt.PointingHandCursor)
        self.mute_btn.setStyleSheet("QPushButton { color: #dfe6e9; font-size: 24px; background-color: transparent; border: none; } QPushButton:hover { color: #81ecec; }")
        self.header_layout.addWidget(self.mute_btn)

        self.content_layout.addLayout(self.header_layout)

        # Create a display frame for a stylized look
        self.display_frame = QFrame(self.content_widget)
        self.display_frame.setStyleSheet("""
            QFrame {
                background-color: #1e272e;
                border: 3px solid #636e72;
                border-radius: 20px;
            }
        """)

        self.display_layout = QVBoxLayout(self.display_frame)
        self.display_layout.setContentsMargins(20, 20, 20, 20)
        
        # Chord String
        self.chord_label = QLabel("Chord", self.display_frame)
        self.chord_label.setFont(QFont('Arial', 80, QFont.Bold))
        self.chord_label.setAlignment(Qt.AlignCenter)
        self.chord_label.setStyleSheet("color: #81ecec; border: none;")

        # Notes String
        self.notes_label = QLabel("Active Notes", self.display_frame)
        self.notes_label.setFont(QFont('Arial', 30))
        self.notes_label.setAlignment(Qt.AlignCenter)
        self.notes_label.setStyleSheet("color: #fab1a0; border: none;")

        # Layout containing chord and notes
        self.display_layout.addWidget(self.chord_label)
        self.display_layout.addWidget(self.notes_label)

        self.content_layout.addWidget(self.display_frame, 0, Qt.AlignHCenter)
        self.main_layout.addWidget(self.content_widget)

        # Alias layout for Piano class
        self.layout = self.content_layout
        self.piano = Piano(self)

        self.resize(1250, 700)
        self.show()

    def setNote(self, input_note):
        self.chord_label.setText(input_note)

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
