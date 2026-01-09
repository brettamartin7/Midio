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


class Piano(object):
    def __init__(self, main_window):
        self.centralwidget = QWidget(main_window)
        self.centralwidget.setObjectName("centralwidget")
        
        self.keys = {}
        white_key_x = 20
        
        # Generate 4 octaves (48 keys)
        for i in range(48):
            # 0=C, 1=C#, 2=D, 3=D#, 4=E, 5=F, 6=F#, 7=G, 8=G#, 9=A, 10=A#, 11=B
            is_black = (i % 12) in [1, 3, 6, 8, 10]
            
            if is_black:
                # Black keys are positioned relative to the gap between white keys.
                # Based on previous logic: x = current_white_x - 20
                btn = QPushButton(self.centralwidget)
                btn.setGeometry(QRect(white_key_x - 20, 30, 31, 111))
                btn.setStyleSheet(blackKeyStyleSheet)
                btn.setObjectName("black_key")
                self.keys[i] = btn
            else:
                btn = QPushButton(self.centralwidget)
                btn.setGeometry(QRect(white_key_x, 30, 41, 181))
                btn.setStyleSheet(whiteKeyStyleSheet)
                btn.setObjectName("white_key")
                self.keys[i] = btn
                white_key_x += 40

        # Raise black keys so they appear on top
        for i in range(48):
            if (i % 12) in [1, 3, 6, 8, 10]:
                self.keys[i].raise_()

        self.centralwidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.centralwidget.resize(white_key_x + 20, 400)
        main_window.layout.addWidget(self.centralwidget)

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

        self.chord_label = QLabel("Chord", self)
        self.chord_label.setFont(QFont('Arial', 100))
        self.chord_label.resize(300, 300)
        self.chord_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.chord_label.setAlignment(Qt.AlignCenter)
        self.chord_label.setStyleSheet("color: #dfe6e9;")

        self.notes_label = QLabel("Active Notes", self)
        self.notes_label.setFont(QFont('Arial', 30))
        self.notes_label.resize(300, 300)
        self.notes_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.notes_label.setAlignment(Qt.AlignCenter)
        self.notes_label.setStyleSheet("color: #b2bec3;")

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.chord_label)
        self.layout.addWidget(self.notes_label)
        self.layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout)
        self.resize(1250, 600)
        self.show()

    def setNote(self, input_note):
        self.chord_label.setText(input_note)
