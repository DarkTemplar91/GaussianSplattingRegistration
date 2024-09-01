import numpy as np
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QColorDialog, QLineEdit, QSizePolicy


class ColorPicker(QWidget):
    def __init__(self, default_color=np.ones(3, dtype=int) * 255):
        super().__init__()
        self.color_debug = default_color

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.color_box = QLineEdit()
        self.color_box.setFixedSize(QSize(20, 20))
        self.color_box.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.color_box.setEnabled(False)

        x_arrstr = np.char.mod('%d', self.color_debug)
        color_str = ",".join(x_arrstr)

        self.color_box.setStyleSheet(f"background:rgb({color_str});")

        button = QPushButton()
        button.setText("Pick color")
        button.setStyleSheet(f"padding-left: 0.5em; padding-right: 0.5em;"
                             f"padding-top: 0.1em; padding-bottom: 0.1em;")

        layout.addWidget(self.color_box)
        layout.addWidget(button)

        layout.addStretch()

        button.clicked.connect(self.button_clicked)

    def button_clicked(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_box.setStyleSheet(f"background-color: {color.name()};")
            self.color_debug = color.getRgbF()[0:3]
