import numpy as np
from PyQt5.QtCore import Qt, pyqtSignal, QLocale
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QSizePolicy, QVBoxLayout

from src.gui.widgets.color_picker_widget import ColorPicker
from src.gui.widgets.registration_input_field_widget import SimpleInputField


class RasterizerTab(QWidget):
    signal_rasterize = pyqtSignal(int, int, float, np.ndarray)

    def __init__(self):
        super().__init__()

        locale = QLocale(QLocale.English)
        int_validator = QIntValidator()
        int_validator.setLocale(locale)
        int_validator.setRange(0, 999999999)

        double_validator = QDoubleValidator()
        double_validator.setLocale(locale)
        double_validator.setRange(0.0, 9999.0)
        double_validator.setDecimals(10)

        layout = QVBoxLayout()
        self.setLayout(layout)

        label_res = QLabel("Rasterization")
        label_res.setStyleSheet(
            "QLabel {"
            "    font-size: 14px;"
            "    font-weight: bold;"
            "    padding: 8px;"
            "}"
        )

        res_widget = QWidget()
        options_layout = QVBoxLayout()
        res_widget.setLayout(options_layout)
        self.image_width_widget = SimpleInputField("Image width:", "512", 75, validator=int_validator)
        self.image_height_widget = SimpleInputField("Image height:", "512", 75, validator=int_validator)

        self.scale = SimpleInputField("Scale:", "1.0", 75, validator=double_validator)
        self.background_color_widget = ColorPicker("Background color: ", np.zeros(3))

        bt_rasterize = QPushButton("Rasterize")
        bt_rasterize.setStyleSheet("padding-left: 10px; padding-right: 10px;"
                                   "padding-top: 2px; padding-bottom: 2px;")
        bt_rasterize.setFixedSize(250, 30)
        bt_rasterize.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        bt_rasterize.clicked.connect(self.button_clicked)

        options_layout.addWidget(self.image_width_widget)
        options_layout.addWidget(self.image_height_widget)
        options_layout.addWidget(self.scale)
        options_layout.addWidget(self.background_color_widget)

        layout.addWidget(label_res)
        layout.addWidget(res_widget)
        layout.addWidget(bt_rasterize, alignment=Qt.AlignCenter)
        layout.addStretch()

    def button_clicked(self):
        width = int(self.image_width_widget.lineedit.text())
        height = int(self.image_height_widget.lineedit.text())
        scale = float(self.scale.lineedit.text())
        color = np.asarray(self.background_color_widget.color_debug)
        self.signal_rasterize.emit(width, height, scale, color)
