import copy

from PyQt5.QtCore import QObject, pyqtSignal

from src.models.registration_data import MultiScaleRegistrationData
from src.utils.file_loader import load_sparse_pc
from src.utils.local_registration_util import do_icp_registration

import open3d as o3d


class MultiScaleRegistrator(QObject):
    signal_finished = pyqtSignal()
    signal_registration_done = pyqtSignal(object, object)
    signal_error_occurred = pyqtSignal(list)

    def __init__(self, pc1, pc2, init_trans, use_corresponding, sparse_first, sparse_second, registration_type,
                 relative_fitness, relative_rmse, voxel_values, iter_values, rejection_type, k_value):
        super().__init__()

        self.pc1 = copy.deepcopy(pc1)
        self.pc2 = copy.deepcopy(pc2)
        self.init_trans = init_trans
        self.use_corresponding = use_corresponding
        self.sparse_first_path = sparse_first
        self.sparse_second_path = sparse_second
        self.registration_type = registration_type
        self.relative_fitness = relative_fitness
        self.relative_rmse = relative_rmse
        self.voxel_values = voxel_values
        self.iter_values = iter_values
        self.rejection_type = rejection_type
        self.k_value = k_value

    def do_registration(self):
        current_trans = self.init_trans
        results = None

        if len(self.iter_values) != len(self.voxel_values):
            return None

        # If sparse clouds were selected, do the initial registration on them
        if self.use_corresponding:
            sparse_pc1 = load_sparse_pc(self.sparse_first_path)
            sparse_pc2 = load_sparse_pc(self.sparse_second_path)

            if not sparse_pc1 or not sparse_pc2:
                return None

            # Use first correspondence and iterations from list
            sparse_result = do_icp_registration(sparse_pc1, sparse_pc2, current_trans, self.registration_type,
                                                self.voxel_values[0], self.relative_fitness,
                                                self.relative_rmse, self.iter_values[0],
                                                self.rejection_type, self.k_value)
            current_trans = sparse_result.transformation

        for scale in range(len(self.iter_values)):
            max_iter = self.iter_values[scale]
            radius = self.voxel_values[scale]

            source_down = self.pc1.voxel_down_sample(radius)
            target_down = self.pc2.voxel_down_sample(radius)

            source_down.estimate_normals(
                o3d.geometry.KDTreeSearchParamHybrid(radius=radius * 2, max_nn=30))
            target_down.estimate_normals(
                o3d.geometry.KDTreeSearchParamHybrid(radius=radius * 2, max_nn=30))

            try:
                results = do_icp_registration(source_down, target_down, current_trans, self.registration_type,
                                          radius, self.relative_fitness, self.relative_rmse, max_iter,
                                          self.rejection_type, self.k_value)
            except RuntimeError as e:
                error_str = str(e)
                error_str += f"\nSource: \"{str(source_down)}\"\nTarget: \"{str(target_down)}\""
                self.signal_error_occurred.emit([error_str])
                self.signal_finished.emit()
                return

            current_trans = results.transformation

        registration_data = self.create_dataclass_object(results)
        self.signal_registration_done.emit(results, registration_data)
        self.signal_finished.emit()

    def create_dataclass_object(self, results):
        return MultiScaleRegistrationData(registration_type=self.registration_type.instance_name,
                                          initial_transformation=self.init_trans,
                                          relative_fitness=self.relative_fitness, relative_rmse=self.relative_rmse,
                                          result_fitness=results.fitness, result_inlier_rmse=results.inlier_rmse,
                                          result_transformation=results.transformation,
                                          voxel_values=self.voxel_values, iteration_values=self.iter_values,
                                          used_sparse_clouds=self.use_corresponding)
