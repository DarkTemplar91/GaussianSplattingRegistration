import torch
from PySide6.QtCore import Signal, QThread

from src.models.gaussian_model import GaussianModel
from src.utils.file_loader import load_sparse_pc, load_o3d_pc, save_point_clouds_to_cache, \
    load_plyfile_pc, is_point_cloud_gaussian
from src.utils.point_cloud_converter import convert_gs_to_open3d_pc


class PointCloudLoaderInput(QThread):
    progress_signal = Signal(int)
    result_signal = Signal(object, object)

    def __init__(self, point_cloud1, point_cloud2):
        super().__init__()
        self.point_cloud1 = point_cloud1
        self.point_cloud2 = point_cloud2

    def run(self):
        result1 = load_sparse_pc(self.point_cloud1)
        result2 = load_sparse_pc(self.point_cloud2)

        self.result_signal.emit(result1, result2)


class PointCloudLoaderGaussian(QThread):
    progress_signal = Signal(int)
    result_signal = Signal(object, object, object, object)

    def __init__(self, point_cloud1, point_cloud2):
        super().__init__()
        self.point_cloud1 = point_cloud1
        self.point_cloud2 = point_cloud2

    def run(self):
        torch.cuda.empty_cache()
        pc1 = load_plyfile_pc(self.point_cloud1)
        pc2 = load_plyfile_pc(self.point_cloud2)

        if not is_point_cloud_gaussian(pc1) or not is_point_cloud_gaussian(pc2):
            self.result_signal.emit(None, None, None, None)
            return

        original1 = GaussianModel(device_name="cuda:0")
        original1.from_ply(pc1)
        original1.move_to_device("cpu")

        original2 = GaussianModel(device_name="cuda:0")
        original2.from_ply(pc2)
        original2.move_to_device("cpu")

        result1 = convert_gs_to_open3d_pc(original1)
        result2 = convert_gs_to_open3d_pc(original2)

        torch.cuda.empty_cache()

        self.result_signal.emit(result1, result2, original1, original2)


class PointCloudLoaderO3D(QThread):
    progress_signal = Signal(int)
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
