import copy

from PyQt5.QtCore import QObject, pyqtSignal

from src.utils.file_loader import load_sparse_pc
from src.utils.local_registration_util import do_icp_registration

import open3d as o3d

class MultiScaleRegistrator(QObject):
    signal_finished = pyqtSignal()
    signal_registration_done = pyqtSignal(object)

    def __init__(self, pc1, pc2, init_trans, use_corresponding, sparse_first, sparse_second, registration_type,
                 relative_fitness, relative_rmse, voxel_values, iter_values):
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
                                                self.relative_rmse, self.iter_values[0])
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

            results = do_icp_registration(source_down, target_down, current_trans, self.registration_type,
                                          radius, self.relative_fitness, self.relative_rmse, max_iter)

            current_trans = results.transformation

        self.signal_registration_done.emit(results)
        self.signal_finished.emit()
