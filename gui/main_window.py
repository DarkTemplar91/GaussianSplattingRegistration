import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QSplitter, QWidget, QGroupBox, QVBoxLayout, \
    QTabWidget, QSizePolicy, QCheckBox, QLabel, QPushButton, QProgressDialog, QErrorMessage

from gui.file_selector_widget import FileSelector
from gui.global_registration_widget import GlobalRegistrationGroup
from gui.local_registration_widget import LocalRegistrationGroup
from gui.merger_widget import MergerWidget
from gui.open3d_window import Open3DWindow
from gui.qt_workers import PointCloudLoaderInput, PointCloudLoaderGaussian, PointCloudLoaderO3D, PointCloudSaver
from gui.transformation_widget import Transformation3DPicker
from gui.visualizer_widget import VisualizerWidget


class RegistrationMainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(RegistrationMainWindow, self).__init__(parent)
        self.merger_widget = None
        self.visualizer_widget = None
        self.transformation_picker = None
        self.fs_cache1 = None
        self.fs_cache2 = None
        self.checkbox_cache = None
        self.fs_input1 = None
        self.fs_input2 = None
        self.fs_pc1 = None
        self.fs_pc2 = None
        self.setWindowTitle("Gaussian Splatting Registration")

        dir_path = os.path.dirname(os.path.realpath(__file__))
        parent_dir = os.path.abspath(os.path.join(dir_path, os.pardir))

        self.cache_dir = os.path.join(parent_dir, "cache")
        self.input_dir = os.path.join(parent_dir, "inputs")
        self.output_dir = os.path.join(parent_dir, "output")

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
        self.setup_registration_group(group_registration)

        layout_pane.addWidget(group_input_data)
        layout_pane.addWidget(group_registration)

        splitter.addWidget(self.pane_open3d)
        splitter.addWidget(pane_data)

        splitter.setOrientation(1)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 0)

        self.setCentralWidget(splitter)

        # TODO: Set up loading bar
        self.progress_dialog = QProgressDialog()
        self.progress_dialog.setModal(Qt.WindowModal)
        self.progress_dialog.setWindowTitle("Loading")
        self.progress_dialog.setLabel(QLabel("Loading point clouds..."))
        self.progress_dialog.close()

    def setup_input_group(self, group_input_data):
        group_input_data.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        group_input_data.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        group_input_data.setTitle("Inputs and settings")
        layout = QVBoxLayout()
        group_input_data.setLayout(layout)

        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)

        self.transformation_picker = Transformation3DPicker()
        self.transformation_picker.transformation_matrix_changed.connect(self.update_point_clouds)
        self.visualizer_widget = VisualizerWidget()
        self.merger_widget = MergerWidget(self.output_dir, self.transformation_picker.transformation_matrix)

        tab_widget.addTab(self.setup_input_tab(), "I/O files")
        tab_widget.addTab(self.setup_cache_tab(), "Cache")
        tab_widget.addTab(self.transformation_picker, "Transformation")
        tab_widget.addTab(self.visualizer_widget, "Visualizer")
        tab_widget.addTab(self.merger_widget, "Merging")

    def setup_registration_group(self, group_registration):
        group_registration.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        group_registration.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout()
        group_registration.setLayout(layout)

        layout.addWidget(GlobalRegistrationGroup())
        layout.addWidget(LocalRegistrationGroup())

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

        self.fs_input1 = FileSelector(text="First sparse input:", base_path=self.input_dir)
        self.fs_input2 = FileSelector(text="Second sparse input:", base_path=self.input_dir)
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
        self.fs_pc1 = FileSelector(text="First point cloud:", base_path=self.input_dir)
        self.fs_pc2 = FileSelector(text="First point cloud:", base_path=self.input_dir)
        bt_gaussian = QPushButton("Import gaussian point cloud")
        bt_gaussian.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        bt_gaussian.setStyleSheet("padding-left: 10px; padding-right: 10px;"
                                  "padding-top: 2px; padding-bottom: 2px;")
        bt_gaussian.setFixedSize(250, 30)

        self.checkbox_cache = QCheckBox()
        self.checkbox_cache.setText("Save converted point clouds")
        self.checkbox_cache.setStyleSheet(
            "QCheckBox::indicator {"
            "    width: 20px;"
            "    height: 20px;"
            "}"
            "QCheckBox::indicator::text {"
            "    padding-left: 10px;"
            "}"
        )

        layout.addWidget(label_sparse)
        layout.addWidget(self.fs_input1)
        layout.addWidget(self.fs_input2)
        layout.addWidget(bt_sparse)
        layout.addSpacing(40)
        layout.addWidget(label_pc)
        layout.addWidget(self.fs_pc1)
        layout.addWidget(self.fs_pc2)
        layout.addWidget(bt_gaussian)
        layout.addWidget(self.checkbox_cache)

        layout.addStretch()

        bt_sparse.clicked.connect(self.sparse_button_pressed)
        bt_gaussian.clicked.connect(self.gaussian_button_pressed)

        return pane

    def setup_cache_tab(self):
        pane = QWidget()
        layout = QVBoxLayout()
        pane.setLayout(layout)

        self.fs_cache1 = FileSelector(text="First point cloud:", base_path=self.cache_dir)
        self.fs_cache2 = FileSelector(text="Second point cloud:", base_path=self.cache_dir)

        label_cache = QLabel("Cached point clouds: ")
        label_cache.setStyleSheet(
            "QLabel {"
            "    font-size: 14px;"
            "    font-weight: bold;"
            "    padding: 8px;"
            "}"
        )

        bt_cached = QPushButton("Import cached point clouds")
        bt_cached.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        bt_cached.setStyleSheet("padding-left: 10px; padding-right: 10px;"
                                "padding-top: 2px; padding-bottom: 2px;")
        bt_cached.setFixedSize(250, 30)

        bt_cached.clicked.connect(self.cached_button_pressed)

        layout.addWidget(label_cache)
        layout.addWidget(self.fs_cache1)
        layout.addWidget(self.fs_cache2)
        layout.addWidget(bt_cached)
        layout.addStretch()
        layout.setAlignment(Qt.AlignTop)

        return pane

    # Event handlers
    def sparse_button_pressed(self):
        path_first = self.fs_input1.file_path
        path_second = self.fs_input2.file_path

        worker = PointCloudLoaderInput(path_first, path_second)
        worker.result_signal.connect(self.handle_result)

        worker.start()
        self.progress_dialog.exec()

    def gaussian_button_pressed(self):
        path_first = self.fs_pc1.file_path
        path_second = self.fs_pc2.file_path

        worker = PointCloudLoaderGaussian(path_first, path_second)
        worker.result_signal.connect(self.handle_result)

        worker.start()
        self.progress_dialog.exec()

    def cached_button_pressed(self):
        path_first = self.fs_cache1.file_path
        path_second = self.fs_cache2.file_path

        worker = PointCloudLoaderO3D(path_first, path_second)
        worker.result_signal.connect(self.handle_result)

        worker.start()
        self.progress_dialog.exec()

    def update_point_clouds(self, transformation_matrix):
        self.pane_open3d.update_transform(transformation_matrix)

    def handle_result(self, pc_first, pc_second):
        self.progress_dialog.close()
        if not pc_first or not pc_second:
            # TODO: Further error messages
            dialog = QErrorMessage(self)
            dialog.setWindowTitle("Error")
            dialog.showMessage("Importing one or both of the point clouds failed.\nPlease check that you entered the "
                               "correct path!")
            return

        if self.checkbox_cache.isChecked():
            worker = PointCloudSaver(pc_first, pc_second)
            worker.run()

        self.pane_open3d.load_point_clouds(pc_first, pc_second)
