"""
Converts PLYFILE Point Clouds to the Open3D format
"""

import open3d as o3d
import numpy as np
from scipy.spatial.transform import Rotation


def _convert_quaternions_to_rot_matrix(quaternion):
    rotation = Rotation.from_quat(quaternion)
    return rotation.as_matrix()


def _convert_scaling_fac_to_matrix(scaling_fac):
    translate_mat = np.eye(3)
    np.fill_diagonal(translate_mat, scaling_fac)
    return translate_mat


def _convert_to_covariance_matrix(scaling_factors, quaternion):
    scaling_matrix = _convert_scaling_fac_to_matrix(scaling_factors)
    rotation_matrix = _convert_quaternions_to_rot_matrix(quaternion)
    transform_matrix = scaling_matrix @ rotation_matrix
    return transform_matrix


def _get_normals_from_covariance(covariance_mat):
    # Perform eigendecomposition
    eig_values, eig_vectors = np.linalg.eig(covariance_mat)

    # Sort eigenvectors by corresponding eigenvalues
    sorted_indices = np.argsort(eig_values)
    normals = eig_vectors[:, sorted_indices]

    # Normal corresponding to the smallest semi-axis (smallest eigenvalue)
    smallest_semiaxis_normal = normals[:, 0]

    imaginary_parts = np.imag(smallest_semiaxis_normal)
    if np.any(imaginary_parts != 0):
        smallest_semiaxis_normal = np.zeros(3)
    return smallest_semiaxis_normal


def convert_input_pc_to_open3d_pc(pc):
    o3d_pc = o3d.geometry.PointCloud()

    # Convert coordinates
    vertices = pc["vertex"]
    points = np.vstack([vertices['x'], vertices['y'], vertices['z']]).T
    o3d_pc.points.extend(points)
    reds = list(map(lambda x: x/255, vertices['red']))
    greens = list(map(lambda x: x/255, vertices['green']))
    blues = list(map(lambda x: x/255, vertices['blue']))

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
    points = np.vstack([vertices['x'], vertices['y'], vertices['z']]).T
    o3d_pc.points.extend(points)

    # Convert color data
    colors = colors = np.vstack([vertices['f_dc_0'], vertices['f_dc_1'], vertices['f_dc_2']]).T
    o3d_pc.colors.extend(colors)

    # convert scaling factors and quaternions to covariance matrix
    scaling = np.vstack([vertices['scale_0'], vertices['scale_1'], vertices['scale_2']]).T
    quaternions = np.vstack([vertices['rot_0'], vertices['rot_1'], vertices['rot_2'], vertices['rot_3']]).T
    o3d_pc.covariances.extend(map(_convert_to_covariance_matrix, scaling, quaternions))

    # get the normals from the covariance matrices
    o3d_pc.normals.extend(map(_get_normals_from_covariance, o3d_pc.covariances))

    o3d_pc.orient_normals_consistent_tangent_plane(30)
    return o3d_pc
