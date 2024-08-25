from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QSizePolicy, QCheckBox, QErrorMessage, \
    QFileDialog, QGroupBox, QFormLayout, QHBoxLayout

from src.gui.widgets.custom_push_button import CustomPushButton
from src.gui.widgets.file_selector_widget import FileSelector
import src.utils.graphics_utils as graphic_util


class MergeTab(QWidget):
    signal_merge_point_clouds = QtCore.Signal(bool, str, str, str)

    def __init__(self, merge_path="", input_path=""):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        label_title = QLabel("Point cloud merging")
        label_title.setStyleSheet(
            """QLabel {
                font-size: 12pt;
                font-weight: bold;
                padding-bottom: 0.5em;
            }"""
        )

        group_box_widget = QGroupBox()
        layout_group_box = QVBoxLayout(group_box_widget)

        form_widget = QWidget()
        layout_form = QFormLayout(form_widget)

        self.input_checkbox = QCheckBox()
        self.input_checkbox.setText("Use corresponding inputs")
        self.input_checkbox.setStyleSheet(
            "QCheckBox::indicator {"
            "    width: 20px;"
            "    height: 20px;"
            "}"
            "QCheckBox::indicator::text {"
            "    padding-left: 0.5em;"
            "}"
        )
        self.input_checkbox.stateChanged.connect(self.checkbox_changed)

        self.fs_input1 = FileSelector(input_path)
        self.fs_input2 = FileSelector(input_path)
        self.fs_input1.setEnabled(False)
        self.fs_input2.setEnabled(False)
        layout_form.addRow("First point cloud:", self.fs_input1)
        layout_form.addRow("Second point cloud:", self.fs_input2)

        layout_group_box.addWidget(self.input_checkbox)
        layout_group_box.addWidget(form_widget)

        widget_save = QWidget()
        layout_save = QHBoxLayout(widget_save)
        label_save = QLabel("Save path:")
        self.fs_merge = FileSelector(base_path=merge_path,
                                     file_type=QFileDialog.FileMode.AnyFile)
        layout_save.addWidget(label_save)
        layout_save.addWidget(self.fs_merge)
        bt_merge = CustomPushButton("Merge point clouds", 90)
        bt_merge.connect_to_clicked(self.merge_point_clouds)

        layout.addWidget(label_title)
        layout.addWidget(group_box_widget)
        layout.addWidget(widget_save)
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
