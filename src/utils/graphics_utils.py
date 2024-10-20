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
    eigen_values, eigen_vectors = torch.linalg.eig(covariance_mat)
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


# Inverse of getWorld2View2
def getView2World2(Rt, translate=np.array([.0, .0, .0]), scale=1.0):
    C2W = np.linalg.inv(Rt)
    cam_center = C2W[:3, 3]
    cam_center = cam_center / scale - translate
    C2W[:3, 3] = cam_center
    original_Rt = np.linalg.inv(C2W)
    R = original_Rt[:3, :3].transpose()
    t = original_Rt[:3, 3]
    return R, t


def fov2focal(fov, pixels):
    return pixels / (2 * math.tan(fov / 2))


def focal2fov(focal, pixels):
    return 2 * math.atan(pixels / (2 * focal))


def get_focal_from_intrinsics(intrinsics):
    fx, fy = intrinsics[:2, :2].diagonal()
    return fx, fy


def get_dimension_from_intrinsics(intrinsics):
    width, height = intrinsics[:2, 2]
    return int(width * 2), int(height * 2)


def fov_x2fov_y(fov_x, aspect_ratio):
    return 2 * math.atan(math.tan(fov_x / 2) / aspect_ratio)


def sh2rgb(sh):
    return sh * 0.28209479177387814 + 0.5


def get_camera_intrinsics(width, height, value, fov_type):
    fx, fy = get_focal_lengths(width, height, value, fov_type)

    cx = width / 2
    cy = height / 2
    intrinsics = np.array([
        [fx, 0, cx],
        [0, fy, cy],
        [0, 0, 1]
    ])
    return intrinsics


def get_focal_lengths(width, height, value, fov_type):
    fx = 0.0
    fy = 0.0
    match fov_type:
        case 0:
            return fx, fy
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

    return fx, fy
