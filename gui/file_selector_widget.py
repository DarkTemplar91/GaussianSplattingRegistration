from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QLabel, QPushButton, QSizePolicy, QStyle


class FileSelector(QWidget):
    def __init__(self, parent=None, text=None):
        super().__init__(parent)

        layout = QHBoxLayout()
        self.setLayout(layout)

        self.inputField = QLineEdit()
        self.label = QLabel(text)
        self.button = QPushButton()
        icon = self.style().standardIcon(QStyle.SP_DialogOpenButton)
        self.button.setIcon(icon)

        layout.addWidget(self.label)
        layout.addWidget(self.inputField)
        layout.addWidget(self.button)

        #self.inputField.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        layout.addStretch()
