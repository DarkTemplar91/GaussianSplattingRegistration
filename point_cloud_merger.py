import numpy as np
import plyfile
from scipy.spatial.transform import Rotation

from point_cloud_converter import _convert_quaternions_to_rot_matrix


def merge_point_clouds(pc1, pc2, output_path, transformation_matrix=None):
    vertex_data1 = pc1["vertex"].data
    vertex_data2 = pc2["vertex"].data

    # calculate the new positions for the transformation if needed
    if transformation_matrix is not None:
        transform_point_cloud(pc1, transformation_matrix)

    out_vertex_data = np.concatenate([vertex_data1, vertex_data2])
    out_vertex_element = plyfile.PlyElement.describe(out_vertex_data, "vertex", len_types={}, val_types={}, comments=[])
    out_ply_data = plyfile.PlyData(text=False,  # binary
                                   byte_order='<',  # < stands for little endian
                                   elements=[out_vertex_element])
    plyfile.PlyData.write(out_ply_data, output_path)


# TODO: Change rotation as well (possibly the FPFHs as well)
# Maybe it's easier to actually convert back to plyfile format, instead of manipulating that directly
def transform_point_cloud(pc, transformation_matrix):
    vertex_data = pc["vertex"].data

    points = np.vstack([vertex_data['x'], vertex_data['y'], vertex_data['z'], np.ones(len(vertex_data['x']))]).T
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

    rotation_matrices = _convert_quaternions_to_rot_matrix(quaternions)

    # Extract the upper-left 3x3 submatrix of the affine transformation matrix (potential rotation matrix)
    potential_rotation_matrix = transformation_matrix[:3, :3]

    # Ensure it represents a rotation (orthogonalization)
    rotation_matrix = np.linalg.qr(potential_rotation_matrix)[0]
    rotation_matrices = np.dot(rotation_matrices, rotation_matrix)

    # Get back new quaternions
    rotations = Rotation.from_matrix(rotation_matrices)
    quaternions = rotations.as_quat(False)

    vertex_data['rot_0'] = quaternions[:, 3]
    vertex_data['rot_1'] = quaternions[:, 2]
    vertex_data['rot_2'] = quaternions[:, 1]
    vertex_data['rot_3'] = quaternions[:, 0]

