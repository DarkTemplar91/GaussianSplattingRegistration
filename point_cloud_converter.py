"""
Converts PLYFILE Point Clouds to the Open3D format
"""

import open3d as o3d
import numpy as np


def _convert_quaternions_to_rot_matrix(quaternions):
    # find normals of the quaternions
    norm = np.sqrt(quaternions[:, 0] ** 2 + quaternions[:, 1] ** 2 +
                   quaternions[:, 2] ** 2 + quaternions[:, 3] ** 2)

    # normalize quaternions
    q = quaternions / norm[:, None]

    rotation_mat = np.zeros((q.shape[0], 3, 3))

    r = q[:, 0]
    x = q[:, 1]
    y = q[:, 2]
    z = q[:, 3]

    # convert quaternions to rotation mat
    rotation_mat[:, 0, 0] = 1 - 2 * (y * y + z * z)
    rotation_mat[:, 0, 1] = 2 * (x * y - r * z)
    rotation_mat[:, 0, 2] = 2 * (x * z + r * y)
    rotation_mat[:, 1, 0] = 2 * (x * y + r * z)
    rotation_mat[:, 1, 1] = 1 - 2 * (x * x + z * z)
    rotation_mat[:, 1, 2] = 2 * (y * z - r * x)
    rotation_mat[:, 2, 0] = 2 * (x * z - r * y)
    rotation_mat[:, 2, 1] = 2 * (y * z + r * x)
    rotation_mat[:, 2, 2] = 1 - 2 * (x * x + y * y)

    return rotation_mat


def _convert_to_covariance_matrix(scaling_factors, quaternion):
    scaling_matrices = np.zeros((scaling_factors.shape[0], 3, 3), dtype=float)
    rotation_matrices = _convert_quaternions_to_rot_matrix(quaternion)

    scaling_matrices[:, 0, 0] = scaling_factors[:, 0]
    scaling_matrices[:, 1, 1] = scaling_factors[:, 1]
    scaling_matrices[:, 2, 2] = scaling_factors[:, 2]

    scaling_matrices = rotation_matrices @ scaling_matrices

    covariance_matrix = scaling_matrices @ scaling_matrices.transpose(0, 2, 1)
    return covariance_matrix


def _get_normals_from_covariance(covariance_mat):
    eigen_values, eigen_vectors = np.linalg.eigh(covariance_mat)
    min_eigenvalue_index = np.argmin(eigen_values, axis=1)
    return eigen_vectors[np.arange(len(eigen_values)), :, min_eigenvalue_index]


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


def convert_pc_to_open3d_pc(pc):
    o3d_pc = o3d.geometry.PointCloud()

    # Convert coordinates
    vertices = pc["vertex"]
    points = np.stack((np.asarray(pc.elements[0]["x"]),
                       np.asarray(pc.elements[0]["y"]),
                       np.asarray(pc.elements[0]["z"])), axis=1)
    o3d_pc.points.extend(points)

    # Convert color data
    colors = colors = np.vstack([vertices['f_dc_0'], vertices['f_dc_1'], vertices['f_dc_2']]).T
    o3d_pc.colors.extend(colors)

    scale_names = [p.name for p in vertices.properties if p.name.startswith("scale_")]
    scale_names = sorted(scale_names, key=lambda x: int(x.split('_')[-1]))
    scaling = np.zeros((points.shape[0], len(scale_names)))
    for idx, attr_name in enumerate(scale_names):
        scaling[:, idx] = np.asarray(vertices[attr_name])

    rot_names = [p.name for p in vertices.properties if p.name.startswith("rot")]
    rot_names = sorted(rot_names, key=lambda x: int(x.split('_')[-1]))
    quaternions = np.zeros((points.shape[0], len(rot_names)))
    for idx, attr_name in enumerate(rot_names):
        quaternions[:, idx] = np.asarray(pc.elements[0][attr_name])

    covariance_matrices = _convert_to_covariance_matrix(scaling, quaternions)
    o3d_pc.covariances.extend(covariance_matrices)

    # get the normals from the covariance matrices
    normal_matrices = _get_normals_from_covariance(np.asarray(o3d_pc.covariances))
    o3d_pc.normals.extend(normal_matrices)

    o3d_pc.orient_normals_consistent_tangent_plane(30)
    return o3d_pc
