from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QSizePolicy, QCheckBox

from src.gui.widgets.file_selector_widget import FileSelector


class MergerWidget(QWidget):
    signal_merge_point_clouds = QtCore.pyqtSignal(bool, str, str, str)

    def __init__(self, merge_path="", input_path=""):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        label_title = QLabel("Point cloud merging")
        label_title.setStyleSheet(
            "QLabel {"
            "    font-size: 14px;"
            "    font-weight: bold;"
            "    padding: 8px;"
            "}"
        )

        self.input_checkbox = QCheckBox()
        self.input_checkbox.setText("Use corresponding inputs")
        self.input_checkbox.setStyleSheet(
            "QCheckBox::indicator {"
            "    width: 20px;"
            "    height: 20px;"
            "}"
            "QCheckBox::indicator::text {"
            "    padding-left: 10px;"
            "}"
        )
        self.input_checkbox.stateChanged.connect(self.checkbox_changed)

        self.fs_input1 = FileSelector(text="First point cloud:", base_path=input_path)
        self.fs_input2 = FileSelector(text="Second point cloud:", base_path=input_path)
        self.fs_input1.setEnabled(False)
        self.fs_input2.setEnabled(False)

        layout_input = QVBoxLayout()
        widget_input = QWidget()
        widget_input.setLayout(layout_input)
        layout_input.addWidget(self.fs_input1)
        layout_input.addWidget(self.fs_input2)

        self.fs_merge = FileSelector(text="Save path:", base_path=merge_path)
        bt_merge = QPushButton("Merge point clouds")
        bt_merge.setStyleSheet("padding-left: 10px; padding-right: 10px;"
                               "padding-top: 2px; padding-bottom: 2px;")
        bt_merge.setFixedSize(250, 30)
        bt_merge.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        bt_merge.clicked.connect(self.merge_point_clouds)

        layout.addWidget(label_title)
        layout.addWidget(self.input_checkbox)
        layout.addWidget(widget_input)
        layout.addWidget(self.fs_merge)
        layout.addWidget(bt_merge)
        layout.addStretch()

    def checkbox_changed(self, state):
        self.fs_input1.setEnabled(state)
        self.fs_input2.setEnabled(state)
        if state:
            return

        self.fs_input1.inputField.setText("")
        self.fs_input1.file_path = ""

        self.fs_input2.inputField.setText("")
        self.fs_input2.file_path = ""

    def merge_point_clouds(self):
        is_checked = self.input_checkbox.isChecked()
        pc_path1 = self.fs_input1.file_path
        pc_path2 = self.fs_input2.file_path
        merge_path = self.fs_merge.file_path
        self.signal_merge_point_clouds.emit(is_checked, pc_path1, pc_path2, merge_path)
