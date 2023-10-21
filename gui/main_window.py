from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QSplitter, QWidget, QGroupBox, QVBoxLayout, \
    QTabWidget, QSizePolicy, QCheckBox, QLabel, QPushButton, QProgressDialog

from gui.file_selector_widget import FileSelector
from gui.open3d_window import Open3DWindow
from gui.transformation_widget import Transformation3DPicker
from utils.file_loader import load_sparse_pc


class RegistrationMainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(RegistrationMainWindow, self).__init__(parent)
        self.fs_cache = None
        self.checkbox_cache = None
        self.fs_input1 = None
        self.fs_input2 = None
        self.fs_pc1 = None
        self.fs_pc2 = None
        self.setWindowTitle("Gaussian Splatting Registration")

        # Set window size to screen size
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(screen)

        QGroupBox()

        # Create splitter and two planes
        splitter = QSplitter(self)
        self.pane_open3d = Open3DWindow()
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

        splitter.addWidget(self.pane_open3d)
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
            "    font-weight: bold;"
            "    padding: 8px;"
            "}"
        )

        self.fs_input1 = FileSelector(text="First sparse input:")
        self.fs_input2 = FileSelector(text="Second sparse input:")
        bt_sparse = QPushButton("Import sparse point cloud")
        bt_sparse.setStyleSheet("padding-left: 10px; padding-right: 10px;"
                                "padding-top: 2px; padding-bottom: 2px;")
        bt_sparse.setFixedSize(250, 30)
        bt_sparse.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        label_pc = QLabel("Point cloud inputs: ")
        label_pc.setStyleSheet(
            "QLabel {"
            "    font-size: 14px;"
            "    font-weight: bold;"
            "    padding: 8px;"
            "}"
        )
        self.fs_pc1 = FileSelector(text="First point cloud:")
        self.fs_pc2 = FileSelector(text="First point cloud:")
        bt_gaussian = QPushButton("Import gaussian point cloud")
        bt_gaussian.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        bt_gaussian.setStyleSheet("padding-left: 10px; padding-right: 10px;"
                                  "padding-top: 2px; padding-bottom: 2px;")
        bt_gaussian.setFixedSize(250, 30)

        layout.addWidget(label_sparse)
        layout.addWidget(self.fs_input1)
        layout.addWidget(self.fs_input2)
        layout.addWidget(bt_sparse)
        layout.addSpacing(40)
        layout.addWidget(label_pc)
        layout.addWidget(self.fs_pc1)
        layout.addWidget(self.fs_pc2)
        layout.addWidget(bt_gaussian)

        layout.addStretch()

        bt_sparse.clicked.connect(self.sparse_button_pressed)
        bt_gaussian.clicked.connect(self.gaussian_button_pressed)

        return pane

    def setup_cache_tab(self):
        pane = QWidget()
        layout = QVBoxLayout()
        pane.setLayout(layout)

        self.checkbox_cache = QCheckBox()
        self.checkbox_cache.setText("Save/Use converted point clouds")
        self.checkbox_cache.setStyleSheet(
            "QCheckBox::indicator {"
            "    width: 20px;" 
            "    height: 20px;"
            "}"
            "QCheckBox::indicator::text {"
            "    padding-left: 10px;"
            "}"
        )

        self.fs_cache = FileSelector(text="Cache directory")
        layout.addWidget(self.checkbox_cache)
        layout.addWidget(self.fs_cache)
        layout.addStretch()
        layout.setAlignment(Qt.AlignTop)

        return pane

    # Event handlers
    def sparse_button_pressed(self):
        # TODO: Set up loading bar
        progress_dialog = QProgressDialog()
        progress_dialog.setModal(Qt.WindowModal)
        progress_dialog.show()

        path_first = self.fs_input1.text()
        path_second = self.fs_input1.text()

        pc_first = load_sparse_pc(path_first)
        pc_second = load_sparse_pc(path_second)

        if not pc_first or not pc_second:
            # TODO: Throw error, error dialog?
            return

        progress_dialog.close()
        self.pane_open3d.load_point_clouds(pc_first, pc_second)

    def gaussian_button_pressed(self):
        return
