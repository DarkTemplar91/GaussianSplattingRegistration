import concurrent.futures

import torch
from PyQt5.QtCore import QObject, pyqtSignal

from src.models.gaussian_mixture_level import GaussianMixtureLevel
from src.utils.math_util import kullback_leibler_distance_batch
import open3d as o3d

class GaussianMixtureWorker(QObject):
    signal_finished = pyqtSignal()
    signal_mixture_created = pyqtSignal(object, object)

    signal_update_progress = pyqtSignal(int)

    def __init__(self, pc1, pc2, o3pc1, o3pc2, hem_reduction, distance_delta, color_delta, cluster_level):
        super().__init__()

        self.hem_reduction = hem_reduction
        self.distance_delta = distance_delta
        self.color_delta = color_delta
        self.cluster_level = cluster_level

        self.gaussian_pc_first = pc1
        self.gaussian_pc_second = pc2
        self.open3d_pc_first = o3pc1
        self.open3d_pc_first = o3pc2

        self.current_progress = 0
        self.max_progress = self.get_approx_max_progress()
        self.max_progress = 80000


    def create_mixture(self):
        self.execute(self.gaussian_pc_first, self.open3d_pc_first)
        #self.execute(self.gaussian_point_clouds_second[0])

    def execute(self, gaussian_pc, open3d_pc):
        gaussian_pcs = [gaussian_pc]
        open3d_pcs = [open3d_pc]

        selection_probability = 1 / self.hem_reduction  # Probability that a point gets selected to be a parent
        self.distance_delta = self.distance_delta
        self.color_delta = self.color_delta

        # TODO: numpy.linalg.norm(self._covariance) # filter small covariances
        current_mixture, parent_indices, non_parent_indices = self.__initialize_gaussians(gaussian_pc, selection_probability)

        # Cluster
        for l in range(self.cluster_level):
            pcd_tree = o3d.geometry.KDTreeFlann(open3d_pcs[l])
            child_indices = self.get_children_indices(parent_indices, non_parent_indices, current_mixture, pcd_tree, open3d_pcs[l])

            print("Done")
            """wl_cache, sum_lw = compute_likelihood_contributions(parent_indices, child_indices, current_mixture)

            #compute responsibilities and update
            new_positions, new_covariances, new_weights, new_rgbs, new_opacities = update_parent_values(
                                                parent_indices, child_indices, sum_lw, wl_cache, current_mixture)

            #hand out new parent flags, create mixture
            random_numbers = torch.rand(len(new_positions))
            parent_indices = torch.nonzero(random_numbers < selection_probability).squeeze()
            current_mixture = GaussianMixtureLevel(torch.stack(new_positions), torch.stack(new_covariances),
                                                           torch.stack(new_rgbs), torch.stack(new_opacities),torch.stack(new_weights))"""

        return current_mixture

    def get_children_indices(self, parent_indices, non_parent_indices, current_mixture, pcd_tree, open3d_pc):
        #TODO: Maybe use the search radii and the kd-tree
        """search_radii = torch.sqrt(torch.linalg.eigvalsh(current_mixture.covariance)[..., -1]) * self.distance_delta
        filtered_non_parent_indices = filter_search_tree(pcd_tree, open3d_pc.points[parent_index], non_parent_indices, search_radii[idx])"""

        def calculate_single_kld(parent_index):
            xyz_parent = current_mixture.xyz[parent_index]
            covariance_parent = current_mixture.covariance[parent_index]
            xyz_children = current_mixture.xyz[non_parent_indices]
            covariance_children = current_mixture.covariance[non_parent_indices]

            kld = kullback_leibler_distance_batch(xyz_children, covariance_children, xyz_parent, covariance_parent)
            mask_kld = (kld < self.distance_delta * self.distance_delta * 0.5).detach().cpu()
            child_indices_inner = non_parent_indices[mask_kld]
            return parent_index, child_indices_inner

        child_indices = [None] * len(parent_indices)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(calculate_single_kld, parent_index): parent_index for parent_index in
                       parent_indices}
            for future in concurrent.futures.as_completed(futures):
                parent_index, indices = future.result()
                child_indices[parent_index] = indices
                self.update_progress()

        return child_indices

    def handle_index_results(self):
        pass

    @staticmethod
    def __initialize_gaussians(gaussian, selection_probability):
        random_numbers = torch.rand(gaussian.get_xyz.shape[0])
        mask = random_numbers < selection_probability
        parent_indices = torch.nonzero(mask).squeeze()
        non_parent_indices = torch.nonzero(~mask).squeeze()

        return (GaussianMixtureLevel(gaussian.get_xyz,
                                     gaussian.get_covariance3D,
                                     gaussian.get_colors,
                                     gaussian.get_raw_opacity,
                                     torch.ones(gaussian.get_xyz.shape[0], device=gaussian.get_xyz.device)),
                parent_indices, non_parent_indices)



    def update_progress(self):
        self.current_progress += 1
        new_percent = int(self.current_progress / self.max_progress * 100)
        self.signal_update_progress.emit(new_percent)

    def get_approx_max_progress(self):
        num_points = ((self.gaussian_pc_first.get_xyz.shape[0] if self.gaussian_pc_first is not None else 0) +
                      (self.gaussian_pc_second.get_xyz.shape[0] if self.gaussian_pc_second is not None else 0))
        selection_probability = 1 / self.hem_reduction

        return int(num_points * (1-selection_probability**(self.cluster_level + 1)) / (1-selection_probability) - num_points)
