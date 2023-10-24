from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QSizePolicy

from src.gui.widgets.file_selector_widget import FileSelector


class MergerWidget(QWidget):
    def __init__(self, dir_path="", transformation=None):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.transformation_matrix = transformation

        label_title = QLabel("Point cloud merging")
        label_title.setStyleSheet(
            "QLabel {"
            "    font-size: 14px;"
            "    font-weight: bold;"
            "    padding: 8px;"
            "}"
        )

        self.fs_input1 = FileSelector(text="Save directory:", base_path=dir_path)
        bt_merge = QPushButton("Merge point clouds")
        bt_merge.setStyleSheet("padding-left: 10px; padding-right: 10px;"
                               "padding-top: 2px; padding-bottom: 2px;")
        bt_merge.setFixedSize(250, 30)
        bt_merge.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        layout.addWidget(label_title)
        layout.addWidget(self.fs_input1)
        layout.addWidget(bt_merge)
        layout.addStretch()
