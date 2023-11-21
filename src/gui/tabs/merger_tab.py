from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QSizePolicy, QCheckBox, QErrorMessage

from src.gui.widgets.file_selector_widget import FileSelector
import src.utils.graphics_utils as graphic_util


class MergeTab(QWidget):
    signal_merge_point_clouds = QtCore.pyqtSignal(bool, str, str, str)

    def __init__(self, merge_path="", input_path=""):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        label_title = QLabel("Point cloud merging")
        label_title.setStyleSheet(
            "QLabel {"
            "   font-size: 11pt;"
            "    font-weight: bold;"
            f"    padding: {int(graphic_util.SIZE_SCALE_X * 8)}px;"
            "}"
        )

        self.input_checkbox = QCheckBox()
        self.input_checkbox.setText("Use corresponding inputs")
        self.input_checkbox.setStyleSheet(
            "QCheckBox::indicator {"
            f"    width: {int(graphic_util.SIZE_SCALE_X * 20)}px;"
            f"    height: {int(graphic_util.SIZE_SCALE_Y * 20)}px;"
            "}"
            "QCheckBox::indicator::text {"
            f"    padding-left: {int(graphic_util.SIZE_SCALE_X * 10)}px;"
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

        self.fs_merge = FileSelector(text="Save path:", base_path=merge_path, label_width=70)
        bt_merge = QPushButton("Merge point clouds")
        bt_merge.setStyleSheet(f"padding-left: 10px; padding-right: {int(graphic_util.SIZE_SCALE_X * 10)}px;"
                               f"padding-top: 2px; padding-bottom: {int(graphic_util.SIZE_SCALE_X * 2)}px;")
        bt_merge.setFixedSize(int(280 * graphic_util.SIZE_SCALE_X), int(30 * graphic_util.SIZE_SCALE_Y))
        bt_merge.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        bt_merge.clicked.connect(self.merge_point_clouds)

        layout.addWidget(label_title)
        layout.addWidget(self.input_checkbox)
        layout.addWidget(widget_input)
        layout.addWidget(self.fs_merge)
        layout.addWidget(bt_merge, alignment=Qt.AlignCenter)
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
        if not self.fs_merge.file_path:
            dialog = QErrorMessage(self)
            dialog.setModal(True)
            dialog.setWindowTitle("Error")
            dialog.showMessage("Please select location to save the merged point cloud!")
            return

        is_checked = self.input_checkbox.isChecked()
        pc_path1 = self.fs_input1.file_path
        pc_path2 = self.fs_input2.file_path
        merge_path = self.fs_merge.file_path
        self.signal_merge_point_clouds.emit(is_checked, pc_path1, pc_path2, merge_path)
