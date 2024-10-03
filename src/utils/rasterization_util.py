import math

import torch
from PySide6 import QtGui
from diff_gaussian_rasterization import GaussianRasterizer, GaussianRasterizationSettings
from gsplat.rendering import rasterization
import torchvision.transforms.functional as F

from src.models.gaussian_model import GaussianModel


def rasterize_image(point_cloud, camera, scale, color, device, leave_on_gpu=True):
    # Create zero tensor. We will use it to make pytorch return gradients of the 2D (screen-space) means
    screenspace_points = torch.zeros_like(point_cloud.get_xyz, dtype=point_cloud.get_xyz.dtype, requires_grad=False,
                                          device=device) + 0

    bg_color = torch.tensor(color, dtype=torch.float32, device=device)

    # Set up rasterization configuration
    tan_fov_x = math.tan(camera.FoVx * 0.5)
    tan_fov_y = math.tan(camera.FoVy * 0.5)

    raster_settings = GaussianRasterizationSettings(
        image_height=int(camera.height),
        image_width=int(camera.width),
        tanfovx=tan_fov_x,
        tanfovy=tan_fov_y,
        bg=bg_color,
        scale_modifier=scale,
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
    opacity = point_cloud.get_opacity_with_activation
    cov3D_precomp = point_cloud.get_covariance(scale)
    shs = point_cloud.get_features

    image_tensor, radii = rasterizer(
        means3D=means3D,
        means2D=means2D,
        shs=shs,
        opacities=opacity,
        cov3D_precomp=cov3D_precomp)

    if leave_on_gpu:
        return image_tensor.detach(), radii
    else:
        return image_tensor.detach().cpu(), radii


def rasterize_image_gsplat(point_cloud: GaussianModel, camera, scale, color, device, intrinsics, leave_on_gpu=True, ):
    color_tensor = torch.tensor(color, dtype=torch.float32, device=device)
    intrinsics_tensor = torch.tensor(intrinsics, dtype=torch.float32, device=device).view(1, 3, 3)
    render_colors, render_alphas, meta = rasterization(
        point_cloud.get_xyz,
        point_cloud.get_rotation,
        point_cloud.get_scaling,
        point_cloud.get_opacity_with_activation.view(-1),
        point_cloud.get_features,
        camera.viewmat.cuda(),
        intrinsics_tensor,
        camera.width,
        camera.height,
        render_mode="RGB",
        sh_degree=3,
        backgrounds=color_tensor.view(1, -1),
        covars=point_cloud.get_full_covariance_precomputed
    )

    return render_colors.detach() if leave_on_gpu else render_colors.cpu()


def get_pixmap_from_tensor(image_tensor):
    img_save = F.to_pil_image(image_tensor[0].permute(2, 0, 1).clamp(0, 1).detach().cpu())
    data = img_save.tobytes("raw")
    qim = QtGui.QImage(data, img_save.width, img_save.height, QtGui.QImage.Format.Format_RGB888)
    pix = QtGui.QPixmap.fromImage(qim)
    return pix
