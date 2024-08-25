from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGroupBox, QFormLayout

from src.gui.widgets.custom_push_button import CustomPushButton
from src.gui.widgets.file_selector_widget import FileSelector


class CacheTab(QWidget):
    signal_load_cached = Signal(str, str)

    def __init__(self, cache_dir):
        super().__init__()
        self.progress_dialog = None
        layout = QVBoxLayout(self)

        label_cache = QLabel("Cached point clouds: ")
        label_cache.setStyleSheet(
            """QLabel {
                font-size: 12pt;
                font-weight: bold;
                padding-bottom: 0.5em;
            }"""
        )

        box_widget = QGroupBox(self)
        layout_box = QVBoxLayout(box_widget)

        form_widget = QWidget()
        layout_form = QFormLayout(form_widget)
        self.fs_cache1 = FileSelector(cache_dir)
        self.fs_cache2 = FileSelector(cache_dir)
        layout_form.addRow("First point cloud:", self.fs_cache1)
        layout_form.addRow("Second point cloud:", self.fs_cache2)

        bt_cached = CustomPushButton("Import cached point clouds", 90)
        layout_box.addWidget(form_widget)
        layout_box.addWidget(bt_cached)

        layout.addWidget(label_cache)
        layout.addWidget(box_widget)
        layout.addStretch()

        bt_cached.connect_to_clicked(lambda: self.signal_load_cached.emit(self.fs_cache1.file_path,
                                                                          self.fs_cache2.file_path))
