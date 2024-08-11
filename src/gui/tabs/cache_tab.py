from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QProgressDialog

from src.gui.widgets.file_selector_widget import FileSelector
from src.gui.workers.qt_workers import PointCloudLoaderO3D
import src.utils.graphics_utils as graphic_util


class CacheTab(QWidget):
    result_signal = pyqtSignal(object, object, bool)

    def __init__(self, cache_dir):
        super().__init__()

        # TODO: Set up loading bar
        self.progress_dialog = QProgressDialog()
        self.progress_dialog.setModal(Qt.WindowModal)
        self.progress_dialog.setWindowTitle("Loading")
        self.progress_dialog.setLabel(QLabel("Loading point clouds..."))
        self.progress_dialog.close()

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.fs_cache1 = FileSelector(text="First point cloud:", base_path=cache_dir)
        self.fs_cache2 = FileSelector(text="Second point cloud:", base_path=cache_dir)

        label_cache = QLabel("Cached point clouds: ")
        label_cache.setStyleSheet(
            "QLabel {"
            "    font-size: 11pt;"
            "    font-weight: bold;"
            f"    padding: {int(graphic_util.SIZE_SCALE_X * 8)}px;"
            "}"
        )

        bt_cached = QPushButton("Import cached point clouds")
        bt_cached.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        bt_cached.setStyleSheet(f"padding-left: 10px; padding-right: {int(graphic_util.SIZE_SCALE_X * 10)}px;"
                                f"padding-top: 2px; padding-bottom: {int(graphic_util.SIZE_SCALE_X * 2)}px;")
        bt_cached.setFixedSize(int(285 * graphic_util.SIZE_SCALE_X), int(30 * graphic_util.SIZE_SCALE_Y))

        layout.addWidget(label_cache)
        layout.addWidget(self.fs_cache1)
        layout.addWidget(self.fs_cache2)
        layout.addWidget(bt_cached, alignment=Qt.AlignCenter)
        layout.addStretch()
        layout.setAlignment(Qt.AlignTop)

        bt_cached.clicked.connect(self.cached_button_pressed)

    def cached_button_pressed(self):
        path_first = self.fs_cache1.file_path
        path_second = self.fs_cache2.file_path

        worker = PointCloudLoaderO3D(path_first, path_second)
        worker.result_signal.connect(self.handle_result)

        worker.start()
        self.progress_dialog.exec()

    def handle_result(self, pc_first, pc_second):
        self.progress_dialog.close()
        self.result_signal.emit(pc_first, pc_second, False)
