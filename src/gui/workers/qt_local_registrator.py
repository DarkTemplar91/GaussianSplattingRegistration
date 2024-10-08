import copy

from PySide6.QtCore import Signal

from src.gui.workers.qt_base_worker import BaseWorker
from src.models.registration_data import LocalRegistrationData
from src.utils.local_registration_util import do_icp_registration


class LocalRegistrator(BaseWorker):
    signal_registration_done = Signal(object, object)

    class ResultData:
        def __init__(self, result, registration_data: LocalRegistrationData):
            self.result = result
            self.registration_data = registration_data

    def __init__(self, pc1, pc2, init_trans, registration_type, max_correspondence,
                 relative_fitness, relative_rmse, max_iteration, rejection_type, k_value):
        super().__init__()

        self.pc1 = copy.deepcopy(pc1)
        self.pc2 = copy.deepcopy(pc2)
        self.init_trans = init_trans
        self.registration_type = registration_type
        self.max_correspondence = max_correspondence
        self.relative_fitness = relative_fitness
        self.relative_rmse = relative_rmse
        self.max_iteration = max_iteration
        self.rejection_type = rejection_type
        self.k_value = k_value

    def run(self):
        results = do_icp_registration(self.pc1, self.pc2, self.init_trans, self.registration_type,
                                      self.max_correspondence, self.relative_fitness,
                                      self.relative_rmse, self.max_iteration, self.rejection_type, self.k_value)

        dataclass = self.create_dataclass_object(results)
        self.signal_result.emit(LocalRegistrator.ResultData(results, dataclass))
        self.signal_progress.emit(100)
        self.signal_finished.emit()

    def create_dataclass_object(self, results):
        return LocalRegistrationData(registration_type=self.registration_type.instance_name,
                                     initial_transformation=self.init_trans,
                                     relative_fitness=self.relative_fitness, relative_rmse=self.relative_rmse,
                                     result_fitness=results.fitness, result_inlier_rmse=results.inlier_rmse,
                                     result_transformation=results.transformation,
                                     max_correspondence=self.max_correspondence, max_iteration=self.max_iteration)
