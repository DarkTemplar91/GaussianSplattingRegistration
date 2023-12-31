import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import QLocale, Qt
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QWidget, QLabel, QCheckBox, QPushButton, QVBoxLayout, QSizePolicy, QStyle, QHBoxLayout

from src.gui.widgets.color_picker_widget import ColorPicker
from src.gui.widgets.registration_input_field_widget import SimpleInputField
from src.gui.widgets.vector_widget import VectorWidget
import src.utils.graphics_utils as graphic_util


class VisualizerTab(QWidget):
    signal_change_vis = QtCore.pyqtSignal(bool, np.ndarray, np.ndarray, float, np.ndarray, np.ndarray, np.ndarray)
    signal_get_current_view = QtCore.pyqtSignal()
    signal_pop_visualizer = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        locale = QLocale(QLocale.English)
        double_validator = QDoubleValidator()
        double_validator.setLocale(locale)
        double_validator.setRange(-9999.0, 9999.0)
        double_validator.setDecimals(10)

        label_widget = QWidget()
        label_layout = QHBoxLayout(label_widget)
        label_title = QLabel("Visualization")
        label_title.setStyleSheet(
            "QLabel {"
            "    font-size: 11pt;"
            "    font-weight: bold;"
            f"    padding: {int(graphic_util.SIZE_SCALE_X * 8)}px;"
            "}"
        )

        self.pop_button = QPushButton(self)
        self.pop_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.pop_button.setFixedSize(int(graphic_util.SIZE_SCALE_X * 20), int(graphic_util.SIZE_SCALE_Y * 20))
        icon = self.style().standardIcon(QStyle.SP_TitleBarNormalButton)
        self.pop_button.setIcon(icon)

        label_layout.addWidget(label_title)
        label_layout.addWidget(self.pop_button)

        self.pop_button.clicked.connect(self.pop_visualizer)

        self.debug_color_checkbox = QCheckBox()
        self.debug_color_checkbox.setText("Use debug colors")
        self.debug_color_checkbox.setStyleSheet(
            "QCheckBox::indicator {"
            f"    width: {int(graphic_util.SIZE_SCALE_X * 20)}px;"
            f"    height: {int(graphic_util.SIZE_SCALE_Y * 20)}px;"
            "}"
            "QCheckBox::indicator::text {"
            f"    padding-left: {int(graphic_util.SIZE_SCALE_X * 10)}px;"
            "}"
        )
        self.debug_color_checkbox.stateChanged.connect(self.checkbox_changed)

        self.debug_color_dialog_first = ColorPicker("Primary debug color: ")
        self.debug_color_dialog_first.setEnabled(False)
        self.debug_color_dialog_second = ColorPicker("Secondary debug color: ")
        self.debug_color_dialog_second.setEnabled(False)

        self.zoom_widget = SimpleInputField("Zoom: ", "1.0", 50, 60, validator=double_validator)

        button_apply = QPushButton()
        button_apply.setFixedSize(int(250 * graphic_util.SIZE_SCALE_X), int(30 * graphic_util.SIZE_SCALE_Y))
        button_apply.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button_apply.setText("Apply")
        button_apply.clicked.connect(self.apply_to_vis)

        button_copy = QPushButton()
        button_copy.setFixedSize(int(250 * graphic_util.SIZE_SCALE_X), int(30 * graphic_util.SIZE_SCALE_Y))
        button_copy.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button_copy.setText("Copy current view")
        button_copy.clicked.connect(self.get_current_view)

        self.front_widget = VectorWidget("Front: ", 3, [0, 0, -1], double_validator)
        self.lookat_widget = VectorWidget("Look at: ", 3, [0, 0, 0], double_validator)
        self.up_widget = VectorWidget("Up: ", 3, [0, 1, 0], double_validator)

        layout.addWidget(label_widget)
        layout.addWidget(self.debug_color_checkbox)
        layout.addWidget(self.debug_color_dialog_first)
        layout.addWidget(self.debug_color_dialog_second)
        layout.addWidget(self.zoom_widget)
        layout.addWidget(self.front_widget)
        layout.addWidget(self.lookat_widget)
        layout.addWidget(self.up_widget)
        layout.addWidget(button_apply, alignment=Qt.AlignCenter)
        layout.addWidget(button_copy, alignment=Qt.AlignCenter)
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
        return (float(
            self.zoom_widget.lineedit.text()), self.front_widget.values,
                self.lookat_widget.values, self.up_widget.values)

    def pop_visualizer(self):
        self.signal_pop_visualizer.emit()
