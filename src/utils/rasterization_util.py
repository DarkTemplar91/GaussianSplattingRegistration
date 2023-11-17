import math

import torch
from diff_gaussian_rasterization import GaussianRasterizer, GaussianRasterizationSettings


def rasterize_image(point_cloud, camera, color, device):
    # Create zero tensor. We will use it to make pytorch return gradients of the 2D (screen-space) means
    screenspace_points = torch.zeros_like(point_cloud.get_xyz, dtype=point_cloud.get_xyz.dtype, requires_grad=True,
                                          device=device) + 0
    try:
        screenspace_points.retain_grad()
    except:
        pass

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
        scale_modifier=camera.scale,
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
    cov3D_precomp = point_cloud.get_covariance(camera.scale)
    shs = point_cloud.get_features

    image_tensor, radii = rasterizer(
        means3D=means3D,
        means2D=means2D,
        shs=shs,
        opacities=opacity,
        cov3D_precomp=cov3D_precomp)

    return image_tensor, radii