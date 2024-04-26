import json

from PyQt5.QtCore import QObject, pyqtSignal
import mixture_bind

from src.models.gaussian_mixture_level import GaussianMixtureModel


class GaussianMixtureWorker(QObject):
    signal_finished = pyqtSignal()
    signal_mixture_created = pyqtSignal(object, object)

    signal_update_progress = pyqtSignal(int)

    def __init__(self, pc1, pc2, o3pc1, o3pc2, hem_reduction, distance_delta, color_delta, cluster_level):
        super().__init__()

        self.hem_reduction = hem_reduction
        self.distance_delta = distance_delta
        self.color_delta = color_delta
        self.cluster_level = cluster_level

        self.gaussian_pc_first = pc1
        self.gaussian_pc_second = pc2
        self.open3d_pc_first = o3pc1
        self.open3d_pc_first = o3pc2

        self.current_progress = 0
        self.max_progress = self.get_approx_max_progress()


    def create_mixture(self):
        self.execute(self.gaussian_pc_first)
        #self.execute(self.gaussian_point_clouds_second[0])

    def execute(self, gaussian_pc):
        mixture_model = GaussianMixtureModel()
        mixture_model.cluster_level = self.cluster_level
        mixture_model.hem_reduction = self.hem_reduction
        mixture_model.distance_delta = self.distance_delta
        mixture_model.color_delta = self.color_delta
        mixture_model.xyz = gaussian_pc.get_xyz.detach().cpu().tolist()
        mixture_model.colors = gaussian_pc.get_colors.detach().cpu().tolist()
        mixture_model.covariance = gaussian_pc.get_scaled_covariance(1).detach().cpu().tolist()

        json_string = json.dumps(mixture_model.__dict__)
        result = mixture_bind.create_mixture(json_string)
        print(result)



    def update_progress(self):
        self.current_progress += 1
        new_percent = int(self.current_progress / self.max_progress * 100)
        self.signal_update_progress.emit(new_percent)

    def get_approx_max_progress(self):
        num_points = ((self.gaussian_pc_first.get_xyz.shape[0] if self.gaussian_pc_first is not None else 0) +
                      (self.gaussian_pc_second.get_xyz.shape[0] if self.gaussian_pc_second is not None else 0))
        selection_probability = 1 / self.hem_reduction

        return int(num_points * (1-selection_probability**(self.cluster_level + 1)) / (1-selection_probability) - num_points)

