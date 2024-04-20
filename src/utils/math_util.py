import math
from time import time

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

def kullback_leibler_distance(child_xyz, child_covariance, parent_xyz, parent_covariance):
    """Edge cases to consider:
        * covariance with negative determinant or zero --> leads to NaN or inf resp.
        * covariance of zero --> trace term is zero. Leads to inf. Should we ignore these?"""

    # TODO: Filter small norms frobenius
    # TODO: Saját értékek (eigvals) --> filter < epsilon
    smd = squared_mahalanobis_distance(child_xyz, child_covariance, parent_xyz)
    trace_term = torch.trace(torch.inverse(parent_covariance) @ child_covariance)
    parent_det = torch.det(parent_covariance)
    child_det = torch.det(child_covariance)
    """if parent_det <= 0:
        print(parent_det)
        return math.inf

    if child_det <= 0:
        print(child_det)
        return math.inf"""

    det_term = torch.log(torch.abs(child_det / parent_det))

    kld = 0.5 * (smd.double() + trace_term.double() - 3.0 - det_term.double())

    if kld < 0:
        return math.inf

    return kld

def kullback_leibler_distance_batch(children_xyz, children_covariance, parent_xyz, parent_covariance):
    # Calculate squared Mahalanobis distance for all children
    smd = squared_mahalanobis_distance_batch(children_xyz, children_covariance, parent_xyz)

    # Calculate trace term for all children
    trace_terms = torch.linalg.solve(parent_covariance, children_covariance).diagonal(offset=0, dim1=-1, dim2=-2).sum(-1)
    # Calculate determinant terms for all children
    parent_det = torch.det(parent_covariance)
    child_dets = torch.det(children_covariance)
    det_terms = torch.log(child_dets / parent_det)

    # Calculate KLD for all children
    kld = 0.5 * (smd.double() + trace_terms.double() - 3.0 - det_terms.double())

    return kld

def squared_mahalanobis_distance(child_xyz, child_covariance, parent_xyz):
    diff = child_xyz - parent_xyz
    covariance_inv = torch.torch.linalg.inv_ex(child_covariance).inverse
    return torch.matmul(torch.matmul(diff.unsqueeze(0), covariance_inv), diff.unsqueeze(-1)).squeeze()

def squared_mahalanobis_distance_batch(children_xyz, children_covariance, parent_xyz):
    diff = children_xyz - parent_xyz
    solve_part = torch.linalg.solve(children_covariance, diff)
    return torch.sum(diff * solve_part, dim=-1)

def clamp(val, minval, maxval):
    if val != val: return 1
    if val < minval: return minval
    if val > maxval: return maxval
    return val
