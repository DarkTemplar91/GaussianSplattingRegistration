import numpy as np
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QColorDialog, QLineEdit


class ColorPicker(QWidget):
    def __init__(self, label_text="", default_color=np.ones(3, dtype=int)*255):
        super().__init__()
        self.color_debug = default_color

        layout = QHBoxLayout()
        self.setLayout(layout)

        label = QLabel(label_text)

        self.color_box = QLineEdit()
        self.color_box.setFixedSize(20, 20)
        self.color_box.setEnabled(False)

        # generate an array with strings
        x_arrstr = np.char.mod('%d', self.color_debug)
        # combine to a string
        color_str = ",".join(x_arrstr)

        self.color_box.setStyleSheet(f"background:rgb({color_str});")

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
