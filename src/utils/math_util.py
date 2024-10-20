import numpy as np
from e3nn import o3
import torch


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


def get_wigner_from_rotation(order, rotation_matrix):
    # Convert the rotation_matrix to a tensor
    rotation_matrix_tensor = torch.tensor(rotation_matrix, dtype=torch.float64)

    # Calculate the rotation angles using the tensor
    rot_angles = o3._rotation.matrix_to_angles(rotation_matrix_tensor)

    # Calculate the Wigner D matrix using the appropriate function
    wigner_d = o3.wigner_D(order, rot_angles[0], rot_angles[1], rot_angles[2])

    return wigner_d.numpy()


def look_at(eye, lookat, up, zoom):
    # Normalize vectors
    front = np.subtract(lookat, eye)
    front = front / np.linalg.norm(front)

    # Compute the new eye position based on zoom and front direction
    eye = lookat - front * zoom

    # Calculate the z-axis (negative front vector)
    z_axis = (eye - lookat)
    z_axis /= np.linalg.norm(z_axis)

    # Calculate the x-axis (cross product of up and z-axis)
    x_axis = np.cross(up, z_axis)
    x_axis /= np.linalg.norm(x_axis)

    # Calculate the y-axis (cross product of z-axis and x-axis)
    y_axis = np.cross(z_axis, x_axis)

    # Create the view matrix
    view_matrix = np.array([
        [x_axis[0], x_axis[1], x_axis[2], -np.dot(x_axis, eye)],
        [y_axis[0], y_axis[1], y_axis[2], -np.dot(y_axis, eye)],
        [z_axis[0], z_axis[1], z_axis[2], -np.dot(z_axis, eye)],
        [0, 0, 0, 1]
    ])

    return view_matrix
