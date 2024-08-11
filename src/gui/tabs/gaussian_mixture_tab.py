from PyQt5 import QtCore
from PyQt5.QtCore import QLocale, Qt
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QPushButton, QSizePolicy, QSlider, QLabel

from src.gui.widgets.simple_input_field_widget import SimpleInputField
import src.utils.graphics_utils as graphic_util


class GaussianMixtureTab(QWidget):
    signal_create_mixture = QtCore.pyqtSignal(float, float, float, int)
    signal_slider_changed = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()

        locale = QLocale(QLocale.English)
        double_validator = QDoubleValidator()
        double_validator.setLocale(locale)
        double_validator.setRange(0.0, 9999.0)
        double_validator.setDecimals(10)

        int_validator = QIntValidator()
        int_validator.setLocale(locale)
        int_validator.setRange(0, 10)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.hem_reduction_field = SimpleInputField("HEM reduction factor:", "3.0", validator=double_validator)
        self.distance_field = SimpleInputField("Geometric distance delta:", "3.0", validator=double_validator)
        self.color_field = SimpleInputField("Color distance delta:", "2.5", validator=double_validator)
        self.cluster_level_field = SimpleInputField("Cluster level:", "3", validator=int_validator)

        slider_label = QLabel("Current mixture level")
        slider_label.setStyleSheet(
            "QLabel {"
            "    font-size: 11pt;"
            "    font-weight: bold;"
            f"   padding: {int(graphic_util.SIZE_SCALE_X * 8)}px;"
            "}"
        )

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(0)
        self.slider.setTickInterval(1)
        self.slider.setEnabled(False)
        self.slider.valueChanged.connect(self.value_changed)

        option_widget = QGroupBox()
        option_widget.setTitle("Inputs")
        options_layout = QVBoxLayout()
        option_widget.setLayout(options_layout)

        options_layout.addWidget(self.hem_reduction_field)
        options_layout.addWidget(self.distance_field)
        options_layout.addWidget(self.color_field)
        options_layout.addWidget(self.cluster_level_field)
        options_layout.addStretch()

        bt_apply = QPushButton("Execute")
        bt_apply.setStyleSheet(f"padding-left: 10px; padding-right: {int(graphic_util.SIZE_SCALE_X * 10)}px;"
                               f"padding-top: 2px; padding-bottom: {int(graphic_util.SIZE_SCALE_X * 2)}px;")
        bt_apply.setFixedHeight(int(30 * graphic_util.SIZE_SCALE_Y))
        bt_apply.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout.addWidget(slider_label)
        layout.addWidget(self.slider)
        layout.addSpacing(int(graphic_util.SIZE_SCALE_Y * 20))
        layout.addWidget(option_widget)
        layout.addWidget(bt_apply)

        bt_apply.clicked.connect(self.hem_execute_button_pressed)

    def hem_execute_button_pressed(self):
        hem_reduction = float(self.hem_reduction_field.lineedit.text())
        distance_delta = float(self.distance_field.lineedit.text())
        color_delta = float(self.color_field.lineedit.text())
        cluster_level = int(self.cluster_level_field.lineedit.text())

        self.signal_create_mixture.emit(hem_reduction, distance_delta, color_delta, cluster_level)

    def set_slider_range(self, value):
        self.slider.setRange(0, value)

    def set_slider_enabled(self, value):
        self.slider.setEnabled(value)

    def set_slider_to(self, value):
        self.slider.setValue(value)

    def value_changed(self):
        if not self.slider.isEnabled():
            return

        value = self.slider.value()
        self.signal_slider_changed.emit(value)
