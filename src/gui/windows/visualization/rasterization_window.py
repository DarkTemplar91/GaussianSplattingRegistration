import numpy as np
import torch
from PySide6 import QtCore
from PySide6.QtGui import Qt, QMouseEvent
from PySide6.QtWidgets import QLabel, QVBoxLayout, QScrollArea

from gui.windows.visualization.viewer_interface import ViewerInterface
from src.models.gaussian_model import GaussianModel
from src.utils.rasterization_util import rasterize_image, get_pixmap_from_tensor


class State:
    NONE = 0
    ROTATE = 1
    TRANSLATE = 2
    ROLL = 3
    ZOOM = 4


# noinspection PyTypeChecker
class GaussianSplatWindow(ViewerInterface):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('3D Viewer')

        self.pc1 = None
        self.pc2 = None
        self.point_cloud_merged = None
        self.camera = None

        self.layout: QVBoxLayout = None
        self.scroll_area = None
        self.render_label: QLabel = None

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_view)

        # Mouse state variables
        self.mouse_down_x = 0
        self.mouse_down_y = 0
        self.state = State.NONE
        self.original_rotation = None
        self.original_position = None
        self.aabb = None

        self.rotation_speed = np.radians(1)
        self.roll_speed = np.radians(5)
        self.translate_speed = 7
        self.zoom_factor = 0.01

        # Approximate background color of the qdarkstyle theme
        self.background_color = np.array((0.09803921568627451, 0.13725490196078433, 0.17647058823529413))

        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.scroll_area = QScrollArea()
        self.scroll_area.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.render_label = QLabel()
        self.render_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.render_label.setScaledContents(False)
        self.render_label.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.scroll_area.setWidget(self.render_label)
        self.layout.addWidget(self.scroll_area)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.set_background_color(self.background_color)

    def resizeEvent(self, event):
        if self.render_label.pixmap() is None:
            return

        scroll_area_size = self.scroll_area.viewport().size()
        scaled_pixmap = self.render_label.pixmap().scaled(scroll_area_size, Qt.AspectRatioMode.KeepAspectRatio,
                                                          Qt.TransformationMode.SmoothTransformation)
        self.render_label.setPixmap(scaled_pixmap)
        self.render_label.resize(scaled_pixmap.size())

        super().resizeEvent(event)

    def set_background_color(self, rgb_array):
        r_255 = int(rgb_array[0] * 255)
        g_255 = int(rgb_array[1] * 255)
        b_255 = int(rgb_array[2] * 255)

        self.background_color = rgb_array
        self.render_label.setStyleSheet(f'background-color: rgb({r_255}, {g_255}, {b_255})')

    def mousePressEvent(self, event: QMouseEvent):
        self.mouse_down_x = event.x()
        self.mouse_down_y = event.y()
        self.original_rotation = self.camera.rotation.clone()
        self.original_position = self.camera.position.clone()

        if event.button() == Qt.MouseButton.LeftButton:
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self.state = State.ROLL  # Shift + Left Button: Roll
            elif event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self.state = State.TRANSLATE  # Ctrl + Left Button: Translate
            else:
                self.state = State.ROTATE  # Left Button: Rotate

        elif event.button() == Qt.MouseButton.MiddleButton:
            self.state = State.TRANSLATE  # Middle Button: Translate

    def mouseMoveEvent(self, event: QMouseEvent):
        dx = event.x() - self.mouse_down_x
        dy = event.y() - self.mouse_down_y

        if self.state == State.ROTATE:
            self.camera.rotation = self.original_rotation.clone()
            self.camera.position = self.original_position.clone()
            self.camera.rotate(dx * self.rotation_speed, dy * self.rotation_speed)
        elif self.state == State.TRANSLATE:
            self.camera.rotation = self.original_rotation.clone()
            self.camera.position = self.original_position.clone()
            self.camera.translate(dx * self.translate_speed, dy * self.translate_speed)
        elif self.state == State.ROLL:
            self.camera.rotation = self.original_rotation.clone()
            self.camera.roll(dx * self.roll_speed)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.state = State.NONE

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.camera.zoom(delta * self.zoom_factor, self.get_aabb)

    @property
    def get_aabb(self):
        return self.aabb

    def update_view(self):
        if self.point_cloud_merged is None:
            return

        if self.camera is None:
            return

        image_tensor = rasterize_image(self.point_cloud_merged, self.camera, 1, self.background_color, "cuda:0", False)
        pix = get_pixmap_from_tensor(image_tensor)
        self.render_label.setPixmap(pix)

    def set_active(self, active):
        if active:
            self.point_cloud_merged.move_to_device("cuda:0")
            self.timer.start(1)
            return

        self.timer.stop()
        if self.point_cloud_merged is not None:
            self.point_cloud_merged.move_to_device("cpu")
            torch.cuda.empty_cache()

    # TODO: Implement if needed
    def on_embed_button_pressed(self):
        pass

    def update_transform(self, transformation):
        if self.pc1 is None or self.pc2 is None:
            return

        if self.point_cloud_merged is not None:
            self.point_cloud_merged.move_to_device("cpu")
            del self.point_cloud_merged
            torch.cuda.empty_cache()

        self.point_cloud_merged = GaussianModel.get_merged_gaussian_point_clouds(self.pc1, self.pc2, transformation)

    def load_point_clouds(self, pc1, pc2, transformation):
        if self.point_cloud_merged is not None:
            self.point_cloud_merged.move_to_device("cpu")
            del self.point_cloud_merged
            torch.cuda.empty_cache()

        if self.pc1 is not None:
            del self.pc1

        if self.pc2 is not None:
            del self.pc2

        self.pc1 = pc1
        self.pc2 = pc2

        self.point_cloud_merged = GaussianModel.get_merged_gaussian_point_clouds(self.pc1, self.pc2, transformation)

    def get_current_view(self):
        if self.camera is None:
            return

        extrinsics = self.camera.viewmat[0].detach().cpu().numpy()
        tan_half_fov = self.camera.height / (self.camera.intrinsics[0, 1, 1].item() * 2.0)
        return self.get_current_view_inner(extrinsics, tan_half_fov)

    def get_camera_model(self):
        return self.camera

    def apply_camera_view(self, transformation):
        if self.camera is None:
            return

        self.camera.set_viewmat(transformation)
