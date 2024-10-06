import numpy as np
from PySide6 import QtCore
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.utils.rasterization_util import rasterize_image, get_pixmap_from_tensor


class InteractiveImageViewer(QWidget):
    def __init__(self, point_cloud, camera):
        super().__init__()
        self.setWindowTitle('3D Viewer')

        self.point_cloud = point_cloud
        self.camera = camera

        self.render_label = None

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_view)
        self.timer.start(30)  # Refresh every 30ms

        self.last_mouse_position = None
        self.setMouseTracking(True)
        self.middle_mouse_pressed = False
        self.left_mouse_pressed = False

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
        if self.last_mouse_position is None:
            return

        if not self.middle_mouse_pressed and not self.left_mouse_pressed:
            return

        dx = self.last_mouse_position.x() - event.x()
        dy = self.last_mouse_position.y() - event.y()

        if self.middle_mouse_pressed:
            if dy != 0:
                self.camera.move_vertically(self.speed * (-1 if dy > 0 else 1))
            if dx != 0:
                self.camera.move_horizontally(-self.speed * (-1 if dx < 0 else 1))

        elif self.left_mouse_pressed:
            self.camera.rotate(dx * self.rotation_speed, dy * self.rotation_speed)

        self.last_mouse_position = event.pos()
        self.camera.update_view_matrix()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.middle_mouse_pressed = True
        elif event.button() == Qt.MouseButton.LeftButton:
            self.left_mouse_pressed = True
        else:
            return

        self.last_mouse_position = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.middle_mouse_pressed = False
        elif event.button() == Qt.MouseButton.LeftButton:
            self.left_mouse_pressed = False

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.camera.zoom(delta * self.zoom_factor)
        self.camera.update_view_matrix()

    def update_view(self):
        image_tensor = rasterize_image(self.point_cloud, self.camera, 1, np.zeros(3), "cuda:0", False)
        pix = get_pixmap_from_tensor(image_tensor)
        self.render_label.setPixmap(pix)
