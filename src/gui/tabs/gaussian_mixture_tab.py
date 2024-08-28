from PySide6.QtCore import QLocale, Qt, Signal
from PySide6.QtGui import QDoubleValidator, QIntValidator
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QPushButton, QSizePolicy, QSlider, QLabel, QFormLayout

from src.gui.widgets.custom_push_button import CustomPushButton
from src.gui.widgets.simple_input_field_widget import SimpleInputField
import src.utils.graphics_utils as graphic_util


class GaussianMixtureTab(QWidget):
    signal_create_mixture = Signal(float, float, float, int)
    signal_slider_changed = Signal(int)

    def __init__(self):
        super().__init__()

        locale = QLocale(QLocale.Language.C)
        double_validator = QDoubleValidator()
        double_validator.setLocale(locale)
        double_validator.setRange(0.0, 9999.0)
        double_validator.setDecimals(10)

        int_validator = QIntValidator()
        int_validator.setLocale(locale)
        int_validator.setRange(0, 10)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.hem_reduction_field = SimpleInputField("3.0", validator=double_validator)
        self.distance_field = SimpleInputField("3.0", validator=double_validator)
        self.color_field = SimpleInputField("2.5", validator=double_validator)
        self.cluster_level_field = SimpleInputField("3", validator=int_validator)

        slider_label = QLabel("Current mixture level")
        slider_label.setStyleSheet(
            "QLabel {"
            "    font-size: 11pt;"
            "    font-weight: bold;"
            f"   padding: 8px;"
            "}"
        )

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(0)
        self.slider.setTickInterval(1)
        self.slider.setEnabled(False)
        self.slider.valueChanged.connect(self.value_changed)

        widget_options = QGroupBox("Inputs")
        layout_options = QFormLayout(widget_options)

        layout_options.addRow("HEM reduction factor:", self.hem_reduction_field)
        layout_options.addRow("Geometric distance delta:", self.distance_field)
        layout_options.addRow("Color distance delta:", self.color_field)
        layout_options.addRow("Cluster level:", self.cluster_level_field)

        bt_apply = CustomPushButton("Execute", 100)

        layout.addWidget(slider_label)
        layout.addWidget(self.slider)
        layout.addSpacing(20)
        layout.addWidget(widget_options)
        layout.addWidget(bt_apply)

        bt_apply.connect_to_clicked(self.hem_execute_button_pressed)

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
