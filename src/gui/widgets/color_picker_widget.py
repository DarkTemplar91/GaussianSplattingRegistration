import numpy as np
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QColorDialog, QLineEdit


class ColorPicker(QWidget):
    def __init__(self, label_text=""):
        super().__init__()
        self.color_debug = np.zeros(3, dtype=float)

        layout = QHBoxLayout()
        self.setLayout(layout)

        label = QLabel(label_text)

        self.color_box = QLineEdit()
        self.color_box.setFixedSize(20, 20)
        self.color_box.setEnabled(False)
        self.color_box.setStyleSheet("background-color:rgb(0;,0;,0;);")

        button = QPushButton()
        button.setText("Pick color")
        button.setStyleSheet("padding-left: 10px; padding-right: 10px;"
                             "padding-top: 2px; padding-bottom: 2px;")

        layout.addWidget(label)
        layout.addWidget(self.color_box)
        layout.addWidget(button)

        layout.addStretch()

        button.clicked.connect(self.button_clicked)

    def button_clicked(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_box.setStyleSheet(f"background-color: {color.name()};")
            self.color_debug = color.getRgbF()[0:3]
            print(self.color_debug)
