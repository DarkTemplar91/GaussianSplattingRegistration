import numpy as np
import torch
from PIL import Image
from PyQt5 import QtGui
from PyQt5.QtCore import QObject, pyqtSignal

from src.models.cameras import Camera
from src.models.gaussian_model import GaussianModel
from src.utils.graphics_utils import focal2fov, get_focal_from_intrinsics
from src.utils.rasterization_util import rasterize_image


class RasterizerWorker(QObject):
    signal_finished = pyqtSignal()
    signal_rasterization_done = pyqtSignal(object)

    def __init__(self, pc1, pc2, transformation, extrinsic, intrinsic, scale, color, img_height, img_width):
        super().__init__()

        self.device = torch.device("cuda:0")
        self.pc1 = pc1.clone_gaussian()
        self.pc2 = pc2.clone_gaussian()

        self.transformation = transformation
        self.width = img_width
        self.height = img_height
        self.scale = scale
        self.color = color

        self.extrinsic = extrinsic
        self.intrinsic = intrinsic

        fx, fy = get_focal_from_intrinsics(intrinsic)
        self.fov_x = focal2fov(fx, img_width)
        self.fov_y = focal2fov(fy, img_height)

    def do_rasterization(self):
        with torch.no_grad():
            point_cloud = GaussianModel.get_merged_gaussian_point_clouds(self.pc1, self.pc2, self.transformation)

            camera_mat = self.extrinsic.transpose()
            camera = Camera(camera_mat[:3, :3], camera_mat[3, :3], self.fov_x, self.fov_y, "",
                            self.width, self.height)

            image_tensor, _ = rasterize_image(point_cloud, camera, self.scale, self.color, self.device)

            pix = self.get_pixmap_from_tensor(image_tensor)
            self.signal_rasterization_done.emit(pix)

        self.signal_finished.emit()
        torch.cuda.empty_cache()

    def get_pixmap_from_tensor(self, image_tensor):
        numpy_image = (image_tensor * 255).clamp(0, 255).to(torch.uint8).permute(1, 2, 0).cpu().detach().numpy().astype(
            dtype=np.uint8)
        img_save = Image.fromarray(numpy_image)

        img_save = img_save.convert("RGBA")
        data = img_save.tobytes("raw", "RGBA")

        qim = QtGui.QImage(data, self.width, self.height, QtGui.QImage.Format_RGBA8888)
        pix = QtGui.QPixmap.fromImage(qim)
        return pix
