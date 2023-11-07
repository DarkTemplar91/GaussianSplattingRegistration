import math

import numpy as np
import torch
from PIL import Image
from PyQt5 import QtGui
from PyQt5.QtCore import QObject, pyqtSignal
from diff_gaussian_rasterization import GaussianRasterizationSettings, GaussianRasterizer

from src.models.cameras import Camera
from src.models.gaussian_model import GaussianModel
from src.utils.graphics_utils import focal2fov, get_focal_from_intrinsics
from src.utils.point_cloud_merger import merge_point_clouds


class RasterizerWorker(QObject):
    signal_finished = pyqtSignal()
    signal_rasterization_done = pyqtSignal(object)

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

        fx, fy = get_focal_from_intrinsics(intrinsic)
        self.fov_x = focal2fov(fx, img_width)
        self.fov_y = focal2fov(fy, img_height)

    def do_rasterization(self):
        merged_pc = merge_point_clouds(self.pc1, self.pc2, self.transformation)
        point_cloud = GaussianModel(3)
        point_cloud.from_ply(merged_pc)

        camera_mat = self.extrinsic.transpose()
        camera = Camera(camera_mat[:3, :3], camera_mat[3, :3], self.fov_x, self.fov_y)

        # Create zero tensor. We will use it to make pytorch return gradients of the 2D (screen-space) means
        screenspace_points = torch.zeros_like(point_cloud.get_xyz, dtype=point_cloud.get_xyz.dtype, requires_grad=True,
                                              device=self.device) + 0
        try:
            screenspace_points.retain_grad()
        except:
            pass

        bg_color = torch.tensor(self.color, dtype=torch.float32, device=self.device)

        # Set up rasterization configuration
        tan_fov_x = math.tan(self.fov_x * 0.5)
        tan_fov_y = math.tan(self.fov_y * 0.5)

        raster_settings = GaussianRasterizationSettings(
            image_height=int(self.height),
            image_width=int(self.width),
            tanfovx=tan_fov_x,
            tanfovy=tan_fov_y,
            bg=bg_color,
            scale_modifier=self.scale,
            viewmatrix=camera.world_view_transform,
            projmatrix=camera.full_proj_transform,
            sh_degree=3,
            campos=camera.camera_center,
            prefiltered=False,
            debug=True
        )

        rasterizer = GaussianRasterizer(raster_settings=raster_settings)

        means3D = point_cloud.get_xyz
        means2D = screenspace_points
        opacity = point_cloud.get_opacity
        cov3D_precomp = point_cloud.get_covariance(self.scale)
        shs = point_cloud.get_features

        image_tensor, radii = rasterizer(
            means3D=means3D,
            means2D=means2D,
            shs=shs,
            opacities=opacity,
            cov3D_precomp=cov3D_precomp)

        pix = self.get_pixmap_from_tensor(image_tensor)
        self.signal_rasterization_done.emit(pix)

    def get_pixmap_from_tensor(self, image_tensor):
        numpy_image = (image_tensor * 255).clamp(0, 255).to(torch.uint8).permute(1, 2, 0).cpu().detach().numpy().astype(
            dtype=np.uint8)
        img_save = Image.fromarray(numpy_image)

        img_save = img_save.convert("RGBA")
        data = img_save.tobytes("raw", "RGBA")

        qim = QtGui.QImage(data, self.width, self.height, QtGui.QImage.Format_RGBA8888)
        pix = QtGui.QPixmap.fromImage(qim)
        return pix
