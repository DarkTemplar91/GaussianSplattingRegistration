import json
import os.path

import numpy as np
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QSizePolicy, QFileDialog, QGroupBox, QHBoxLayout,
                             QLabel, QSpinBox, QLineEdit, QErrorMessage)

from src.gui.widgets.color_picker_widget import ColorPicker
from src.gui.widgets.file_selector_widget import FileSelector
from src.models.cameras import Camera
from src.utils.general_utils import convert_to_camera_transform
from src.utils.graphics_utils import focal2fov


class EvaluationTab(QWidget):
    signal_camera_change = pyqtSignal(np.ndarray)
    signal_evaluate_registration = pyqtSignal(list, str, str, np.ndarray)

    def __init__(self):
        super().__init__()

        self.error_message = None

        self.raster_window = None
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.cameras_list = []

        input_group = QGroupBox()
        input_group.setTitle("Cameras")
        input_layout = QVBoxLayout()
        input_group.setLayout(input_layout)

        self.fs_cameras = FileSelector(text="Cameras: ", name_filter="*.json", label_width=60)

        self.button_load_cameras = QPushButton("Load cameras")
        self.button_load_cameras.setStyleSheet("padding-left: 10px; padding-right: 10px;"
                                               "padding-top: 2px; padding-bottom: 2px;")
        self.button_load_cameras.setFixedHeight(30)
        self.button_load_cameras.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

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
        input_layout.addWidget(spinbox_widget)
        input_layout.addWidget(self.button_load_cameras)

        evaluation_group = QGroupBox()
        evaluation_group.setTitle("Evaluation")
        evaluation_layout = QVBoxLayout()
        evaluation_group.setLayout(evaluation_layout)

        self.fs_images = FileSelector(text="Images folder: ", file_type=QFileDialog.Directory, label_width=80)
        self.fs_log = FileSelector(text="Log file: ", name_filter="*.txt *.log", label_width=80)
        self.render_color = ColorPicker("Background color: ", np.zeros(3))
        self.button_evaluate = QPushButton("Evaluate registration")
        self.button_evaluate.setStyleSheet("padding-left: 10px; padding-right: 10px;"
                                           "padding-top: 2px; padding-bottom: 2px;")
        self.button_evaluate.setFixedHeight(30)
        self.button_evaluate.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        evaluation_layout.addWidget(self.fs_images)
        evaluation_layout.addWidget(self.fs_log)
        evaluation_layout.addWidget(self.render_color)
        evaluation_layout.addWidget(self.button_evaluate)

        layout.addWidget(input_group)
        layout.addWidget(evaluation_group)

        self.button_load_cameras.clicked.connect(self.load_cameras_clicked)
        self.button_evaluate.clicked.connect(self.evaluate_registration)

    def load_cameras_clicked(self):
        self.cameras_list.clear()
        self.spinbox.setEnabled(False)

        cameras_path = self.fs_cameras.file_path
        if cameras_path == "" or not os.path.isfile(cameras_path):
            dialog = QErrorMessage(self)
            dialog.setWindowTitle("Error")
            dialog.setModal(True)
            dialog.showMessage("Select a valid path to your cameras JSON file!")
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

            rot = np.array([np.array(xi) for xi in camera_iter["rotation"]])
            pos = np.array([np.array(xi) for xi in camera_iter["position"]])
            R, T = convert_to_camera_transform(rot, pos)
            image_name = camera_iter["img_name"]
            camera = Camera(R, T, fov_x, fov_y, image_name, width, height)
            self.cameras_list.append(camera)

        self.spinbox.setEnabled(True)
        self.spinbox.setRange(1, len(self.cameras_list))
        self.spinbox.setValue(0)
        self.current_image_name.setText(self.cameras_list[0].image_name)

    def current_camera_changed(self, camera_id):
        current_camera = self.cameras_list[camera_id - 1]
        self.current_image_name.setText(current_camera.image_name)
        self.signal_camera_change.emit(current_camera.world_view_transform.detach().cpu().numpy().transpose())

    def evaluate_registration(self):
        image_path = self.fs_images.file_path
        log_file = self.fs_log.file_path

        if not len(self.cameras_list) > 0:
            self.creat_error_box("There are no cameras loaded.\nPlease load cameras before evaluation!")
            return

        if not os.path.isdir(image_path):
            self.creat_error_box("Select a valid image directory!")
            return

        if log_file == "":
            self.creat_error_box("Select a path for the log file!")
            return

        color = np.asarray(self.render_color.color_debug)
        self.signal_evaluate_registration.emit(self.cameras_list, image_path, log_file, color)

    def creat_error_box(self, message):
        self.error_message = QErrorMessage()
        self.error_message.setWindowTitle("Error")
        self.error_message.setModal(True)
        self.error_message.showMessage(message)
