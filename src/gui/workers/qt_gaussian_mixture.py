import copy

from PyQt5.QtCore import QObject, pyqtSignal

from src.utils.global_registration_util import do_fgr_registration


class GaussianMixtureWorker(QObject):
    signal_finished = pyqtSignal()
    signal_mixture_created = pyqtSignal(object, object)

    def __init__(self, pc1, pc2, hem_reduction, distance_delta, color_delta, cluster_level):
        super().__init__()

        self.pc1 = pc1
        self.pc2 = pc2
        self.hem_reduction = hem_reduction
        self.distance_delta = distance_delta
        self.color_delta = color_delta
        self.cluster_level = cluster_level


    def create_mixture(self):
        pass
