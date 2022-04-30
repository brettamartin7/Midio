#!/usr/bin/env python3
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


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
