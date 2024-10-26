import numpy as np
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QColorDialog, QLineEdit, QSizePolicy


class ColorPicker(QWidget):
    def __init__(self, default_color=np.ones(3, dtype=int)):
        super().__init__()
        self.color = default_color

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.color_box = QLineEdit()
        self.color_box.setFixedSize(QSize(20, 20))
        self.color_box.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.color_box.setEnabled(False)

        r_255 = int(self.color[0] * 255)
        g_255 = int(self.color[1] * 255)
        b_255 = int(self.color[2] * 255)

        self.color_box.setStyleSheet(f'background-color: rgb({r_255}, {g_255}, {b_255})')

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
            self.color = color.getRgbF()[0:3]

    def sizeHint(self):
        size = QWidget.sizeHint(self)
        return QSize(size.width(), size.height() + 2)
