import json

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal
import mixture_bind
from kornia.color import rgb_to_lab

from src.utils.graphics_utils import sh2rgb

from src.models.gaussian_mixture_level import GaussianMixtureModel


class GaussianMixtureWorker(QObject):
    signal_finished = pyqtSignal()
    signal_mixture_created = pyqtSignal(list, list)

    signal_update_progress = pyqtSignal(int)

    def __init__(self, pc1, pc2, hem_reduction, distance_delta, color_delta, cluster_level):
        super().__init__()

        self.hem_reduction = hem_reduction
        self.distance_delta = distance_delta
        self.color_delta = color_delta
        self.cluster_level = cluster_level

        self.gaussian_pc_first = pc1
        self.gaussian_pc_second = pc2

        self.current_progress = 0
        self.max_progress = 6
        self.signal_cancel = False

    def execute(self):

        mixture_model_first = GaussianMixtureModel()
        mixture_model_first.cluster_level = self.cluster_level
        mixture_model_first.hem_reduction = self.hem_reduction
        mixture_model_first.distance_delta = self.distance_delta
        mixture_model_first.color_delta = self.color_delta
        mixture_model_first.xyz = self.gaussian_pc_first.get_xyz.detach().cpu().tolist()
        """features_first = self.gaussian_pc_first.get_features.detach()
        mixture_model_first.colors = rgb_to_lab(sh2rgb(features_first[0:3].cpu()
                                                       .view(-1, 3, 1, 1))).view(-1, 3).tolist()
        mixture_model_first.features = features_first[3:].cpu().tolist()
        mixture_model_first.colors = rgb_to_lab(sh2rgb(self.gaussian_pc_first.get_colors.detach().cpu()
                                                       .view(-1, 3, 1, 1))).view(-1, 3).tolist()"""
        mixture_model_first.colors = self.gaussian_pc_first.get_colors.detach().cpu().tolist()

        mixture_model_first.opacities = self.gaussian_pc_first.get_raw_opacity.detach().cpu().view(-1).tolist()
        mixture_model_first.covariance = self.gaussian_pc_first.get_scaled_covariance(1).detach().cpu().tolist()

        mixture_model_second = GaussianMixtureModel()
        mixture_model_second.cluster_level = self.cluster_level
        mixture_model_second.hem_reduction = self.hem_reduction
        mixture_model_second.distance_delta = self.distance_delta
        mixture_model_second.color_delta = self.color_delta
        mixture_model_second.xyz = self.gaussian_pc_second.get_xyz.detach().cpu().tolist()
        """features_second = self.gaussian_pc_first.get_features.detach()
        mixture_model_second.colors = rgb_to_lab(sh2rgb(features_second[0:3].cpu()
                                                        .view(-1, 3, 1, 1))).view(-1, 3).tolist()
        mixture_model_second.features = features_second[3:].cpu().tolist()
        mixture_model_second.colors = rgb_to_lab(sh2rgb(self.gaussian_pc_second.get_colors.detach().cpu()
                                                       .view(-1, 3, 1, 1))).view(-1, 3).tolist()"""
        mixture_model_second.colors = self.gaussian_pc_second.get_colors.detach().cpu().tolist()

        mixture_model_second.opacities = self.gaussian_pc_second.get_raw_opacity.detach().view(-1).cpu().tolist()
        mixture_model_second.covariance = self.gaussian_pc_second.get_scaled_covariance(1).detach().cpu().tolist()
        QtWidgets.QApplication.processEvents()
        if self.signal_cancel:
            return

        json_string_first = json.dumps(mixture_model_first.__dict__)
        #with open('data.json', 'w') as file:
        #    file.write(json_string_first)
        self.update_progress()
        QtWidgets.QApplication.processEvents()
        if self.signal_cancel:
            return

        json_string_second = json.dumps(mixture_model_second.__dict__)
        self.update_progress()
        QtWidgets.QApplication.processEvents()
        if self.signal_cancel:
            return

        print("Creating Gaussian Mixture Model for the first point cloud.")
        result_first = mixture_bind.create_mixture(json_string_first)
        self.update_progress()
        QtWidgets.QApplication.processEvents()
        if self.signal_cancel:
            return

        print("Creating Gaussian Mixture Model for the second point cloud.")
        result_second = mixture_bind.create_mixture(json_string_second)
        self.update_progress()
        QtWidgets.QApplication.processEvents()
        if self.signal_cancel:
            return

        mixture_models_first = json.loads(result_first, object_hook=lambda d: GaussianMixtureModel(**d))
        self.update_progress()
        QtWidgets.QApplication.processEvents()
        if self.signal_cancel:
            return

        mixture_models_second = json.loads(result_second, object_hook=lambda d: GaussianMixtureModel(**d))
        self.update_progress()
        QtWidgets.QApplication.processEvents()
        if self.signal_cancel:
            return

        self.signal_mixture_created.emit(mixture_models_first, mixture_models_second)

    def update_progress(self):
        self.current_progress += 1
        new_percent = int(self.current_progress / self.max_progress * 100)
        self.signal_update_progress.emit(new_percent)

    def cancel(self):
        self.signal_cancel = True
