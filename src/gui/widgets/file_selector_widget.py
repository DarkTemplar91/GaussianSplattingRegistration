import os

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QLabel, QPushButton, QSizePolicy, QStyle, QFileDialog


class FileSelector(QWidget):
    def __init__(self, parent=None, text="", base_path=None, label_width=120):
        super().__init__(parent)

        layout = QHBoxLayout()
        self.setLayout(layout)

        self.inputField = QLineEdit()
        label = QLabel(text)
        label.setFixedWidth(label_width)
        button = QPushButton()
        icon = self.style().standardIcon(QStyle.SP_DialogOpenButton)
        button.setIcon(icon)

        self.base_path = base_path
        if not base_path or not os.path.isdir(base_path):
            self.base_path = None

        layout.addWidget(label)
        layout.addWidget(self.inputField)
        layout.addWidget(button)

        button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        button.clicked.connect(self.button_clicked)
        self.file_path = str()
        layout.addStretch()

    def button_clicked(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilter("*.ply *.stl *.obj *.off")

        if self.base_path:
            dialog.setDirectory(self.base_path)

        dialog.setViewMode(QFileDialog.Detail)
        if dialog.exec():
            self.file_path = dialog.selectedFiles()[0]
            self.inputField.setText(self.file_path)
