import torch
from PySide6.QtCore import Signal, QThread

from src.gui.workers.qt_base_worker import BaseWorker
from src.models.gaussian_model import GaussianModel
from src.utils.file_loader import load_sparse_pc, load_o3d_pc, save_point_clouds_to_cache, \
    load_plyfile_pc, is_point_cloud_gaussian, load_gaussian_pc
from src.utils.point_cloud_converter import convert_gs_to_open3d_pc


class PointCloudLoaderInput(BaseWorker):
    def __init__(self, point_cloud):
        super().__init__()
        self.point_cloud = point_cloud

    def run(self):
        result = load_sparse_pc(self.point_cloud)
        self.signals.result.emit(self.worker_id, result)
        self.signals.finished.emit()


class PointCloudLoaderGaussian(BaseWorker):
    def __init__(self, point_cloud):
        super().__init__()
        self.point_cloud = point_cloud

    def run(self):
        result = load_gaussian_pc(self.point_cloud)
        self.signals.result.emit(self.worker_id, result)
        self.signals.finished.emit()


class PointCloudLoaderO3D(QThread):
    result_signal = Signal(object, object)

    def __init__(self, point_cloud1, point_cloud2):
        super().__init__()
        self.point_cloud1 = point_cloud1
        self.point_cloud2 = point_cloud2

    def run(self):
        result1 = load_o3d_pc(self.point_cloud1)
        result2 = load_o3d_pc(self.point_cloud2)

        self.result_signal.emit(result1, result2)


class PointCloudSaver(QThread):

    def __init__(self, point_cloud1, point_cloud2):
        super().__init__()
        self.point_cloud1 = point_cloud1
        self.point_cloud2 = point_cloud2

    def run(self):
        save_point_clouds_to_cache(self.point_cloud1, self.point_cloud2)
