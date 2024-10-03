import numpy as np
import torch
from PIL import Image
from PySide6 import QtGui

from src.gui.workers.qt_base_worker import BaseWorker
from src.models.cameras import Camera
from src.models.gaussian_model import GaussianModel
from src.utils.graphics_utils import focal2fov, get_focal_from_intrinsics
from src.utils.rasterization_util import rasterize_image, get_pixmap_from_tensor


class RasterizerWorker(BaseWorker):

    def __init__(self, pc1, pc2, transformation, extrinsic, intrinsic, scale, color, img_height, img_width):
        super().__init__()

        self.device = torch.device("cuda:0")
        self.pc1 = pc1
        self.pc2 = pc2

        self.transformation = transformation
        self.width = img_width
        self.height = img_height
        self.scale = scale
        self.color = color

        self.extrinsic = extrinsic
        self.intrinsic = intrinsic

        self.fx, self.fy = get_focal_from_intrinsics(intrinsic)

    def run(self):
        with torch.no_grad():
            point_cloud = GaussianModel.get_merged_gaussian_point_clouds(self.pc1, self.pc2, self.transformation)

            camera_mat = self.extrinsic.transpose()
            camera = Camera(camera_mat[:3, :3], camera_mat[3, :3], self.fx, self.fy, "",
                            self.width, self.height)

            point_cloud.move_to_device(self.device)
            image_tensor = rasterize_image(point_cloud, camera, self.scale, self.color, self.device, False)
            pix = get_pixmap_from_tensor(image_tensor)

            del point_cloud
            torch.cuda.empty_cache()
            self.signal_result.emit(pix)

        self.signal_progress.emit(100)
        #self.signal_finished.emit()
        torch.cuda.empty_cache()


