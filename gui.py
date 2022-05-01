#!/usr/bin/env python3
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

blackKeyStyleSheet = \
"""
#black_key{\n
background-color: rgb(0, 0, 0);\n
background-color: qlineargradient(spread:pad, x1:0.028, y1:0.619, x2:1, y2:0.494, stop:0.852273 rgba(0, 0, 0, 250), stop:1 rgba(255, 255, 255, 255));\n
}\n
#black_key:pressed{\n
background-color: rgb(255, 0, 0);\n
\n
background-color: qlineargradient(spread:pad, x1:0.857955, y1:0.0170455, x2:1, y2:0, stop:0.125 rgba(200, 0, 0, 255), stop:0.977273 rgba(255, 255, 255, 255));\n
\n
}\n
"""

whiteKeyStyleSheet = \
"""
#white_key{\n
background-color: rgb(242, 242, 242);\n
background-color: qlineargradient(spread:pad, x1:1, y1:0.711, x2:0.903455, y2:0.711, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(255, 255, 255, 255));\n
}\n
#white_key:pressed{\n
background-color: rgb(240, 0, 0);\n
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

        self.c5 = QPushButton(self.centralwidget)
        self.c5.setGeometry(QRect(300, 30, 41, 181))
        self.c5.setStyleSheet(whiteKeyStyleSheet)
        self.c5.setText("")
        self.c5.setObjectName("white_key")

        self.d5 = QPushButton(self.centralwidget)
        self.d5.setGeometry(QRect(340, 30, 41, 181))
        self.d5.setStyleSheet(whiteKeyStyleSheet)
        self.d5.setText("")
        self.d5.setObjectName("white_key")

        self.a5 = QPushButton(self.centralwidget)
        self.a5.setGeometry(QRect(500, 30, 41, 181))
        self.a5.setStyleSheet(whiteKeyStyleSheet)
        self.a5.setText("")
        self.a5.setObjectName("white_key")

        self.e5 = QPushButton(self.centralwidget)
        self.e5.setGeometry(QRect(380, 30, 41, 181))
        self.e5.setStyleSheet(whiteKeyStyleSheet)
        self.e5.setText("")
        self.e5.setObjectName("white_key")

        self.g5 = QPushButton(self.centralwidget)
        self.g5.setGeometry(QRect(460, 30, 41, 181))
        self.g5.setStyleSheet(whiteKeyStyleSheet)
        self.g5.setText("")
        self.g5.setObjectName("white_key")

        self.f5 = QPushButton(self.centralwidget)
        self.f5.setGeometry(QRect(420, 30, 41, 181))
        self.f5.setStyleSheet(whiteKeyStyleSheet)
        self.f5.setText("")
        self.f5.setObjectName("white_key")

        self.b5 = QPushButton(self.centralwidget)
        self.b5.setGeometry(QRect(540, 30, 41, 181))
        self.b5.setStyleSheet(whiteKeyStyleSheet)
        self.b5.setText("")
        self.b5.setObjectName("white_key")

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

        self.c50 = QPushButton(self.centralwidget)
        self.c50.setGeometry(QRect(320, 30, 31, 111))
        self.c50.setStyleSheet(blackKeyStyleSheet)
        self.c50.setText("")
        self.c50.setObjectName("black_key")

        self.d50 = QPushButton(self.centralwidget)
        self.d50.setGeometry(QRect(360, 30, 31, 111))
        self.d50.setStyleSheet(blackKeyStyleSheet)
        self.d50.setText("")
        self.d50.setObjectName("black_key")

        self.f50 = QPushButton(self.centralwidget)
        self.f50.setGeometry(QRect(440, 30, 31, 111))
        self.f50.setStyleSheet(blackKeyStyleSheet)
        self.f50.setText("")
        self.f50.setObjectName("black_key")

        self.g50 = QPushButton(self.centralwidget)
        self.g50.setGeometry(QRect(480, 30, 31, 111))
        self.g50.setStyleSheet(blackKeyStyleSheet)
        self.g50.setText("")
        self.g50.setObjectName("black_key")

        self.a50 = QPushButton(self.centralwidget)
        self.a50.setGeometry(QRect(520, 30, 31, 111))
        self.a50.setStyleSheet(blackKeyStyleSheet)
        self.a50.setText("")
        self.a50.setObjectName("black_key")

        self.c4.raise_()
        self.d4.raise_()
        self.c40.raise_()
        self.e4.raise_()
        self.f4.raise_()
        self.d40.raise_()
        self.g4.raise_()
        self.a4.raise_()
        self.b4.raise_()
        self.c5.raise_()
        self.d5.raise_()
        self.a5.raise_()
        self.e5.raise_()
        self.g5.raise_()
        self.f5.raise_()
        self.b5.raise_()
        self.f40.raise_()
        self.g40.raise_()
        self.a40.raise_()
        self.c50.raise_()
        self.d50.raise_()
        self.f50.raise_()
        self.g50.raise_()
        self.a50.raise_()

        self.centralwidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.centralwidget.resize(400, 400)
        main_window.layout.addWidget(self.centralwidget, 2, 0)

class Window(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)

        self.chord_label = QLabel("Chord", self)
        self.chord_label.setFont(QFont('Times', 200))
        self.chord_label.resize(400,400)
        self.chord_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.chord_label.setAlignment(Qt.AlignCenter)
        self.chord_label.setStyleSheet("QLabel {background-color: white;}")

        self.notes_label = QLabel("Active Notes", self)
        self.notes_label.setFont(QFont('Times', 40))
        self.notes_label.resize(400, 400)
        self.notes_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.notes_label.setAlignment(Qt.AlignCenter)
        self.notes_label.setStyleSheet("QLabel {background-color: white;}")

        self.layout = QGridLayout()
        self.layout.addWidget(self.chord_label, 0, 0)
        self.layout.addWidget(self.notes_label, 1, 0)
        self.setLayout(self.layout)
        self.resize(800,800)
        self.show()

    def setNote(self, input_note):
        self.chord_label.setText(input_note)
