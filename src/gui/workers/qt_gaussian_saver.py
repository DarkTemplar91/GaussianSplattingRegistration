import torch

from src.gui.workers.qt_base_worker import BaseWorker


class GaussianSaver(BaseWorker):

    def __init__(self, gaussian, path):
        super().__init__()
        self.gaussian = gaussian
        self.path = path

    def run(self):
        torch.cuda.empty_cache()
        self.gaussian.save_ply(self.path)
        del self.gaussian
        torch.cuda.empty_cache()
        self.signal_progress.emit(100)
        self.signal_finished.emit()
