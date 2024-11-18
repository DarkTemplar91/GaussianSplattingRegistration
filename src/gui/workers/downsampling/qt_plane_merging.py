import mixture_bind
from PySide6 import QtWidgets

from src.gui.workers.qt_base_worker import BaseWorker
from src.models.gaussian_mixture_level import GaussianMixtureModel
from src.models.gaussian_model import GaussianModel
from src.utils.point_cloud_converter import convert_gs_to_open3d_pc


def initialize_mixture_storage(cluster_level):
    """Initialize storage for mixture data across all levels."""
    return ([[] for _ in range(cluster_level)],  # xyz
            [[] for _ in range(cluster_level)],  # colors
            [[] for _ in range(cluster_level)],  # opacities
            [[] for _ in range(cluster_level)],  # covariance
            [[] for _ in range(cluster_level)])  # features


def process_all_planes(pc, plane_indices_list, xyz, colors, opacities, covariance, features,
                       cluster_level, hem_reduction, distance_delta, color_delta, decay_rate,
                       update_progress, signal_cancel):
    """Process all planes in a point cloud."""
    for indices in plane_indices_list:
        mixture_level = process_plane(pc, indices)
        mixture_models = mixture_bind.MixtureCreator.CreateMixture(
            cluster_level, hem_reduction, distance_delta, color_delta, decay_rate, mixture_level
        )

        # Append data for each depth
        for depth, mixture in enumerate(mixture_models):
            xyz_d, colors_d, opacities_d, covariance_d, features_d = mixture_bind.MixtureLevel.CreatePythonLists(
                mixture)
            xyz[depth].extend(xyz_d)
            colors[depth].extend(colors_d)
            opacities[depth].extend(opacities_d)
            covariance[depth].extend(covariance_d)
            features[depth].extend(features_d)

        update_progress()
        QtWidgets.QApplication.processEvents()
        if signal_cancel:
            return


def create_models_from_mixture(xyz_list, colors_list, opacities_list, covariance_list, features_list):
    """Create Gaussian models and Open3D point clouds from mixture data."""
    gaussian_models = []
    open3d_point_clouds = []

    for depth in range(len(xyz_list)):
        if not xyz_list[depth]:
            continue  # Skip empty depths

        # Create Gaussian model
        mixture_model = GaussianMixtureModel(
            xyz_list[depth], colors_list[depth], opacities_list[depth],
            covariance_list[depth], features_list[depth]
        )
        gaussian = GaussianModel(device_name="cuda:0")
        gaussian.from_mixture(mixture_model)
        gaussian.move_to_device("cpu")

        # Convert to Open3D point cloud
        result_open3d = convert_gs_to_open3d_pc(gaussian)

        gaussian_models.append(gaussian)
        open3d_point_clouds.append(result_open3d)

    return gaussian_models, open3d_point_clouds


def process_plane(pc, plane_indices):
    """Process a single plane to extract Gaussian Mixture Level data."""
    plane_points_xyz = pc.get_xyz[plane_indices].detach().cpu().tolist()
    plane_colors = pc.get_colors[plane_indices].detach().cpu().tolist()
    plane_opacity = pc.get_raw_opacity[plane_indices].view(-1).detach().cpu().tolist()
    plane_covariance = pc.get_covariance(1)[plane_indices].detach().cpu().tolist()
    plane_spherical_harmonics = pc.get_spherical_harmonics[plane_indices].detach().cpu().tolist()

    return mixture_bind.MixtureLevel.CreateMixtureLevel(
        plane_points_xyz, plane_colors, plane_opacity,
        plane_covariance, plane_spherical_harmonics
    )


class PlaneMergingWorker(BaseWorker):
    class ResultData:
        def __init__(self, list_gaussian_first, list_gaussian_second,
                     list_open3d_first, list_open3d_second):
            self.list_gaussian_first = list_gaussian_first
            self.list_gaussian_second = list_gaussian_second
            self.list_open3d_first = list_open3d_first
            self.list_open3d_second = list_open3d_second

    def __init__(self, pc1, pc2, first_plane_indices, second_plane_indices):
        super().__init__()

        self.hem_reduction = 3.0
        self.distance_delta = 2.5
        self.color_delta = 2.5
        self.decay_rate = 1.0
        self.cluster_level = 3

        self.first_plane_indices = first_plane_indices
        self.second_plane_indices = second_plane_indices

        self.gaussian_pc_first = pc1
        self.gaussian_pc_second = pc2

        self.current_progress = 0
        self.max_progress = 6
        self.signal_cancel = False

    def run(self):
        QtWidgets.QApplication.processEvents()
        if self.signal_cancel:
            self.signal_finished.emit()
            return

        print("Processing planes for the first point cloud.")
        xyz_first, colors_first, opacities_first, covariance_first, features_first = initialize_mixture_storage(
            self.cluster_level)

        # Process the first point cloud
        process_all_planes(
            self.gaussian_pc_first,
            self.first_plane_indices,
            xyz_first, colors_first, opacities_first, covariance_first, features_first,
            self.cluster_level, self.hem_reduction, self.distance_delta, self.color_delta, self.decay_rate,
            self.update_progress, self.signal_cancel
        )

        print("Processing planes for the second point cloud.")
        xyz_second, colors_second, opacities_second, covariance_second, features_second = initialize_mixture_storage(
            self.cluster_level)

        # Process the second point cloud
        process_all_planes(
            self.gaussian_pc_second,
            self.second_plane_indices,
            xyz_second, colors_second, opacities_second, covariance_second, features_second,
            self.cluster_level, self.hem_reduction, self.distance_delta, self.color_delta, self.decay_rate,
            self.update_progress, self.signal_cancel
        )

        print("Creating final Gaussian models.")
        list_gaussian_first, list_open3d_first = create_models_from_mixture(xyz_first, colors_first, opacities_first,
                                                                            covariance_first, features_first)
        list_gaussian_second, list_open3d_second = create_models_from_mixture(xyz_second, colors_second,
                                                                              opacities_second, covariance_second,
                                                                              features_second)

        self.signal_result.emit(PlaneMergingWorker.ResultData(
            list_gaussian_first, list_gaussian_second,
            list_open3d_first, list_open3d_second
        ))
        self.signal_finished.emit()

    def update_progress(self):
        self.current_progress += 1
        new_percent = int(self.current_progress / self.max_progress * 100)
        self.signal_progress.emit(new_percent)

    def cancel(self):
        self.signal_cancel = True
