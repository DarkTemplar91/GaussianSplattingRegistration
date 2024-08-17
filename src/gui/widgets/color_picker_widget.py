import numpy as np
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QColorDialog, QLineEdit, QSizePolicy
import src.utils.graphics_utils as graphic_util


class ColorPicker(QWidget):
    def __init__(self, default_color=np.ones(3, dtype=int) * 255):
        super().__init__()
        self.color_debug = default_color

        layout = QHBoxLayout()
        self.setLayout(layout)

        self.color_box = QLineEdit()
        self.color_box.setFixedSize(QSize(20, 20))
        self.color_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.color_box.setEnabled(False)

        # generate an array with strings
        x_arrstr = np.char.mod('%d', self.color_debug)
        # combine to a string
        color_str = ",".join(x_arrstr)

        self.color_box.setStyleSheet(f"background:rgb({color_str});")

        button = QPushButton()
        button.setText("Pick color")
        button.setStyleSheet(f"padding-left: 10px; padding-right: {int(graphic_util.SIZE_SCALE_X * 10)}px;"
                             f"padding-top: 2px; padding-bottom: {int(graphic_util.SIZE_SCALE_X * 2)}px;")

        layout.addWidget(self.color_box)
        layout.addWidget(button)

        layout.addStretch()

        button.clicked.connect(self.button_clicked)

    def button_clicked(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_box.setStyleSheet(f"background-color: {color.name()};")
            self.color_debug = color.getRgbF()[0:3]
