#!/usr/bin/env python3
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import logging

blackKeyStyleSheet = \
    """
#black_key:active{\n
background-color: rgb(0, 0, 0);\n
background-color: qlineargradient(spread:pad, x1:0.028, y1:0.619, x2:1, y2:0.494, stop:0.852273 rgba(0, 0, 0, 250), stop:1 rgba(255, 255, 255, 255));\n
}\n
#black_key:disabled{\n
background-color: rgb(255, 50, 0);\n
\n
background-color: qlineargradient(spread:pad, x1:0.857955, y1:0.0170455, x2:1, y2:0, stop:0.125 rgba(200, 0, 0, 255), stop:0.977273 rgba(255, 255, 255, 255));\n
border-style: solid;\n
border-width: 2px;\n
border-color: black;\n
\n
}\n
"""

whiteKeyStyleSheet = \
    """
#white_key:active{\n
background-color: rgb(242, 242, 242);\n
background-color: qlineargradient(spread:pad, x1:1, y1:0.711, x2:0.903455, y2:0.711, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(255, 255, 255, 255));\n
}\n
#white_key:disabled{\n
background-color: rgb(240, 0, 0);\n
border-style: solid;\n
border-width: 2px;\n
border-color: black;\n
\n
}\n
"""


class Piano(object):
    def __init__(self, main_window):
        self.centralwidget = QWidget(main_window)
        self.centralwidget.setObjectName("centralwidget")

        self.c4 = QPushButton(self.centralwidget)
        self.c4.setGeometry(QRect(20, 30, 41, 181))
        self.c4.setStyleSheet(whiteKeyStyleSheet)
        self.c4.setText("")
        self.c4.setObjectName("white_key")

        self.d4 = QPushButton(self.centralwidget)
        self.d4.setGeometry(QRect(60, 30, 41, 181))
        self.d4.setStyleSheet(whiteKeyStyleSheet)
        self.d4.setText("")
        self.d4.setObjectName("white_key")

        self.c40 = QPushButton(self.centralwidget)
        self.c40.setGeometry(QRect(40, 30, 31, 111))
        self.c40.setStyleSheet(blackKeyStyleSheet)
        self.c40.setText("")
        self.c40.setObjectName("black_key")

        self.d40 = QPushButton(self.centralwidget)
        self.d40.setGeometry(QRect(80, 30, 31, 111))
        self.d40.setStyleSheet(blackKeyStyleSheet)
        self.d40.setText("")
        self.d40.setObjectName("black_key")

        self.e4 = QPushButton(self.centralwidget)
        self.e4.setGeometry(QRect(100, 30, 41, 181))
        self.e4.setStyleSheet(whiteKeyStyleSheet)
        self.e4.setText("")
        self.e4.setObjectName("white_key")

        self.f4 = QPushButton(self.centralwidget)
        self.f4.setGeometry(QRect(140, 30, 41, 181))
        self.f4.setStyleSheet(whiteKeyStyleSheet)
        self.f4.setText("")
        self.f4.setObjectName("white_key")

        self.g4 = QPushButton(self.centralwidget)
        self.g4.setGeometry(QRect(180, 30, 41, 181))
        self.g4.setStyleSheet(whiteKeyStyleSheet)
        self.g4.setText("")
        self.g4.setObjectName("white_key")

        self.a4 = QPushButton(self.centralwidget)
        self.a4.setGeometry(QRect(220, 30, 41, 181))
        self.a4.setStyleSheet(whiteKeyStyleSheet)
        self.a4.setText("")
        self.a4.setObjectName("white_key")

        self.b4 = QPushButton(self.centralwidget)
        self.b4.setGeometry(QRect(260, 30, 41, 181))
        self.b4.setStyleSheet(whiteKeyStyleSheet)
        self.b4.setText("")
        self.b4.setObjectName("white_key")

        self.f40 = QPushButton(self.centralwidget)
        self.f40.setGeometry(QRect(160, 30, 31, 111))
        self.f40.setStyleSheet(blackKeyStyleSheet)
        self.f40.setText("")
        self.f40.setObjectName("black_key")

        self.g40 = QPushButton(self.centralwidget)
        self.g40.setGeometry(QRect(200, 30, 31, 111))
        self.g40.setStyleSheet(blackKeyStyleSheet)
        self.g40.setText("")
        self.g40.setObjectName("black_key")

        self.a40 = QPushButton(self.centralwidget)
        self.a40.setGeometry(QRect(240, 30, 31, 111))
        self.a40.setStyleSheet(blackKeyStyleSheet)
        self.a40.setText("")
        self.a40.setObjectName("black_key")


        self.c4.raise_()
        self.d4.raise_()
        self.c40.raise_()
        self.e4.raise_()
        self.f4.raise_()
        self.d40.raise_()
        self.g4.raise_()
        self.a4.raise_()
        self.b4.raise_()
        self.f40.raise_()
        self.g40.raise_()
        self.a40.raise_()

        # Define note dictionary
        self.piano_note_dict = {
            "C": self.c4,
            "C#/Db": self.c40,
            "D": self.d4,
            "D#/Eb": self.d40,
            "E": self.e4,
            "F": self.f4,
            "F#/Gb": self.f40,
            "G": self.g4,
            "G#/Ab": self.g40,
            "A": self.a4,
            "A#/Bb": self.a40,
            "B": self.b4
        }

        self.centralwidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.centralwidget.resize(400, 1000)
        main_window.layout.addWidget(self.centralwidget)

    # Roast me, makes sense for how this works
    def activate_button(self, note):
        try:
            self.piano_note_dict[note].setDisabled(True)
        except Exception as e:
            logging.warning(e)

    def deactivate_button(self, note):
        try:
            self.piano_note_dict[note].setDisabled(False)
        except Exception as e:
            logging.warning(e)

class Window(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)

        self.chord_label = QLabel("Chord", self)
        self.chord_label.setFont(QFont('Times', 200))
        self.chord_label.resize(300, 300)
        self.chord_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.chord_label.setAlignment(Qt.AlignCenter)
        self.chord_label.setStyleSheet("QLabel {background-color: white; color: black;}")

        self.notes_label = QLabel("Active Notes", self)
        self.notes_label.setFont(QFont('Times', 40))
        self.notes_label.resize(300, 300)
        self.notes_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.notes_label.setAlignment(Qt.AlignCenter)
        self.notes_label.setStyleSheet("QLabel {background-color: white; color: black;}")

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.chord_label)
        self.layout.addWidget(self.notes_label)
        self.layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout)
        self.resize(800, 800)
        self.show()

    def setNote(self, input_note):
        self.chord_label.setText(input_note)
