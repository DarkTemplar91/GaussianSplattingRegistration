import torch
from PySide6 import QtGui
from gsplat.rendering import rasterization
import torchvision.transforms.functional as F

from src.models.gaussian_model import GaussianModel


def rasterize_image(point_cloud: GaussianModel, camera, scale, color, device, intrinsics, leave_on_gpu=True, ):
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
