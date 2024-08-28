#
# Copyright (C) 2023, Inria
# GRAPHDECO research group, https://team.inria.fr/graphdeco
# All rights reserved.
#
# This software is free for non-commercial, research and evaluation use 
# under the terms of the LICENSE.md file.
#
# For inquiries contact  george.drettakis@inria.fr
#

import math

import numpy as np
import torch


def get_normals_from_covariance(covariance_mat):
    eigen_values, eigen_vectors = torch.linalg.eigh(covariance_mat)
    min_eigenvalue_index = eigen_values.argsort()[:, 0]
    return eigen_vectors[torch.arange(eigen_values.shape[0]), :, min_eigenvalue_index]


def getWorld2View2(R, t, translate=np.array([.0, .0, .0]), scale=1.0):
    Rt = np.zeros((4, 4))
    Rt[:3, :3] = R.transpose()
    Rt[:3, 3] = t
    Rt[3, 3] = 1.0

    C2W = np.linalg.inv(Rt)
    cam_center = C2W[:3, 3]
    cam_center = (cam_center + translate) * scale
    C2W[:3, 3] = cam_center
    Rt = np.linalg.inv(C2W)
    return np.float32(Rt)


def getProjectionMatrix(znear, zfar, fovX, fovY):
    tanHalfFovY = math.tan((fovY / 2))
    tanHalfFovX = math.tan((fovX / 2))

    top = tanHalfFovY * znear
    bottom = -top
    right = tanHalfFovX * znear
    left = -right

    P = torch.zeros(4, 4)

    z_sign = 1.0

    P[0, 0] = 2.0 * znear / (right - left)
    P[1, 1] = 2.0 * znear / (top - bottom)
    P[0, 2] = (right + left) / (right - left)
    P[1, 2] = (top + bottom) / (top - bottom)
    P[3, 2] = z_sign
    P[2, 2] = z_sign * zfar / (zfar - znear)
    P[2, 3] = -(zfar * znear) / (zfar - znear)
    return P


def fov2focal(fov, pixels):
    return pixels / (2 * math.tan(fov / 2))


def focal2fov(focal, pixels):
    return 2 * math.atan(pixels / (2 * focal))


def get_focal_from_intrinsics(intrinsics):
    fx, fy = intrinsics[:2, :2].diagonal()
    return fx, fy


def fov_x2fov_y(fov_x, aspect_ratio):
    return 2 * math.atan(math.tan(fov_x / 2) / aspect_ratio)


def sh2rgb(sh):
    return sh * 0.28209479177387814 + 0.5


def get_camera_intrinsics(width, height, value, fov_type):
    fx = 0.0
    fy = 0.0
    match fov_type:
        case 0:
            return None
        case 1:
            # if value is greate than pi, the user entered the fov in degrees
            if value > math.pi:
                value = value * math.pi / 180
            fx = fov2focal(value, width)
            fy = fov2focal(value, height)
        case 2:
            # Approximate solution only.
            fx = value
            fov_x = focal2fov(fx, width)
            fov_y = fov_x2fov_y(fov_x, width / height)
            fy = fov2focal(fov_y, height)

    cx = width / 2
    cy = height / 2
    intrinsics = np.array([
        [fx, 0, cx],
        [0, fy, cy],
        [0, 0, 1]
    ])
    return intrinsics
