from gui.workers.qt_base_worker import BaseWorker
from utils.plane_fitting_util import fit_plane, get_o3d_plane


class PlaneFittingWorker(BaseWorker):
    class ResultData:
        def __init__(self, plane_first, plane_second):
            self.plane_first = plane_first
            self.plane_second = plane_second
    def __init__(self, pc1, pc2, iterations, threshold, min_sample_distance):
        super().__init__()
        self.pc1 = pc1
        self.pc2 = pc2
        self.iterations = iterations
        self.threshold = threshold
        self.min_sample_distance = min_sample_distance

    def run(self):
        self.signal_progress.emit(0)
        best_plane_pc1, best_points_pc1, best_indices_pc1 = fit_plane(self.pc1, self.iterations,
                                                                      self.threshold, self.min_sample_distance)
        self.signal_progress.emit(50)
        best_plane_pc2, best_points_pc2, best_indices_pc2 = fit_plane(self.pc2, self.iterations,
                                                                      self.threshold, self.min_sample_distance)
        self.signal_result.emit(PlaneFittingWorker.ResultData(get_o3d_plane(best_plane_pc1, best_points_pc1),
                                                              get_o3d_plane(best_plane_pc2, best_points_pc2)))
        self.signal_progress.emit(100)
        self.signal_finished.emit()

