import os

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QLabel, QPushButton, QSizePolicy, QStyle, QFileDialog
import src.utils.graphics_utils as graphic_util


class FileSelector(QWidget):
    def __init__(self, parent=None, text="", base_path=None, label_width=120,
                 file_type=QFileDialog.FileMode.ExistingFile,
                 name_filter="All files (*.*);;*.ply;;*.stl;;*.obj;;*.off"):
        super().__init__(parent)

        layout = QHBoxLayout()
        self.setLayout(layout)
        self.type = file_type
        self.name_filter = name_filter

        self.inputField = QLineEdit()
        label = QLabel(text)
        label.setFixedWidth(int(label_width * graphic_util.SIZE_SCALE_X))
        button = QPushButton()
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton)
        button.setIcon(icon)

        self.base_path = base_path
        if not base_path or not os.path.isdir(base_path):
            self.base_path = None

        layout.addWidget(label)
        layout.addWidget(self.inputField)
        layout.addWidget(button)

        button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        button.clicked.connect(self.button_clicked)
        self.inputField.textChanged.connect(self.text_changed)
        self.file_path = str()
        layout.addStretch()

    def button_clicked(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(self.type)

        if self.type is not QFileDialog.FileMode.Directory:
            dialog.setNameFilter(self.name_filter)

        if self.base_path:
            dialog.setDirectory(self.base_path)

        dialog.setViewMode(QFileDialog.ViewMode.Detail)
        if dialog.exec():
            self.file_path = dialog.selectedFiles()[0]
            self.inputField.setText(self.file_path)

    def text_changed(self):
        self.file_path = self.inputField.text()
