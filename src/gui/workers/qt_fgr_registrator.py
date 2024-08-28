import copy

from PySide6.QtCore import QObject, Signal

from src.gui.workers.qt_base_worker import BaseWorker
from src.utils.global_registration_util import do_fgr_registration


class FGRRegistrator(BaseWorker):

    def __init__(self, pc1, pc2, init_transformation,
                 voxel_size, division_factor, use_absolute_scale, decrease_mu, maximum_correspondence,
                 max_iterations, tuple_scale, max_tuple_count, tuple_test):
        super().__init__()

        self.pc1 = copy.deepcopy(pc1)
        self.pc2 = copy.deepcopy(pc2)
        self.pc1.transform(init_transformation)

        self.voxel_size = voxel_size
        self.division_factor = division_factor
        self.use_absolute_scale = use_absolute_scale
        self.decrease_mu = decrease_mu
        self.maximum_correspondence = maximum_correspondence
        self.max_iteration = max_iterations
        self.tuple_scale = tuple_scale
        self.max_tuple_count = max_tuple_count
        self.tuple_test = tuple_test

    def run(self):
        results = do_fgr_registration(self.pc1, self.pc2, self.voxel_size,
                                      self.division_factor,
                                      self.use_absolute_scale,
                                      self.decrease_mu,
                                      self.maximum_correspondence,
                                      self.max_iteration,
                                      self.tuple_scale,
                                      self.max_tuple_count,
                                      self.tuple_test)

        self.signal_result.emit(results)
        self.signal_progress.emit(100)
        self.signal_finished.emit()
