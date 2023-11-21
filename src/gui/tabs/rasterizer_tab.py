import math

import numpy as np
from PyQt5.QtCore import Qt, pyqtSignal, QLocale
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QRadioButton, QButtonGroup, \
    QHBoxLayout, QGroupBox

from src.gui.widgets.color_picker_widget import ColorPicker
from src.gui.widgets.registration_input_field_widget import SimpleInputField

from src.utils.graphics_utils import fov2focal
import src.utils.graphics_utils as graphic_util

class RasterizerTab(QWidget):
    signal_rasterize = pyqtSignal(int, int, float, np.ndarray, object)

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
            "    font-size: 11pt;"
            "    font-weight: bold;"
            f"    padding: {int(graphic_util.SIZE_SCALE_X * 8)}px;"
            "}"
        )

        option_widget = QGroupBox()
        option_widget.setTitle("Dimensions")
        options_layout = QVBoxLayout()
        option_widget.setLayout(options_layout)
        self.image_width_widget = SimpleInputField("Image width:", "512", 75, validator=int_validator)
        self.image_height_widget = SimpleInputField("Image height:", "512", 75, validator=int_validator)

        self.scale = SimpleInputField("Scale:", "1.0", 75, validator=double_validator)
        self.background_color_widget = ColorPicker("Background color: ", np.zeros(3))

        bt_rasterize = QPushButton("Rasterize")
        bt_rasterize.setStyleSheet(f"padding-left: 10px; padding-right: {int(graphic_util.SIZE_SCALE_X * 10)}px;"
                                   f"padding-top: 2px; padding-bottom: {int(graphic_util.SIZE_SCALE_X * 2)}px;")
        bt_rasterize.setFixedSize(int(250 * graphic_util.SIZE_SCALE_X), int(30 * graphic_util.SIZE_SCALE_Y))
        bt_rasterize.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        bt_rasterize.clicked.connect(self.button_clicked)

        options_layout.addWidget(self.image_width_widget)
        options_layout.addWidget(self.image_height_widget)
        options_layout.addWidget(self.scale)
        options_layout.addWidget(self.background_color_widget)

        widget_fov_group_box = QGroupBox()
        widget_fov_group_box.setTitle("FOV")
        layout_group_box = QVBoxLayout()
        widget_fov_group_box.setLayout(layout_group_box)

        widget_radio_group = QWidget()
        layout_radio = QHBoxLayout()
        widget_radio_group.setLayout(layout_radio)

        rb_default = QRadioButton("Default")
        rb_fov = QRadioButton("Field of View")
        rb_focal = QRadioButton("Focal Length")
        self.button_group = QButtonGroup(self)
        self.button_group.addButton(rb_default, id=0)
        self.button_group.addButton(rb_fov, id=1)
        self.button_group.addButton(rb_focal, id=2)
        layout_radio.addWidget(rb_default)
        layout_radio.addWidget(rb_fov)
        layout_radio.addWidget(rb_focal)
        rb_default.setChecked(True)

        self.fov_widget = SimpleInputField("FOV/FX:", "0.0", 60, validator=double_validator)
        self.fov_widget.setEnabled(False)

        self.button_group.idToggled.connect(self.fov_source_changed)

        layout_group_box.addWidget(widget_radio_group)
        layout_group_box.addWidget(self.fov_widget)

        layout.addWidget(label_res)
        layout.addWidget(option_widget)
        layout.addWidget(widget_fov_group_box)

        layout.addWidget(bt_rasterize, alignment=Qt.AlignCenter)
        layout.addStretch()

    def button_clicked(self):
        width = int(self.image_width_widget.lineedit.text())
        height = int(self.image_height_widget.lineedit.text())
        scale = float(self.scale.lineedit.text())
        color = np.asarray(self.background_color_widget.color_debug)
        intrinsics = self.create_intrinsics()
        self.signal_rasterize.emit(width, height, scale, color, intrinsics)

    def fov_source_changed(self, button_id, checked):
        self.fov_widget.setEnabled(button_id != 0 and checked)

    def create_intrinsics(self):
        width = float(self.image_width_widget.lineedit.text())
        height = float(self.image_height_widget.lineedit.text())
        fx = 0.0
        fy = 0.0
        button_id = self.button_group.checkedId()
        value = float(self.fov_widget.lineedit.text())
        match button_id:
            case 0:
                return None
            case 1:
                # if value is greate than pi, the user entered the fov in degrees
                if value > math.pi:
                    value = value * math.pi / 180
                fx = fov2focal(value, width)
                fy = fov2focal(value, height)
            case 2:
                fx = value
                fy = fx * (width/height)
        cx = width / 2
        cy = height / 2
        intrinsics = np.array([
            [fx, 0, cx],
            [0, fy, cy],
            [0, 0, 1]
        ])
        return intrinsics
