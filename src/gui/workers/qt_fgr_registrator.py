import copy

from PyQt5.QtCore import QObject, pyqtSignal

from src.utils.global_registration_util import do_ransac_registration, do_fgr_registration
from src.utils.local_registration_util import do_icp_registration


class FGRRegistrator(QObject):
    signal_finished = pyqtSignal()
    signal_registration_done = pyqtSignal(object)

    def __init__(self, pc1, pc2, init_transformation,
                 voxel_size, division_factor, use_absolute_scale, decrease_mu, maximum_correspondence,
                 max_iterations, tuple_scale, max_tuple_count, tuple_test):
        super().__init__()

        self.pc1 = copy.deepcopy(pc1)
        self.pc2 = copy.deepcopy(pc2)
        self.pc2.transform(init_transformation)

        self.voxel_size = voxel_size
        self.division_factor = division_factor
        self.use_absolute_scale = use_absolute_scale
        self.decrease_mu = decrease_mu
        self.maximum_correspondence = maximum_correspondence
        self.max_iteration = max_iterations
        self.tuple_scale = tuple_scale
        self.max_tuple_count = max_tuple_count
        self.tuple_test = tuple_test

    def do_registration(self):
        results = do_fgr_registration(self.pc1, self.pc2, self.voxel_size,
                                      self.division_factor,
                                      self.use_absolute_scale,
                                      self.decrease_mu,
                                      self.maximum_correspondence,
                                      self.max_iteration,
                                      self.tuple_scale,
                                      self.max_tuple_count,
                                      self.tuple_test)

        self.signal_registration_done.emit(results)
        self.signal_finished.emit()
