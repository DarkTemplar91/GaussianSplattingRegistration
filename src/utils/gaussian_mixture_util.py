import sys

import numpy as np
import torch

from src.utils.math_util import clamp


def update_parent_values(parent_indices, child_indices, sum_lw, wl_cache, current_mixture):
    new_positions = []
    new_covariances = []
    new_weights = []
    new_rgbs = []
    new_opacities = []
    for parent_index, parent in enumerate(parent_indices):

        sum_weight = 0
        sum_pos = torch.zeros(3, device="cuda:0")
        sum_cov = torch.zeros(3, 3, device="cuda:0")
        sum_colors = torch.zeros(3, device="cuda:0")
        sum_opacities = 0
        for child in child_indices[parent_index]:

            if sum_lw[child] == 0:
                continue

            responsibility = wl_cache[parent_index][child] / sum_lw[child]
            weight = responsibility * current_mixture.weight[child]

            # accumulate
            sum_weight += weight
            sum_pos += weight * current_mixture.xyz[child]
            sum_cov += weight * current_mixture.covariance[child]
            sum_colors += weight * current_mixture.features_dc[child]
            sum_opacities += weight * current_mixture.opacity[child]

        # if all zero, use the current parent values
        if sum_weight == 0:
            new_positions.append(current_mixture.xyz[parent])
            new_covariances.append(current_mixture.covariance[parent])
            new_weights.append(current_mixture.weight[parent])
            new_rgbs.append(current_mixture.features_dc[parent])
            new_opacities.append(current_mixture.opacity[parent])
            continue

        # normalize
        inv_weight = 1 / sum_weight
        new_pos = inv_weight * sum_pos
        new_cov = inv_weight * sum_cov  # TODO: Condition?
        sum_colors = inv_weight * sum_colors
        sum_opacities = inv_weight * sum_opacities

        new_positions.append(new_pos)
        new_covariances.append(new_cov)
        new_weights.append(sum_weight)
        new_rgbs.append(sum_colors)
        new_opacities.append(sum_opacities)

    for i in range(current_mixture.xyz.shape[0]):
        if sum_lw[i] != 0 or i in parent_indices:
            continue

        new_positions.append(current_mixture.xyz[i])
        new_covariances.append(current_mixture.covariance[i])
        new_weights.append(current_mixture.weight[i])
        new_rgbs.append(current_mixture.features_dc[i])
        new_opacities.append(current_mixture.opacity[i])

    return new_positions, new_covariances, new_weights, new_rgbs, new_opacities


def __compute_hem_likelihood(parent_index, child_index, current_mixture):
    if torch.det(current_mixture.covariance[parent_index]) == 0:
        return 0

    diff = current_mixture.xyz[parent_index] - current_mixture.xyz[child_index]
    parent_precision_matrix = torch.inverse(current_mixture.covariance[parent_index])

    temp = torch.matmul(diff, parent_precision_matrix)
    smd = torch.sum(diff * temp)
    intermediate_matrices = torch.matmul(parent_precision_matrix, current_mixture.covariance[child_index])
    ipcTrace = torch.trace(intermediate_matrices)

    e = -0.5 * (smd + ipcTrace)
    # 1 / ((2pi) ^ (3 / 2)) * sqrt( | Sigma1 |) ^ -1 = sqrt( | Sigma1 ^ -1 |)   *e ^ exponent
    f = 0.063493635934241 * torch.sqrt(torch.det(parent_precision_matrix)) * torch.exp(e)

    return torch.pow(f, current_mixture.weight[child_index])


def compute_likelihood_contributions(parent_indices, child_indices, current_mixture):
    wl_cache = [[0] * current_mixture.xyz.shape[0] for _ in child_indices]
    sum_lw = [0] * current_mixture.xyz.shape[0]
    maxL = 1e8
    minL = sys.float_info.min
    for parent_index, parent in enumerate(parent_indices):
        for child in child_indices[parent_index]:
            likelihood = current_mixture.weight[parent] * clamp(
                __compute_hem_likelihood(parent, child, current_mixture), minL, maxL)
            wl_cache[parent_index][child] = likelihood
            sum_lw[child] += likelihood

    return wl_cache, sum_lw


def filter_search_tree(pcd_tree, open3d_point, non_parent_indices, search_radius):
    _, filtered_indices, _ = pcd_tree.search_knn_vector_3d (open3d_point, 200)
    filtered_indices_tensor = torch.tensor(list(filtered_indices))
    filtered_non_parent_indices = np.intersect1d(filtered_indices_tensor, non_parent_indices)
    return filtered_non_parent_indices