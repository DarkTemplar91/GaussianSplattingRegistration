import numpy as np
from PySide6 import QtCore
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QFormLayout, QGroupBox, QPushButton, QSizePolicy, \
    QStyle, QHBoxLayout, QCheckBox

from src.gui.widgets.color_picker_widget import ColorPicker
from src.gui.widgets.custom_push_button import CustomPushButton
from src.gui.widgets.simple_input_field_widget import SimpleInputField
from src.gui.widgets.vector_widget import VectorWidget


class VisualizerTab(QWidget):
    class CameraView:
        def __init__(self, zoom, front, lookat, up):
            self.zoom = zoom
            self.front = front
            self.lookat = lookat
            self.up = up

    signal_change_vis_settings_o3d = QtCore.Signal(CameraView,
                                                   object, object)

    signal_change_vis_settings_3dgs = QtCore.Signal(CameraView, object)

    signal_change_type = QtCore.Signal(int)
    signal_get_current_view = QtCore.Signal()
    signal_pop_visualizer = QtCore.Signal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        double_validator = QDoubleValidator(-9999.0, 9999.0, 10)

        label_title = QLabel("Visualization")
        label_title.setStyleSheet(
            """QLabel {
                font-size: 12pt;
                font-weight: bold;
                padding-bottom: 0.5em;
            }"""
        )

        self.checkbox = QCheckBox()
        self.checkbox.setText("Use GSPLAT")
        self.checkbox.toggled.connect(self.change_visualizer)

        titled_label_widget = QWidget()
        label_layout = QHBoxLayout(titled_label_widget)
        label_layout.setContentsMargins(0, 0, 0, 0)
        label_layout.setSpacing(0)

        self.pop_button = QPushButton(self)
        self.pop_button.setCheckable(True)
        self.pop_button.setChecked(False)
        self.pop_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.pop_button.setFixedSize(20, 20)
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarNormalButton)
        self.pop_button.setIcon(icon)

        label_layout.addWidget(label_title)
        label_layout.addWidget(self.pop_button)

        self.pop_button.clicked.connect(self.pop_visualizer)

        self.form_widget_color = QGroupBox("Debug color")
        self.form_widget_color.setCheckable(True)
        self.form_widget_color.setChecked(False)
        layout_form_color = QFormLayout(self.form_widget_color)

        self.debug_color_dialog_first = ColorPicker()
        self.debug_color_dialog_second = ColorPicker()
        layout_form_color.addRow("Primary debug color:", self.debug_color_dialog_first)
        layout_form_color.addRow("Secondary debug color:", self.debug_color_dialog_second)

        view_group_widget = QGroupBox("View")
        layout_form_view = QFormLayout(view_group_widget)
        self.zoom_widget = SimpleInputField("1.0", 60, validator=double_validator)
        zoom_layout = self.zoom_widget.layout()
        margin = zoom_layout.getContentsMargins()
        zoom_layout.setContentsMargins(margin[0], 0, margin[2], 0)
        self.front_widget = VectorWidget(3, [0.0, 0.0, -1.0], double_validator)
        self.lookat_widget = VectorWidget(3, [0.0, 0.0, 0.0], double_validator)
        self.up_widget = VectorWidget(3, [0.0, 1.0, 0.0], double_validator)
        layout_form_view.addRow("Zoom:", self.zoom_widget)
        layout_form_view.addRow("Front:", self.front_widget)
        layout_form_view.addRow("Look at:", self.lookat_widget)
        layout_form_view.addRow("Up:", self.up_widget)

        button_apply = CustomPushButton("Apply", 90)
        button_apply.connect_to_clicked(self.apply_to_vis)
        button_copy = CustomPushButton("Copy current view", 90)
        button_copy.connect_to_clicked(self.get_current_view)

        layout.addWidget(titled_label_widget)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.form_widget_color)
        layout.addWidget(view_group_widget)
        layout.addWidget(button_apply)
        layout.addWidget(button_copy)
        layout.addStretch()

    def apply_to_vis(self):
        if not self.checkbox.isChecked():
            use_debug_color = self.get_use_debug_color()
            dc1 = dc2 = None
            if use_debug_color:
                dc1 = np.asarray(self.debug_color_dialog_first.color_debug)
                dc2 = np.asarray(self.debug_color_dialog_second.color_debug)

            self.signal_change_vis_settings_o3d.emit(self.get_current_transformations(), dc1, dc2)
            return

        self.signal_change_vis_settings_3dgs.emit(self.get_current_transformations(), np.zeros(3))

    def get_current_view(self):
        self.signal_get_current_view.emit()

    def set_visualizer_attributes(self, zoom, front, lookat, up):
        self.zoom_widget.lineedit.setText(str(zoom))
        self.zoom_widget.lineedit.setCursorPosition(0)
        self.front_widget.set_values(front)
        self.lookat_widget.set_values(lookat)
        self.up_widget.set_values(up)

    def get_use_debug_color(self):
        return self.form_widget_color.isChecked()

    def get_debug_colors(self):
        return np.asarray(self.debug_color_dialog_first.color_debug), np.asarray(
            self.debug_color_dialog_second.color_debug)

    def get_current_transformations(self):
        return VisualizerTab.CameraView(float(
            self.zoom_widget.lineedit.text()), self.front_widget.values,
                self.lookat_widget.values, self.up_widget.values)

    def pop_visualizer(self):
        self.signal_pop_visualizer.emit()

    def change_visualizer(self, visualizer_index):
        self.signal_change_type.emit(visualizer_index)
