import copy

from src.gui.workers.qt_base_worker import BaseWorker
from src.utils.global_registration_util import do_ransac_registration


class RANSACRegistrator(BaseWorker):

    def __init__(self, pc1, pc2, init_transformation,
                 voxel_size, mutual_filter, max_correspondence, estimation_method,
                 ransac_n, checkers, max_iteration, confidence):
        super().__init__()

        self.pc1 = copy.deepcopy(pc1)
        self.pc2 = copy.deepcopy(pc2)
        self.pc1.transform(init_transformation)

        self.voxel_size = voxel_size
        self.mutual_filter = mutual_filter
        self.max_correspondence = max_correspondence
        self.estimation_method = estimation_method
        self.ransac_n = ransac_n
        self.checkers = checkers
        self.max_iteration = max_iteration
        self.confidence = confidence

    def run(self):
        results = do_ransac_registration(self.pc1, self.pc2, self.voxel_size,
                                         self.mutual_filter,
                                         self.max_correspondence,
                                         self.estimation_method,
                                         self.ransac_n,
                                         self.checkers,
                                         self.max_iteration,
                                         self.confidence)

        self.signal_result.emit(results)
        self.signal_progress.emit(100)
        self.signal_finished.emit()
