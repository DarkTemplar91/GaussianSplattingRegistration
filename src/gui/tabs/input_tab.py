from PySide6.QtCore import Signal, QThread
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QProgressDialog, QGroupBox
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

from src.gui.widgets.centered_push_button import CustomPushButton
from src.gui.widgets.file_selector_widget import FileSelector
from src.gui.workers.qt_base_worker import move_worker_to_thread
from src.gui.workers.qt_pc_loaders import PointCloudLoaderInput, PointCloudLoaderGaussian


class InputTab(QWidget):
    result_signal = Signal(object, object, bool, object, object)

    def __init__(self, input_dir):
        super().__init__()

        # TODO: Create custom spinner instead
        # TODO: Set up loading bar
        self.progress_dialog = QProgressDialog()
        self.progress_dialog.setModal(True)
        self.progress_dialog.setWindowTitle("Loading")
        self.progress_dialog.setLabel(QLabel("Loading point clouds..."))
        self.progress_dialog.close()

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
        self.fs_input1 = FileSelector(text="First sparse input:", base_path=input_dir)
        self.fs_input2 = FileSelector(text="Second sparse input:", base_path=input_dir)
        bt_sparse = CustomPushButton("Import sparse point cloud", 90)
        layout_sparse_group.addWidget(self.fs_input1)
        layout_sparse_group.addWidget(self.fs_input2)
        layout_sparse_group.addWidget(bt_sparse)

        input_group_widget = QGroupBox("Point cloud inputs")
        layout_input_group = QVBoxLayout(input_group_widget)
        self.fs_pc1 = FileSelector(text="First point cloud:", base_path=input_dir)
        self.fs_pc2 = FileSelector(text="Second point cloud:", base_path=input_dir)
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

        layout_input_group.addWidget(self.fs_pc1)
        layout_input_group.addWidget(self.fs_pc2)
        layout_input_group.addWidget(self.checkbox_cache)
        layout_input_group.addWidget(bt_gaussian)

        layout_main.addWidget(label_io)
        layout_main.addWidget(sparse_group_widget)
        layout_main.addStretch()
        layout_main.addWidget(input_group_widget)

        bt_sparse.connect_to_clicked(self.sparse_button_pressed)
        bt_gaussian.connect_to_clicked(self.gaussian_button_pressed)

    def sparse_button_pressed(self):
        path_first = self.fs_input1.file_path
        path_second = self.fs_input2.file_path

        worker = PointCloudLoaderInput(path_first, path_second)
        thread = move_worker_to_thread(worker, self.handle_result_sparse)
        thread.start()
        self.progress_dialog.setLabelText("Loading point clouds...")
        self.progress_dialog.exec()

    def gaussian_button_pressed(self):
        path_first = self.fs_pc1.file_path
        path_second = self.fs_pc2.file_path

        worker = PointCloudLoaderGaussian(path_first, path_second)
        thread = move_worker_to_thread(worker, self.handle_result_gaussian)
        thread.start()
        self.progress_dialog.setLabelText("Loading point clouds...")
        self.progress_dialog.exec()

    def handle_result_sparse(self, input_result: PointCloudLoaderInput.ResultData):
        self.result_signal.emit(input_result.point_cloud_first, input_result.point_cloud_second, False, None, None)
        self.progress_dialog.close()

    def handle_result_gaussian(self, gaussian_result: PointCloudLoaderGaussian.ResultData):
        self.result_signal.emit(gaussian_result.o3d_point_cloud_first, gaussian_result.o3d_point_cloud_second,
                                self.checkbox_cache.isChecked(),
                                gaussian_result.gaussian_point_cloud_first, gaussian_result.gaussian_point_cloud_second)
        self.progress_dialog.close()
