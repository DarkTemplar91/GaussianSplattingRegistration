import numpy as np
import plyfile

from src.utils.math_util import matrices_to_quaternions, convert_quaternions_to_rot_matrix, get_wigner_from_rotation


def save_merged_point_clouds(pc1, pc2, output_path, transformation_matrix=None):
    out_ply_data = merge_point_clouds(pc1, pc2, transformation_matrix)
    plyfile.PlyData.write(out_ply_data, output_path)


def merge_point_clouds(pc1, pc2, transformation_matrix=None):
    vertex_data1 = pc1["vertex"].data
    vertex_data2 = pc2["vertex"].data

    # calculate the new positions for the transformation if needed
    if transformation_matrix is not None:
        transform_point_cloud(pc2, transformation_matrix)

    out_vertex_data = np.concatenate([vertex_data1, vertex_data2])
    out_vertex_element = plyfile.PlyElement.describe(out_vertex_data, "vertex", len_types={}, val_types={},
                                                     comments=[])
    out_ply_data = plyfile.PlyData(text=False,  # binary
                                   byte_order='<',  # < stands for little endian
                                   elements=[out_vertex_element])

    return out_ply_data


# Not sure if this is actually needed.
def rotate_sh(pc, points, transformation_matrix):
    vertex_data = pc["vertex"].data

    # Read in the SH
    extra_f_names = [p.name for p in pc["vertex"].properties if p.name.startswith("f_rest_")]
    extra_f_names = sorted(extra_f_names, key=lambda x: int(x.split('_')[-1]))
    features_extra = np.zeros((points.shape[0], len(extra_f_names)))
    for idx, attr_name in enumerate(extra_f_names):
        features_extra[:, idx] = np.asarray(pc.elements[0][attr_name])
    # Reshape (P,F*SH_coeffs) to (P, F, SH_coeffs except DC)
    features_extra = features_extra.reshape((features_extra.shape[0], 3, 4 ** 2 - 1))

    # Calculate second and third order and multiply them by the rotation
    d_1 = transformation_matrix
    d_2 = get_wigner_from_rotation(2, transformation_matrix)
    d_3 = get_wigner_from_rotation(3, transformation_matrix)

    # Select the corresponding parts of the spherical harmonics matrix for each order
    spherical_harmonics_order1 = features_extra[:, :, :3]  # For J = 1
    spherical_harmonics_order2 = features_extra[:, :, 3:8]  # For J = 2
    spherical_harmonics_order3 = features_extra[:, :, 8:]  # For J = 3

    # Multiply each part with the corresponding Wigner D matrix
    rotated_harmonics_order1 = np.einsum('nij,jk->nik', spherical_harmonics_order1, d_1)
    rotated_harmonics_order2 = np.einsum('nij,jk->nik', spherical_harmonics_order2, d_2)
    rotated_harmonics_order3 = np.einsum('nij,jk->nik', spherical_harmonics_order3, d_3)

    features_extra = np.concatenate((rotated_harmonics_order1,
                                     rotated_harmonics_order2,
                                     rotated_harmonics_order3), axis=2)

    features_transposed = np.transpose(features_extra, (0, 2, 1))
    features_flattened = features_transposed.reshape(features_transposed.shape[0], -1)

    for idx, attr_name in enumerate(extra_f_names):
        vertex_data[attr_name] = features_flattened[:, idx]


def transform_point_cloud(pc, transformation_matrix):
    vertex_data = pc["vertex"].data

    points = np.vstack([vertex_data['x'], vertex_data['y'], vertex_data['z'], np.ones(vertex_data["x"].shape)]).T
    transformed_points = np.dot(transformation_matrix, points.T).T[:, :3]

    # Update the coordinates in the PLY data
    vertex_data['x'] = transformed_points[:, 0]
    vertex_data['y'] = transformed_points[:, 1]
    vertex_data['z'] = transformed_points[:, 2]

    # Get quaternions and convert them to rotation matrices
    rot_names = [p.name for p in pc["vertex"].properties if p.name.startswith("rot")]
    rot_names = sorted(rot_names, key=lambda x: int(x.split('_')[-1]))
    quaternions = np.zeros((points.shape[0], len(rot_names)))
    for idx, attr_name in enumerate(rot_names):
        quaternions[:, idx] = np.asarray(pc.elements[0][attr_name])

    new_rotation = convert_quaternions_to_rot_matrix(quaternions)
    new_rotation = transformation_matrix[:3, :3] @ new_rotation

    # Get back new quaternions
    quaternions = matrices_to_quaternions(new_rotation)

    vertex_data['rot_0'] = quaternions[:, 0]
    vertex_data['rot_1'] = quaternions[:, 1]
    vertex_data['rot_2'] = quaternions[:, 2]
    vertex_data['rot_3'] = quaternions[:, 3]
