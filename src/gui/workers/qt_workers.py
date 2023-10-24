from PyQt5.QtCore import QThread, pyqtSignal

from src.utils.file_loader import load_sparse_pc, load_gaussian_pc, load_o3d_pc, save_point_clouds_to_cache


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
    result_signal = pyqtSignal(object, object)

    def __init__(self, point_cloud1, point_cloud2):
        super().__init__()
        self.point_cloud1 = point_cloud1
        self.point_cloud2 = point_cloud2

    def run(self):
        result1 = load_gaussian_pc(self.point_cloud1)
        result2 = load_gaussian_pc(self.point_cloud2)

        self.result_signal.emit(result1, result2)


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
