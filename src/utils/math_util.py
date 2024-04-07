import numpy as np
from e3nn import o3
import torch

def get_wigner_from_rotation(order, rotation_matrix):
    # Convert the rotation_matrix to a tensor
    rotation_matrix_tensor = torch.tensor(rotation_matrix, dtype=torch.float64)

    # Calculate the rotation angles using the tensor
    rot_angles = o3._rotation.matrix_to_angles(rotation_matrix_tensor)

    # Calculate the Wigner D matrix using the appropriate function
    wigner_d = o3.wigner_D(order, rot_angles[0], rot_angles[1], rot_angles[2])

    return wigner_d.numpy()
