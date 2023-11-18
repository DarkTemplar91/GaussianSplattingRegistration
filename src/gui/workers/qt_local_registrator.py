import copy

from PyQt5.QtCore import QObject, pyqtSignal

from src.models.registration_data import LocalRegistrationData
from src.utils.local_registration_util import do_icp_registration


class LocalRegistrator(QObject):
    signal_finished = pyqtSignal()
    signal_registration_done = pyqtSignal(object, object)

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

        dataclass = self.create_dataclass_object(results)
        self.signal_registration_done.emit(results, dataclass)
        self.signal_finished.emit()

    def create_dataclass_object(self, results):
        return LocalRegistrationData(registration_type=self.registration_type.instance_name,
                                     initial_transformation=self.init_trans,
                                     relative_fitness=self.relative_fitness, relative_rmse=self.relative_rmse,
                                     result_fitness=results.fitness, result_inlier_rmse=results.inlier_rmse,
                                     result_transformation=results.transformation,
                                     max_correspondence=self.max_correspondence, max_iteration=self.max_iteration)
