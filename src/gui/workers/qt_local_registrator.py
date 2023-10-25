import copy

from PyQt5.QtCore import QObject, pyqtSignal

from src.utils.local_registration_util import do_icp_registration


class LocalRegistrator(QObject):
    signal_finished = pyqtSignal()
    signal_registration_done = pyqtSignal(object)

    def __init__(self, pc1, pc2, init_trans, registration_type, max_correspondence,
                 relative_fitness, relative_rmse, max_iteration):
        super().__init__()

        self.pc1 = copy.deepcopy(pc1)
        self.pc2 = copy.deepcopy(pc2)
        self.init_trans = init_trans
        self.registration_type = registration_type
        self.max_correspondence = max_correspondence
        self.relative_fitness = relative_fitness
        self.relative_rmse = relative_rmse
        self.max_iteration = max_iteration

    def do_registration(self):
        results = do_icp_registration(self.pc1, self.pc2, self.init_trans, self.registration_type,
                                      self.max_correspondence, self.relative_fitness,
                                      self.relative_rmse, self.max_iteration)

        self.signal_registration_done.emit(results)
        self.signal_finished.emit()
