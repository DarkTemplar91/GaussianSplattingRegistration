from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QSplitter, QWidget, QGroupBox, QVBoxLayout, \
    QTabWidget, QSizePolicy, QCheckBox, QLabel, QHBoxLayout, QPushButton

from PyQt5.QtCore import Qt

from gui.file_selector_widget import FileSelector
from gui.open3d_window import Open3DWindow
from gui.transformation_widget import Transformation3DPicker


class RegistrationMainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(RegistrationMainWindow, self).__init__(parent)
        self.setWindowTitle("Gaussian Splatting Registration")

        # Set window size to screen size
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(screen)

        QGroupBox()

        # Create splitter and two planes
        splitter = QSplitter(self)
        pane_open3d = Open3DWindow()
        pane_data = QWidget()

        layout_pane = QVBoxLayout()
        pane_data.setLayout(layout_pane)

        group_input_data = QGroupBox()
        self.setup_input_group(group_input_data)

        group_registration = QGroupBox()
        group_registration.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        group_registration.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        group_registration.setTitle("Registration")

        layout_pane.addWidget(group_input_data)
        layout_pane.addWidget(group_registration)

        splitter.addWidget(pane_open3d)
        splitter.addWidget(pane_data)

        splitter.setOrientation(1)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)

        self.setCentralWidget(splitter)

    def setup_input_group(self, group_input_data):
        group_input_data.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        group_input_data.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        group_input_data.setTitle("Inputs")
        layout = QVBoxLayout()
        group_input_data.setLayout(layout)

        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)

        tab_widget.addTab(self.setup_input_tab(), "I/O files")
        tab_widget.addTab(self.setup_cache_tab(), "Cache")
        tab_widget.addTab(Transformation3DPicker(), "Transformation")

    def setup_registration_group(self, group_registration):
        group_registration.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        group_registration.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        group_registration.setTitle("Registration")

    def setup_input_tab(self):
        pane = QWidget()
        layout = QVBoxLayout()
        pane.setLayout(layout)

        label_sparse = QLabel("Sparse inputs: ")
        label_sparse.setStyleSheet(
            "QLabel {"
            "    font-size: 14px;"
            "    font-weight: bold;"  # Bold font
            "    padding: 8px;"  # Padding
            "}"
        )

        fs_input1 = FileSelector(text="First sparse input:")
        fs_input2 = FileSelector(text="Second sparse input:")
        bt_sparse = QPushButton("Import sparse point cloud")
        bt_sparse.setStyleSheet("padding-left: 10px; padding-right: 10px;"
                                "padding-top: 2px; padding-bottom: 2px;")
        bt_sparse.setFixedSize(250, 30)
        bt_sparse.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        label_pc = QLabel("Point cloud inputs: ")
        label_pc.setStyleSheet(
            "QLabel {"
            "    font-size: 14px;"
            "    font-weight: bold;"  # Bold font
            "    padding: 8px;"  # Padding
            "}"
        )
        fs_pc1 = FileSelector(text="First point cloud:")
        fs_pc2 = FileSelector(text="First point cloud:")
        bt_gaussian = QPushButton("Import gaussian point cloud")
        bt_gaussian.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        bt_gaussian.setStyleSheet("padding-left: 10px; padding-right: 10px;"
                                  "padding-top: 2px; padding-bottom: 2px;")
        bt_gaussian.setFixedSize(250, 30)

        layout.addWidget(label_sparse)
        layout.addWidget(fs_input1)
        layout.addWidget(fs_input2)
        layout.addWidget(bt_sparse)
        layout.addSpacing(40)
        layout.addWidget(label_pc)
        layout.addWidget(fs_pc1)
        layout.addWidget(fs_pc2)
        layout.addWidget(bt_gaussian)

        layout.addStretch()

        return pane

    def setup_cache_tab(self):
        pane = QWidget()
        layout = QVBoxLayout()
        pane.setLayout(layout)

        checkbox = QCheckBox()
        checkbox.setText("Save converted point clouds to directory")
        checkbox.setStyleSheet(
            "QCheckBox::indicator {"
            "    width: 20px;"  # Adjust the width of the indicator (checkbox)
            "    height: 20px;"  # Adjust the height of the indicator
            "}"
            "QCheckBox::indicator::text {"
            "    padding-left: 10px;"  # Adjust the left padding for the text
            "}"
        )

        layout.addWidget(checkbox)
        layout.addWidget(FileSelector(text="Cache directory"))
        layout.addStretch()
        layout.setAlignment(Qt.AlignTop)

        return pane
