from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QCheckBox, QProgressDialog
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QSizePolicy, QVBoxLayout

from src.gui.widgets.file_selector_widget import FileSelector
from src.gui.workers.qt_workers import PointCloudLoaderInput, PointCloudLoaderGaussian


class InputTab(QWidget):
    result_signal = pyqtSignal(object, object, bool, object, object)

    def __init__(self, input_dir):
        super().__init__()

        # TODO: Set up loading bar
        self.progress_dialog = QProgressDialog()
        self.progress_dialog.setModal(Qt.WindowModal)
        self.progress_dialog.setWindowTitle("Loading")
        self.progress_dialog.setLabel(QLabel("Loading point clouds..."))
        self.progress_dialog.close()

        layout = QVBoxLayout()
        self.setLayout(layout)

        label_sparse = QLabel("Sparse inputs: ")
        label_sparse.setStyleSheet(
            "QLabel {"
            "    font-size: 14px;"
            "    font-weight: bold;"
            "    padding: 8px;"
            "}"
        )

        self.fs_input1 = FileSelector(text="First sparse input:", base_path=input_dir)
        self.fs_input2 = FileSelector(text="Second sparse input:", base_path=input_dir)
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
        self.fs_pc1 = FileSelector(text="First point cloud:", base_path=input_dir)
        self.fs_pc2 = FileSelector(text="Second point cloud:", base_path=input_dir)
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

    def handle_result(self, pc_first, pc_second, original1=None, original2=None):
        self.progress_dialog.close()
        self.result_signal.emit(pc_first, pc_second, self.checkbox_cache.isChecked(), original1, original2)
