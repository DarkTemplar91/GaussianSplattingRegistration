import numpy as np
from PySide6.QtCore import Signal, QLocale
from PySide6.QtGui import QIntValidator, QDoubleValidator
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QRadioButton, QButtonGroup, \
    QHBoxLayout, QGroupBox, QFormLayout

import src.utils.graphics_utils as graphic_util
from src.gui.widgets.custom_push_button import CustomPushButton
from src.gui.widgets.color_picker_widget import ColorPicker
from src.gui.widgets.simple_input_field_widget import SimpleInputField


class RasterizerTab(QWidget):
    signal_rasterize = Signal(int, int, float, np.ndarray, object)

    def __init__(self):
        super().__init__()

        locale = QLocale(QLocale.Language.C)
        locale.setNumberOptions(QLocale.NumberOption.RejectGroupSeparator)
        int_validator = QIntValidator(0, 4096)
        int_validator.setLocale(locale)
        double_validator = QDoubleValidator(0.0, 10.0, 10)
        double_validator.setLocale(locale)

        layout_main = QVBoxLayout()
        self.setLayout(layout_main)

        label_res = QLabel("Rasterization")
        label_res.setStyleSheet(
            """QLabel {
                font-size: 12pt;
                font-weight: bold;
                padding-bottom: 0.5em;
            }"""
        )

        # Options
        self.image_width_widget = SimpleInputField("512", 60, int_validator)
        self.image_height_widget = SimpleInputField("512", 60, int_validator)
        self.scale_widget = SimpleInputField("1.0", 60, double_validator)
        self.background_color_widget = ColorPicker(np.zeros(3))

        option_widget = QGroupBox("Dimensions")
        layout_options = QFormLayout(option_widget)
        layout_options.addRow("Image width:", self.image_width_widget)
        layout_options.addRow("Image height:", self.image_height_widget)
        layout_options.addRow("Scale:", self.scale_widget)
        layout_options.addRow("Background color:", self.background_color_widget)

        bt_rasterize = CustomPushButton("Rasterize", 90)
        bt_rasterize.connect_to_clicked(self.button_clicked)

        widget_fov_group_box = QGroupBox("FOV")
        layout_group_box = QFormLayout(widget_fov_group_box)

        # Create radio button group
        widget_radio_group = QWidget()
        layout_radio = QHBoxLayout(widget_radio_group)
        self.button_group = QButtonGroup(self)
        self.button_group.addButton(QRadioButton("Default"), id=0)
        self.button_group.addButton(QRadioButton("Field of View"), id=1)
        self.button_group.addButton(QRadioButton("Focal Length"), id=2)
        self.button_group.button(0).setChecked(True)
        self.button_group.idToggled.connect(self.fov_source_changed)
        for button in self.button_group.buttons():
            layout_radio.addWidget(button)

        self.fov_widget = SimpleInputField("0.0", 40, validator=double_validator)
        self.fov_widget.setEnabled(False)

        layout_group_box.addRow(widget_radio_group)
        layout_group_box.addRow("FOV/FX:", self.fov_widget)

        layout_main.addWidget(label_res)
        layout_main.addWidget(option_widget)
        layout_main.addWidget(widget_fov_group_box)
        layout_main.addWidget(bt_rasterize)
        layout_main.addStretch()

    def button_clicked(self):
        width = int(self.image_width_widget.text())
        height = int(self.image_height_widget.text())
        scale = float(self.scale_widget.text())
        color = np.asarray(self.background_color_widget.color_debug)
        value = float(self.fov_widget.lineedit.text())
        intrinsics = graphic_util.get_camera_intrinsics(width, height, value, self.button_group.checkedId())
        self.signal_rasterize.emit(width, height, scale, color, intrinsics)

    def fov_source_changed(self, button_id, checked):
        self.fov_widget.setEnabled(button_id != 0 and checked)

    def scale_enable(self, value):
        if value is False:
            self.scale_widget.setText(str("1.0"))

        self.scale_widget.setEnabled(value)
