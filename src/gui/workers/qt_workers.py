from PyQt5.QtCore import QThread, pyqtSignal

from src.models.gaussian_model import GaussianModel
from src.utils.file_loader import load_sparse_pc, load_o3d_pc, save_point_clouds_to_cache, \
    load_plyfile_pc
from src.utils.point_cloud_converter import convert_gs_to_open3d_pc


class PointCloudLoaderInput(QThread):
    progress_signal = pyqtSignal(int)
    result_signal = pyqtSignal(object, object)

    def __init__(self, point_cloud1, point_cloud2):
        super().__init__()
        self.point_cloud1 = point_cloud1
        self.point_cloud2 = point_cloud2

    def run(self):
        result1 = load_sparse_pc(self.point_cloud1)
        result2 = load_sparse_pc(self.point_cloud2)

        self.result_signal.emit(result1, result2)


class PointCloudLoaderGaussian(QThread):
    progress_signal = pyqtSignal(int)
    result_signal = pyqtSignal(object, object, object, object)

    def __init__(self, point_cloud1, point_cloud2):
        super().__init__()
        self.point_cloud1 = point_cloud1
        self.point_cloud2 = point_cloud2

    def run(self):
        pc1 = load_plyfile_pc(self.point_cloud1)
        pc2 = load_plyfile_pc(self.point_cloud2)

        original1 = GaussianModel(3)
        original2 = GaussianModel(3)
        original1.from_ply(pc1)
        original2.from_ply(pc2)

        result1 = convert_gs_to_open3d_pc(original1)
        result2 = convert_gs_to_open3d_pc(original2)

        self.result_signal.emit(result1, result2, original1, original2)


class PointCloudLoaderO3D(QThread):
    progress_signal = pyqtSignal(int)
    result_signal = pyqtSignal(object, object)

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
