from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QSplitter, QTextEdit, QWidget

from gui.open3d_window import Open3DWindow


class RegistrationMainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(RegistrationMainWindow, self).__init__(parent)
        self.setWindowTitle("Gaussian Splatting Registration")

        # Set window size to screen size
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(screen)

        # Change the color of the title bar using a stylesheet
        self.setStyleSheet("QMenuBar { background-color: #000000; }"
                             "QMenuBar::item { background-color: #336699; color: white; }")

        # Create splitter and two planes
        splitter = QSplitter(self)
        pane_open3d = Open3DWindow()
        pane_data = QTextEdit("Placeholder")

        splitter.addWidget(pane_open3d)
        splitter.addWidget(pane_data)

        splitter.setOrientation(1)

        splitter.setStretchFactor(0, 50)
        splitter.setStretchFactor(1, 1)

        self.setCentralWidget(splitter)

