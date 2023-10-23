from PyQt5.QtWidgets import QWidget, QLabel, QCheckBox, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QSizePolicy

from gui.color_picker_widget import ColorPicker
from gui.vector_widget import VectorWidget


class VisualizerWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

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

        self.debug_color_dialog_first = ColorPicker("Primary debug color: ")
        self.debug_color_dialog_second = ColorPicker("Secondary debug color: ")

        # TODO: camera stuff

        layout_zoom = QHBoxLayout()
        zoom_widget = QWidget()
        zoom_widget.setLayout(layout_zoom)
        zoom_label = QLabel("Zoom: ")
        zoom_label.setFixedWidth(50)
        zoom_lineedit = QLineEdit("0.0")
        zoom_lineedit.setFixedWidth(60)
        layout_zoom.addWidget(zoom_label)
        layout_zoom.addWidget(zoom_lineedit)
        layout_zoom.addStretch()

        button_apply = QPushButton()
        button_apply.setFixedSize(250, 30)
        button_apply.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button_apply.setText("Apply")

        layout.addWidget(label_title)
        layout.addWidget(self.debug_color_checkbox)
        layout.addWidget(self.debug_color_dialog_first)
        layout.addWidget(self.debug_color_dialog_second)
        layout.addWidget(zoom_widget)
        layout.addWidget(VectorWidget("Front: "))
        layout.addWidget(VectorWidget("Look at: "))
        layout.addWidget(VectorWidget("Up: "))
        layout.addWidget(button_apply)
        layout.addStretch()

