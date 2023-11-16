from PyQt5.QtWidgets import QWidget, QVBoxLayout

from src.gui.widgets.file_selector_widget import FileSelector


class EvaluationTab(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.fs_cameras = FileSelector(text="Cameras: ")
        self.fs_images = FileSelector(text="Images: ")

        layout.addWidget(self.fs_cameras)
        layout.addWidget(self.fs_images)
        layout.addStretch()

