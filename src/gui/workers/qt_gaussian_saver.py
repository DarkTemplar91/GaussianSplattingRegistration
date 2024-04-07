import copy

import torch
from PyQt5.QtCore import QObject, pyqtSignal


class GaussianSaver(QObject):
    signal_finished = pyqtSignal()
    signal_registration_done = pyqtSignal(object, object)

    def __init__(self, gaussian, path):
        super().__init__()
        self.gaussian = gaussian
        self.path = path

    def save_gaussian(self):
        torch.cuda.empty_cache()
        self.gaussian.save_ply(self.path)
        del self.gaussian
        torch.cuda.empty_cache()
        self.signal_finished.emit()