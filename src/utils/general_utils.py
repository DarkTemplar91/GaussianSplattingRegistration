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

import numpy as np
import torch


def inverse_sigmoid(x):
    return torch.log(x / (1 - x))


def strip_lowerdiag(L):
    uncertainty = torch.zeros((L.shape[0], 6), dtype=torch.float, device="cuda")

    uncertainty[:, 0] = L[:, 0, 0]
    uncertainty[:, 1] = L[:, 0, 1]
    uncertainty[:, 2] = L[:, 0, 2]
    uncertainty[:, 3] = L[:, 1, 1]
    uncertainty[:, 4] = L[:, 1, 2]
    uncertainty[:, 5] = L[:, 2, 2]
    return uncertainty


def rebuild_lowerdiag(covariance):
    row1 = covariance[:, [0, 1, 2]]
    row2 = covariance[:, [1, 3, 4]]
    row3 = covariance[:, [2, 4, 5]]

    # Stack the rows to create the covariance matrix
    covariance_matrix = torch.stack([row1, row2, row3], dim=1)

    return covariance_matrix


def strip_symmetric(sym):
    return strip_lowerdiag(sym)


def build_rotation(r):
    norm = torch.sqrt(r[:, 0] * r[:, 0] + r[:, 1] * r[:, 1] + r[:, 2] * r[:, 2] + r[:, 3] * r[:, 3])

    q = r / norm[:, None]

    R = torch.zeros((q.size(0), 3, 3), device='cuda')

    r = q[:, 0]
    x = q[:, 1]
    y = q[:, 2]
    z = q[:, 3]

    R[:, 0, 0] = 1 - 2 * (y * y + z * z)
    R[:, 0, 1] = 2 * (x * y - r * z)
    R[:, 0, 2] = 2 * (x * z + r * y)
    R[:, 1, 0] = 2 * (x * y + r * z)
    R[:, 1, 1] = 1 - 2 * (x * x + z * z)
    R[:, 1, 2] = 2 * (y * z - r * x)
    R[:, 2, 0] = 2 * (x * z - r * y)
    R[:, 2, 1] = 2 * (y * z + r * x)
    R[:, 2, 2] = 1 - 2 * (x * x + y * y)
    return R


def build_scaling_rotation(s, r):
    L = torch.zeros((s.shape[0], 3, 3), dtype=torch.float, device="cuda")
    R = build_rotation(r)

    L[:, 0, 0] = s[:, 0]
    L[:, 1, 1] = s[:, 1]
    L[:, 2, 2] = s[:, 2]

    L = R @ L
    return L


def convert_to_camera_transform(rot, pos):
    W2C = np.zeros((4, 4))
    W2C[:3, 3] = pos
    W2C[:3, :3] = rot
    W2C[3, 3] = 1.0
    Rt = np.linalg.inv(W2C)
    R = Rt[:3, :3].transpose()
    T = Rt[:3, 3]
    return R, T


def matrices_to_quaternions(rotation_matrices):
    trace = torch.vmap(torch.trace)(rotation_matrices)
    w = torch.sqrt(1 + trace) / 2
    x = (rotation_matrices[:, 2, 1] - rotation_matrices[:, 1, 2]) / (4 * w)
    y = (rotation_matrices[:, 0, 2] - rotation_matrices[:, 2, 0]) / (4 * w)
    z = (rotation_matrices[:, 1, 0] - rotation_matrices[:, 0, 1]) / (4 * w)
    return torch.stack((w, x, y, z), dim=-1)
