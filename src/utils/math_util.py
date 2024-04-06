import numpy as np
from e3nn import o3
import torch

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
