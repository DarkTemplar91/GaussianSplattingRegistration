import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import QLocale
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QWidget, QLabel, QCheckBox, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QSizePolicy

from src.gui.widgets.color_picker_widget import ColorPicker
from src.gui.widgets.registration_input_field_widget import SimpleInputField
from src.gui.widgets.vector_widget import VectorWidget


class VisualizerTab(QWidget):
    signal_change_vis = QtCore.pyqtSignal(bool, np.ndarray, np.ndarray, float, np.ndarray, np.ndarray, np.ndarray)
    signal_get_current_view = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        locale = QLocale(QLocale.English)
        double_validator = QDoubleValidator()
        double_validator.setLocale(locale)
        double_validator.setRange(-9999.0, 9999.0)
        double_validator.setDecimals(10)

        label_title = QLabel("Visualization")
        label_title.setStyleSheet(
            "QLabel {"
            "    font-size: 14px;"
            "    font-weight: bold;"
            "    padding: 8px;"
            "}"
        )
        self.debug_color_checkbox = QCheckBox()
        self.debug_color_checkbox.setText("Use debug colors")
        self.debug_color_checkbox.setStyleSheet(
            "QCheckBox::indicator {"
            "    width: 20px;"
            "    height: 20px;"
            "}"
            "QCheckBox::indicator::text {"
            "    padding-left: 10px;"
            "}"
        )
        self.debug_color_checkbox.stateChanged.connect(self.checkbox_changed)

        self.debug_color_dialog_first = ColorPicker("Primary debug color: ")
        self.debug_color_dialog_first.setEnabled(False)
        self.debug_color_dialog_second = ColorPicker("Secondary debug color: ")
        self.debug_color_dialog_second.setEnabled(False)

        self.zoom_widget = SimpleInputField("Zoom: ", "1.0", 50, 60, validator=double_validator)

        button_apply = QPushButton()
        button_apply.setFixedSize(250, 30)
        button_apply.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button_apply.setText("Apply")
        button_apply.clicked.connect(self.apply_to_vis)

        button_copy = QPushButton()
        button_copy.setFixedSize(250, 30)
        button_copy.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button_copy.setText("Copy current view")
        button_copy.clicked.connect(self.get_current_view)

        self.front_widget = VectorWidget("Front: ", 3, [0, 0, -1], double_validator)
        self.lookat_widget = VectorWidget("Look at: ", 3, [0, 0, 0], double_validator)
        self.up_widget = VectorWidget("Up: ", 3, [0, 1, 0], double_validator)

        layout.addWidget(label_title)
        layout.addWidget(self.debug_color_checkbox)
        layout.addWidget(self.debug_color_dialog_first)
        layout.addWidget(self.debug_color_dialog_second)
        layout.addWidget(self.zoom_widget)
        layout.addWidget(self.front_widget)
        layout.addWidget(self.lookat_widget)
        layout.addWidget(self.up_widget)
        layout.addWidget(button_apply)
        layout.addWidget(button_copy)
        layout.addStretch()

    def checkbox_changed(self, state):
        self.debug_color_dialog_first.setEnabled(state)
        self.debug_color_dialog_second.setEnabled(state)

    def apply_to_vis(self):
        use_debug_color = self.debug_color_checkbox.isChecked()
        self.signal_change_vis.emit(use_debug_color, np.asarray(self.debug_color_dialog_first.color_debug),
                                    np.asarray(self.debug_color_dialog_second.color_debug),
                                    float(self.zoom_widget.lineedit.text()),
                                    self.front_widget.values, self.lookat_widget.values, self.up_widget.values)

    def get_current_view(self):
        self.signal_get_current_view.emit()

    def assign_new_values(self, zoom, front, lookat, up):
        self.zoom_widget.lineedit.setText(str(zoom))
        self.zoom_widget.lineedit.setCursorPosition(0)
        self.front_widget.set_values(front)
        self.lookat_widget.set_values(lookat)
        self.up_widget.set_values(up)

    def get_use_debug_color(self):
        return self.debug_color_checkbox.isChecked()

    def get_debug_colors(self):
        return np.asarray(self.debug_color_dialog_first.color_debug), np.asarray(
            self.debug_color_dialog_second.color_debug)

    def get_current_transformations(self):
        return float(
            self.zoom_widget.lineedit.text()), self.front_widget.values, self.lookat_widget.values, self.up_widget.values
