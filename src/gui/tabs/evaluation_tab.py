import json
import os.path

import numpy as np
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy, QFileDialog, QGroupBox, QHBoxLayout, QLabel, \
    QSpinBox, QLineEdit

from src.gui.widgets.file_selector_widget import FileSelector
from src.models.cameras import Camera
from src.utils.graphics_utils import focal2fov


class EvaluationTab(QWidget):
    signal_camera_change = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.cameras_list = list()

        input_group = QGroupBox()
        input_layout = QVBoxLayout()
        input_group.setLayout(input_layout)

        self.fs_cameras = FileSelector(text="Cameras: ", name_filter="*.json")

        self.button_load_cameras = QPushButton("Load cameras")
        self.button_load_cameras.setStyleSheet("padding-left: 10px; padding-right: 10px;"
                                               "padding-top: 2px; padding-bottom: 2px;")
        self.button_load_cameras.setFixedSize(285, 30)
        self.button_load_cameras.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Spinbox row
        spinbox_layout = QHBoxLayout()
        spinbox_widget = QWidget()
        spinbox_widget.setLayout(spinbox_layout)
        label = QLabel("Snap to:")
        self.spinbox = QSpinBox()
        self.spinbox.setFixedWidth(50)
        self.spinbox.setFixedHeight(30)
        self.spinbox.setRange(0, 0)
        self.spinbox.setKeyboardTracking(False)
        self.current_image_name = QLineEdit()
        self.current_image_name.setEnabled(False)
        self.current_image_name.setFixedHeight(30)
        self.current_image_name.setFixedWidth(100)
        self.current_image_name.setAlignment(Qt.AlignLeft)
        spinbox_layout.addWidget(label)
        spinbox_layout.addWidget(self.spinbox)
        spinbox_layout.addWidget(self.current_image_name)
        spinbox_layout.addStretch()
        self.spinbox.setEnabled(False)
        self.spinbox.valueChanged.connect(self.current_camera_changed)

        input_layout.addWidget(self.fs_cameras)
        input_layout.addWidget(self.button_load_cameras, alignment=Qt.AlignCenter)
        input_layout.addWidget(spinbox_widget)

        self.evaluation_group = QGroupBox()
        evaluation_layout = QVBoxLayout()
        self.evaluation_group.setLayout(evaluation_layout)

        self.fs_images = FileSelector(text="Images: ", type=QFileDialog.Directory)
        self.fs_log = FileSelector(text="Log file: ", name_filter="*.txt")
        self.button_evaluate = QPushButton("Evaluate registration")
        self.button_evaluate.setStyleSheet("padding-left: 10px; padding-right: 10px;"
                                           "padding-top: 2px; padding-bottom: 2px;")
        self.button_evaluate.setFixedSize(285, 30)
        self.button_evaluate.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        evaluation_layout.addWidget(self.fs_images)
        evaluation_layout.addWidget(self.fs_log)
        evaluation_layout.addWidget(self.button_evaluate)

        layout.addWidget(input_group)
        layout.addWidget(self.evaluation_group)

        self.button_load_cameras.clicked.connect(self.load_cameras_clicked)

        self.pc1 = None
        self.pc2 = None

    def load_cameras_clicked(self):
        self.cameras_list.clear()
        self.spinbox.setEnabled(False)

        cameras_path = self.fs_cameras.file_path
        if cameras_path == "" or not os.path.isfile(cameras_path):
            return

        f = open(cameras_path)
        data = json.load(f)
        for camera_iter in data:
            fx = camera_iter["fx"]
            fy = camera_iter["fy"]
            height = camera_iter["height"]
            width = camera_iter["width"]
            fov_x = focal2fov(fx, width)
            fov_y = focal2fov(fy, height)

            rotation = np.array([np.array(xi) for xi in camera_iter["rotation"]])
            position = np.array([np.array(xi) for xi in camera_iter["position"]])
            image_name = camera_iter["img_name"]
            camera = Camera(rotation, position, fov_x, fov_y, image_name, width, height)
            self.cameras_list.append(camera)

        self.spinbox.setEnabled(True)
        self.spinbox.setRange(1, len(self.cameras_list))
        self.current_image_name.setText(self.cameras_list[0].image_name)

    def current_camera_changed(self, camera_id):
        current_camera = self.cameras_list[camera_id-1]
        self.current_image_name.setText(current_camera.image_name)
        R = current_camera.R
        T = current_camera.T

        extrinsics = np.eye(4)
        extrinsics[:3, :3] = R
        extrinsics[3, :3] = T
        extrinsics = extrinsics.transpose()

        self.signal_camera_change.emit(extrinsics)

