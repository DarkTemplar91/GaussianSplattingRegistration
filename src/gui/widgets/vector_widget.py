import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QColorDialog, QLineEdit, QVBoxLayout


class VectorWidget(QWidget):
    def __init__(self, label_text=""):
        super().__init__()
        self.values = np.array(3)

        layout = QHBoxLayout()
        self.setLayout(layout)

        label = QLabel(label_text)
        label.setFixedWidth(50)

        self.lineedit1 = QLineEdit("0.0")
        self.lineedit2 = QLineEdit("0.0")
        self.lineedit3 = QLineEdit("0.0")

        self.lineedit1.setAlignment(Qt.AlignLeft)
        self.lineedit2.setAlignment(Qt.AlignLeft)
        self.lineedit3.setAlignment(Qt.AlignLeft)

        self.lineedit1.setFixedWidth(60)
        self.lineedit2.setFixedWidth(60)
        self.lineedit3.setFixedWidth(60)

        layout.addWidget(label)
        layout.addWidget(self.lineedit1)
        layout.addWidget(self.lineedit2)
        layout.addWidget(self.lineedit3)
        layout.addStretch()
