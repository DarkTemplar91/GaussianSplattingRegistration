from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QGroupBox, QFormLayout
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

from src.gui.widgets.custom_push_button import CustomPushButton
from src.gui.widgets.file_selector_widget import FileSelector


class InputTab(QWidget):
    signal_load_sparse = Signal(str, str)
    signal_load_gaussian = Signal(str, str)

    result_signal = Signal(object, object, bool, object, object)

    def __init__(self, input_dir):
        super().__init__()
        self.progress_dialog = None
        layout_main = QVBoxLayout(self)

        label_io = QLabel("Input and output")
        label_io.setStyleSheet(
            """QLabel {
                font-size: 12pt;
                font-weight: bold;
                padding-bottom: 0.5em;
            }"""
        )

        sparse_group_widget = QGroupBox("Sparse inputs")
        layout_sparse_group = QVBoxLayout(sparse_group_widget)
        widget_sparse = QWidget()
        layout_sparse_form = QFormLayout(widget_sparse)
        self.fs_input1 = FileSelector(input_dir)
        self.fs_input2 = FileSelector(input_dir)
        bt_sparse = CustomPushButton("Import sparse point cloud", 90)
        layout_sparse_form.addRow("First sparse input:", self.fs_input1)
        layout_sparse_form.addRow("Second sparse input:", self.fs_input2)
        layout_sparse_group.addWidget(widget_sparse)
        layout_sparse_group.addWidget(bt_sparse)

        input_group_widget = QGroupBox("Point cloud inputs")
        layout_input_group = QVBoxLayout(input_group_widget)
        widget_inputs = QWidget()
        layout_input_form = QFormLayout(widget_inputs)
        self.fs_pc1 = FileSelector(input_dir)
        self.fs_pc2 = FileSelector(input_dir)
        bt_gaussian = CustomPushButton("Import gaussian point cloud", 90)
        self.checkbox_cache = QCheckBox()
        self.checkbox_cache.setText("Save converted point clouds")
        self.checkbox_cache.setStyleSheet(
            "QCheckBox::indicator {"
            f"    width: 20px;"
            f"    height: 20px;"
            "}"
            "QCheckBox::indicator::text {"
            f"    padding-left: 0.7em;"
            "}"
        )

        layout_input_form.addRow("First point cloud:", self.fs_pc1)
        layout_input_form.addRow("Second point cloud:", self.fs_pc2)
        layout_input_group.addWidget(self.checkbox_cache)
        layout_input_group.addWidget(widget_inputs)
        layout_input_group.addWidget(bt_gaussian)

        layout_main.addWidget(label_io)
        layout_main.addWidget(sparse_group_widget)
        layout_main.addStretch()
        layout_main.addWidget(input_group_widget)

        bt_sparse.connect_to_clicked(lambda: self.signal_load_sparse.emit(self.fs_input1.file_path,
                                                                          self.fs_input2.file_path))
        bt_gaussian.connect_to_clicked(lambda: self.signal_load_gaussian.emit(self.fs_pc1.file_path,
                                                                              self.fs_pc2.file_path))
