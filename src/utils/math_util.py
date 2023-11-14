import numpy as np
from e3nn import o3
import torch


def get_normals_from_covariance(covariance_mat):
    eigen_values, eigen_vectors = np.linalg.eigh(covariance_mat)
    min_eigenvalue_index = np.argmin(eigen_values, axis=1)
    return eigen_vectors[np.arange(len(eigen_values)), :, min_eigenvalue_index]


def convert_to_covariance_matrix(scaling_factors, quaternion):
    scaling_matrices = np.zeros((scaling_factors.shape[0], 3, 3), dtype=float)
    rotation_matrices = convert_quaternions_to_rot_matrix(quaternion)

    scaling_matrices[:, 0, 0] = scaling_factors[:, 0]
    scaling_matrices[:, 1, 1] = scaling_factors[:, 1]
    scaling_matrices[:, 2, 2] = scaling_factors[:, 2]

    scaling_matrices = rotation_matrices @ scaling_matrices

    covariance_matrix = scaling_matrices @ scaling_matrices.transpose(0, 2, 1)
    return covariance_matrix


def convert_quaternions_to_rot_matrix(quaternions):
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


def matrices_to_quaternions(rotation_matrices):
    trace = np.trace(rotation_matrices, axis1=1, axis2=2)
    w = np.sqrt(1 + trace) / 2
    x = (rotation_matrices[:, 2, 1] - rotation_matrices[:, 1, 2]) / (4 * w)
    y = (rotation_matrices[:, 0, 2] - rotation_matrices[:, 2, 0]) / (4 * w)
    z = (rotation_matrices[:, 1, 0] - rotation_matrices[:, 0, 1]) / (4 * w)
    return np.stack((w, x, y, z), axis=-1)


def get_wigner_from_rotation(order, rotation_matrix):
    # Convert the rotation_matrix to a tensor
    rotation_matrix_tensor = torch.tensor(rotation_matrix, dtype=torch.float64)

    # Calculate the rotation angles using the tensor
    rot_angles = o3._rotation.matrix_to_angles(rotation_matrix_tensor)

    # Calculate the Wigner D matrix using the appropriate function
    wigner_d = o3.wigner_D(order, rot_angles[0], rot_angles[1], rot_angles[2])

    return wigner_d.numpy()


def sh2rgb(sh):
    return sh * 0.28209479177387814 + 0.5
