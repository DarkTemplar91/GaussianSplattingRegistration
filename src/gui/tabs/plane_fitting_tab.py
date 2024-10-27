from PySide6.QtCore import Signal
from PySide6.QtGui import QIntValidator, QDoubleValidator
from PySide6.QtGui import QIntValidator, QDoubleValidator
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGroupBox, QFormLayout

from src.gui.widgets.custom_push_button import CustomPushButton
from src.gui.widgets.simple_input_field_widget import SimpleInputField


class PlaneFittingTab(QWidget):
    signal_fit_plane = Signal(int, float, float)

    def __init__(self):
        super().__init__()
        double_validator = QDoubleValidator(0.0, 9999.0, 10)
        int_validator = QIntValidator(0, 100000)
        layout_main = QVBoxLayout(self)

        label_res = QLabel("Plane fitting")
        label_res.setStyleSheet(
            """QLabel {
                font-size: 12pt;
                font-weight: bold;
                padding-bottom: 0.5em;
            }"""
        )

        # Plane fitting options
        self.iterations_widget = SimpleInputField("1000", 60, int_validator)
        self.threshold_widget = SimpleInputField("0.01", 60, double_validator)
        self.min_distance_widget = SimpleInputField("0.05", 60, double_validator)
        bt_fit_plane = CustomPushButton("Fit plane", 90)
        bt_fit_plane.connect_to_clicked(self.fit_plane_pressed)

        plane_fitting_box = QGroupBox("Plane fitting")
        layout_plane_fitting = QFormLayout(plane_fitting_box)
        layout_plane_fitting.addRow("Max iterations:", self.iterations_widget)
        layout_plane_fitting.addRow("Distance threshold:", self.threshold_widget)
        layout_plane_fitting.addRow("Min sample distance:", self.min_distance_widget)
        layout_plane_fitting.addRow(bt_fit_plane)

        layout_main.addWidget(label_res)
        layout_main.addWidget(plane_fitting_box)
        layout_main.addStretch()

    def fit_plane_pressed(self):
        iteration = int(self.iterations_widget.text())
        threshold = float(self.threshold_widget.text())
        min_distance = float(self.min_distance_widget.text())
        self.signal_fit_plane.emit(iteration, threshold, min_distance)
