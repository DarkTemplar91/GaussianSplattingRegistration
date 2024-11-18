from gui.workers.qt_base_worker import BaseWorker
from utils.plane_fitting_util import fit_plane, get_o3d_plane, fit_multiple_planes


class PlaneFittingWorker(BaseWorker):
    class ResultData:
        def __init__(self, planes_pc1, indices_pc1, planes_pc2, indices_pc2):
            self.planes_pc1 = planes_pc1
            self.indices_pc1 = indices_pc1
            self.planes_pc2 = planes_pc2
            self.indices_pc2 = indices_pc2

    def __init__(self, pc1, pc2, plane_count, iterations, threshold, min_sample_distance):
        super().__init__()
        self.pc1 = pc1
        self.pc2 = pc2
        self.iterations = iterations
        self.threshold = threshold
        self.min_sample_distance = min_sample_distance
        self.plane_count = plane_count

    def run(self):
        self.signal_progress.emit(0)
        planes_pc1, indices_pc1 = fit_multiple_planes(self.pc1, self.plane_count, self.iterations,
                                                      self.threshold, self.min_sample_distance)

        self.signal_progress.emit(50)
        planes_pc2, indices_pc2 = fit_multiple_planes(self.pc2, self.plane_count, self.iterations,
                                                      self.threshold, self.min_sample_distance)

        self.signal_progress.emit(100)
        self.signal_result.emit(PlaneFittingWorker.ResultData(
            planes_pc1, indices_pc1, planes_pc2, indices_pc2
        ))
        self.signal_finished.emit()

