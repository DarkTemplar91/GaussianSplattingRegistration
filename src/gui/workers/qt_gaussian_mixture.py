import copy
import sys

import numpy as np
import torch
from PyQt5.QtCore import QObject, pyqtSignal

from src.models.gaussian_mixture_level import GaussianMixtureLevel
from src.utils.math_util import kullback_leibler_distance, clamp


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
            weight = responsibility * current_mixture._weights[child]

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
            new_weights.append(current_mixture._weights[parent])
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
        new_weights.append(current_mixture._weights[i])
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

    return torch.pow(f, current_mixture._weights[child_index])


def compute_likelihood_contributions(parent_indices, child_indices, current_mixture):
    wl_cache = [[0] * current_mixture.xyz.shape[0] for _ in child_indices]
    sum_lw = [0] * current_mixture.xyz.shape[0]
    maxL = 1e8
    minL = sys.float_info.min
    for parent_index, parent in enumerate(parent_indices):
        for child in child_indices[parent_index]:
            likelihood = current_mixture._weights[parent] * clamp(
                __compute_hem_likelihood(parent, child, current_mixture), minL, maxL)
            wl_cache[parent_index][child] = likelihood
            sum_lw[child] += likelihood

    return wl_cache, sum_lw


class GaussianMixtureWorker(QObject):
    signal_finished = pyqtSignal()
    signal_mixture_created = pyqtSignal(object, object)

    def __init__(self, pc1, pc2, hem_reduction, distance_delta, color_delta, cluster_level):
        super().__init__()

        self.pc1 = pc1
        self.pc2 = pc2
        self.hem_reduction = hem_reduction
        self.distance_delta = distance_delta
        self.color_delta = color_delta
        self.cluster_level = cluster_level


    def create_mixture(self):
        """# filter for point like gaussians, and zero determinants
        non_zero_covariances = torch.all(self._covariance != 0, dim=(1, 2))
        determinants = torch.det(self._covariance)
        # selected_indices = torch.nonzero((determinants > 0) & non_zero_covariances, as_tuple=False).squeeze()
        selected_indices = torch.nonzero(non_zero_covariances, as_tuple=False).squeeze()

        self._covariance = self._covariance[selected_indices]
        self._xyz = self._xyz[selected_indices]
        self.colors = self.colors[selected_indices]
        self.opacities = self.opacities[selected_indices]"""

        self.execute(self.pc1)
        #self.execute(self.pc2)

    def execute(self, gaussian):
        # Use hash grid?
        selection_probability = 1 / self.hem_reduction  # Probability that a point gets selected to be a parent
        self.distance_delta = self.distance_delta
        self.color_delta = self.color_delta

        # TODO: numpy.linalg.norm(self._covariance) # filter small covariances
        current_mixture, parent_indices = self.__initialize_gaussians(gaussian, selection_probability)

        # Cluster
        for l in range(self.cluster_level):
            non_parent_indices = np.array([index for index in range(len(current_mixture.xyz)) if index not in parent_indices])

            child_indices = self.get_children_indices(parent_indices, non_parent_indices, current_mixture)

            wl_cache, sum_lw = compute_likelihood_contributions(parent_indices, child_indices, current_mixture)

            #compute responsibilities and update
            new_positions, new_covariances, new_weights, new_rgbs, new_opacities = update_parent_values(
                                                parent_indices, child_indices, sum_lw, wl_cache, current_mixture)

            #hand out new parent flags, create mixture
            random_numbers = torch.rand(len(new_positions))
            parent_indices = torch.nonzero(random_numbers < selection_probability).squeeze()
            current_mixture = GaussianMixtureLevel(torch.stack(new_positions), torch.stack(new_covariances),
                                                           torch.stack(new_rgbs), torch.stack(new_opacities),torch.stack(new_weights))

        return current_mixture


    def get_children_indices(self, parent_indices, non_parent_indices, current_mixture):
        child_indices = []

        for parent in parent_indices:
            child_array = []
            if torch.det(current_mixture.covariance[parent]) != 0:
                for child in non_parent_indices:
                    #TODO: Calculate batch-wise
                    kld = kullback_leibler_distance(
                        current_mixture.xyz[child], current_mixture.covariance[child],
                        current_mixture.xyz[parent], current_mixture.covariance[parent])

                    color_distance = (current_mixture.features_dc[parent] - current_mixture.features_dc[child]).pow(2).sum().sqrt()

                    # TODO: Filter for -inf?
                    if kld < self.distance_delta * self.distance_delta * 0.5 and color_distance < self.color_delta * self.color_delta * 0.5:
                        child_array.append(child)

            child_indices.append(child_array)

        return child_indices

    def __initialize_gaussians(self, gaussian, selection_probability):
        random_numbers = torch.rand(gaussian.get_xyz.shape[0])
        selected_indices = torch.nonzero(random_numbers < selection_probability).squeeze()

        return (GaussianMixtureLevel(gaussian.get_xyz,
                                     gaussian.get_covariance3D,
                                     gaussian.get_colors,
                                     gaussian.get_opacity, # TODO: Get real opacities
                                     torch.ones(gaussian.get_xyz.shape[0], device=gaussian.get_xyz.device)),
                selected_indices)



