"""
Converts PLYFILE Point Clouds to the Open3D format
"""

import open3d as o3d
import numpy as np

from src.utils.graphics_utils import get_normals_from_covariance, sh2rgb


def convert_input_pc_to_open3d_pc(pc):
    o3d_pc = o3d.geometry.PointCloud()

    # Convert coordinates
    vertices = pc["vertex"]
    points = np.vstack([vertices['x'], vertices['y'], vertices['z']]).T
    o3d_pc.points.extend(points)
    reds = list(map(lambda x: x / 255, vertices['red']))
    greens = list(map(lambda x: x / 255, vertices['green']))
    blues = list(map(lambda x: x / 255, vertices['blue']))

    # Convert color data
    colors = np.vstack([reds, greens, blues]).T
    o3d_pc.colors.extend(colors)

    o3d_pc.estimate_normals()

    o3d_pc.orient_normals_consistent_tangent_plane(30)
    return o3d_pc


def convert_gs_to_open3d_pc(gaussian):
    o3d_pc = o3d.geometry.PointCloud()
    points = gaussian.get_xyz.double().detach().cpu().numpy()

    o3d_pc.points = o3d.utility.Vector3dVector(points)

    colors = sh2rgb(np.ascontiguousarray(gaussian.get_colors.double().detach().cpu().numpy()))
    o3d_pc.colors = o3d.utility.Vector3dVector(colors)

    covariances_tensor = gaussian.get_full_covariance_precomputed
    o3d_pc.covariances = o3d.utility.Matrix3dVector(covariances_tensor.double().detach().cpu().numpy())

    normal_matrices = get_normals_from_covariance(covariances_tensor)
    o3d_pc.normals = o3d.utility.Vector3dVector(normal_matrices.double().detach().cpu().numpy())
    # o3d_pc.orient_normals_consistent_tangent_plane(30)

    return o3d_pc
