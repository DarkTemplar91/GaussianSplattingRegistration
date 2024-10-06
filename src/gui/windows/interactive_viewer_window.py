import sys

import numpy as np
from PySide6 import QtWidgets, QtCore
import torch
import torch.nn.functional as F
from PySide6.QtGui import Qt

from src.utils.rasterization_util import rasterize_image, get_pixmap_from_tensor


class InteractiveImageViewer(QtWidgets.QWidget):
    def __init__(self, point_cloud, camera):
        super().__init__()
        self.setWindowTitle('3D Viewer')
        self.setFixedSize(1600, 900)

        self.point_cloud = point_cloud
        self.camera = camera

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_view)
        self.timer.start(30)  # Refresh every 30ms

        self.last_mouse_position = None
        self.setMouseTracking(True)
        self.middle_mouse_pressed = False
        self.left_mouse_pressed = False

        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel(self)
        layout.addWidget(self.label)

    def keyPressEvent(self, event):
        """Handle keyboard input for camera movement."""
        if event.key() == Qt.Key_Control:
            self.ctrl_pressed = True  # Set Ctrl key pressed state

    def keyReleaseEvent(self, event):
        """Handle keyboard input for camera movement."""
        if event.key() == Qt.Key_Control:
            self.ctrl_pressed = False

    def mouseMoveEvent(self, event):
        if self.middle_mouse_pressed and self.last_mouse_position is not None:
            dx = self.last_mouse_position.x() - event.x()
            dy = self.last_mouse_position.y() - event.y()

            if dy > 0:
                self.camera.move("down")
            elif dy < 0:
                self.camera.move("up")

            if dx < 0:
                self.camera.move("left")
            elif dx > 0:
                self.camera.move("right")

        elif self.left_mouse_pressed and self.last_mouse_position is not None:
            dx = self.last_mouse_position.x() - event.x()
            dy = self.last_mouse_position.y() - event.y()

            # Rotate the camera based on left mouse button drag
            self.camera.rotate(dx * self.camera.rotation_speed, dy * self.camera.rotation_speed)

        self.last_mouse_position = event.pos()

    def mousePressEvent(self, event):
        """Handle mouse press to capture the mouse position."""
        if event.button() == Qt.MiddleButton:
            self.middle_mouse_pressed = True  # Set the middle mouse pressed state
            self.last_mouse_position = event.pos()  # Capture the mouse position
        elif event.button() == Qt.LeftButton:
            self.left_mouse_pressed = True  # Set the left mouse pressed state
            self.last_mouse_position = event.pos()  # Capture the mouse position

    def mouseReleaseEvent(self, event):
        """Release mouse to show the cursor again."""
        if event.button() == Qt.MiddleButton:
            self.middle_mouse_pressed = False  # Reset the middle mouse pressed state
        elif event.button() == Qt.LeftButton:
            self.left_mouse_pressed = False

    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming."""
        delta = event.angleDelta().y()  # Get the wheel delta
        self.camera.zoom(delta)

    def update_view(self):
        image_tensor = rasterize_image(self.point_cloud, self.camera, 1, np.zeros(3), "cuda:0", False)
        pix = get_pixmap_from_tensor(image_tensor)
        self.label.setPixmap(pix)