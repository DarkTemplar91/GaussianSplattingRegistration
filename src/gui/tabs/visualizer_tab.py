import numpy as np
from PySide6 import QtCore
from PySide6.QtCore import QLocale, Qt
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import QWidget, QLabel, QCheckBox, QPushButton, QVBoxLayout, QSizePolicy, QStyle, QHBoxLayout, \
    QFormLayout, QGroupBox

from src.gui.widgets.centered_push_button import CustomPushButton
from src.gui.widgets.color_picker_widget import ColorPicker
from src.gui.widgets.simple_input_field_widget import SimpleInputField
from src.gui.widgets.vector_widget import VectorWidget
import src.utils.graphics_utils as graphic_util


class VisualizerTab(QWidget):
    signal_change_vis = QtCore.Signal(float, np.ndarray, np.ndarray, np.ndarray,
                                      object, object)
    signal_get_current_view = QtCore.Signal()
    signal_pop_visualizer = QtCore.Signal()

    # TODO: Consider not using QGroupBox
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        locale = QLocale(QLocale.Language.C)
        double_validator = QDoubleValidator()
        double_validator.setLocale(locale)
        double_validator.setRange(-9999.0, 9999.0)
        double_validator.setDecimals(10)

        label_title = QLabel("Visualization")
        label_title.setStyleSheet(
            """QLabel {
                font-size: 12pt;
                font-weight: bold;
                padding-bottom: 0.5em;
            }"""
        )

        #self.pop_button = QPushButton(self)
        #self.pop_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        #self.pop_button.setFixedSize(20, 20)
        #icon = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarNormalButton)
        #self.pop_button.setIcon(icon)

        #label_layout.addWidget(label_title)
        #label_layout.addWidget(self.pop_button)

        #self.pop_button.clicked.connect(self.pop_visualizer)

        color_group_widget = QGroupBox("Color")
        layout_group_box_color = QVBoxLayout(color_group_widget)

        self.debug_color_checkbox = QCheckBox()
        self.debug_color_checkbox.setText("Use debug colors")
        self.debug_color_checkbox.setStyleSheet(
            "QCheckBox::indicator {"
            "    width: 20px;"
            "    height: 20px;"
            "}"
            "QCheckBox::indicator::text {"
            f"    padding-left: 0.5em;"
            "}"
        )
        self.debug_color_checkbox.stateChanged.connect(self.checkbox_changed)

        form_widget_color = QWidget()
        layout_form_color = QFormLayout(form_widget_color)
        self.debug_color_dialog_first = ColorPicker()
        self.debug_color_dialog_first.setEnabled(False)
        self.debug_color_dialog_second = ColorPicker()
        self.debug_color_dialog_second.setEnabled(False)
        layout_form_color.addRow("Primary debug color:", self.debug_color_dialog_first)
        layout_form_color.addRow("Secondary debug color:", self.debug_color_dialog_second)
        layout_group_box_color.addWidget(self.debug_color_checkbox)
        layout_group_box_color.addWidget(form_widget_color)

        view_group_widget = QGroupBox("View")
        layout_group_box_view = QVBoxLayout(view_group_widget)
        form_widget_view = QWidget()
        layout_form_view = QFormLayout(form_widget_view)
        self.zoom_widget = SimpleInputField("1.0", 60, validator=double_validator)
        self.front_widget = VectorWidget(3, [0, 0, -1], double_validator)
        self.lookat_widget = VectorWidget(3, [0, 0, 0], double_validator)
        self.up_widget = VectorWidget(3, [0, 1, 0], double_validator)
        layout_form_view.addRow("Zoom:", self.zoom_widget)
        layout_form_view.addRow("Front:", self.front_widget)
        layout_form_view.addRow("Look at:", self.lookat_widget)
        layout_form_view.addRow("Up:", self.up_widget)
        layout_group_box_view.addWidget(form_widget_view)

        button_apply = CustomPushButton("Apply", 90)
        button_apply.connect_to_clicked(self.apply_to_vis)
        button_copy = CustomPushButton("Copy current view", 90)
        button_copy.connect_to_clicked(self.get_current_view)

        layout.addWidget(label_title)
        layout.addWidget(color_group_widget)
        layout.addWidget(view_group_widget)
        layout.addWidget(button_apply)
        layout.addWidget(button_copy)

    def checkbox_changed(self, state):
        self.debug_color_dialog_first.setEnabled(state)
        self.debug_color_dialog_second.setEnabled(state)

    def apply_to_vis(self):
        use_debug_color = self.get_use_debug_color()
        dc1 = dc2 = None
        if use_debug_color:
            dc1 = np.asarray(self.debug_color_dialog_first.color_debug)
            dc2 = np.asarray(self.debug_color_dialog_second.color_debug)

        self.signal_change_vis.emit(float(self.zoom_widget.lineedit.text()),
                                    self.front_widget.values, self.lookat_widget.values, self.up_widget.values,
                                    dc1, dc2)

    def get_current_view(self):
        self.signal_get_current_view.emit()

    def set_visualizer_attributes(self, zoom, front, lookat, up):
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
