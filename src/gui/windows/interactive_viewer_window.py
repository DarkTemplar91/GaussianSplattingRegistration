import numpy as np
from PySide6 import QtCore
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.utils.rasterization_util import rasterize_image, get_pixmap_from_tensor


class InteractiveImageViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('3D Viewer')

        self.point_cloud = None
        self.camera = None

        self.render_label = None

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_view)

        self.last_mouse_position = None
        self.left_mouse_pressed = False
        self.setMouseTracking(True)

        self.rotation_speed = np.radians(1)
        self.zoom_factor = 0.01
        self.speed = 0.01

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.render_label = QLabel()
        layout.addWidget(self.render_label)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

    def mouseMoveEvent(self, event):
        if self.last_mouse_position is None or not self.left_mouse_pressed:
            return

        dx = self.last_mouse_position.x() - event.x()
        dy = self.last_mouse_position.y() - event.y()

        self.camera.rotate(dx * self.rotation_speed, dy * self.rotation_speed)

        self.last_mouse_position = event.pos()
        self.camera.update_view_matrix()

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        self.left_mouse_pressed = True
        self.last_mouse_position = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        self.left_mouse_pressed = False

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.camera.zoom(delta * self.zoom_factor)
        self.camera.update_view_matrix()

    def update_view(self):
        if self.point_cloud is None:
            return

        """self.camera.width = self.width()
        self.camera.height = self.height()"""
        image_tensor = rasterize_image(self.point_cloud, self.camera, 1, np.zeros(3), "cuda:0", False)
        pix = get_pixmap_from_tensor(image_tensor)
        self.render_label.setPixmap(pix)

    def set_active(self, start):
        if start:
            self.timer.start(30)
        else:
            self.timer.stop()

    def set_point_cloud(self, point_cloud):
        self.point_cloud = point_cloud

    def set_camera(self, camera):
        self.camera = camera
