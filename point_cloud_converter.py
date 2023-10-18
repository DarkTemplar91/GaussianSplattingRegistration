"""
Converts PLYFILE Point Clouds to the Open3D format
"""

import open3d as o3d
import numpy as np

from math_util import get_normals_from_covariance, convert_to_covariance_matrix


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

    covariance_matrices = convert_to_covariance_matrix(scaling, quaternions)
    o3d_pc.covariances.extend(covariance_matrices)

    # get the normals from the covariance matrices
    normal_matrices = get_normals_from_covariance(np.asarray(o3d_pc.covariances))
    o3d_pc.normals.extend(normal_matrices)

    o3d_pc.orient_normals_consistent_tangent_plane(30)
    return o3d_pc
