import numpy as np


class BaseLocalRegistrationData(object):
    registration_type: str
    initial_transformation: np.ndarray

    relative_fitness: float
    relative_rmse: float

    is_multi_scale: bool

    # TODO: Add other metrics
    result_fitness: float
    result_inlier_rmse: float
    result_transformation: np.ndarray

    def __init__(self, registration_type, initial_transformation, relative_fitness, relative_rmse, is_multi_scale,
                 result_fitness, result_inlier_rmse, result_transformation):
        super().__init__()
        self.registration_type = registration_type
        self.initial_transformation = initial_transformation
        self.relative_fitness = relative_fitness
        self.relative_rmse = relative_rmse
        self.is_multi_scale = is_multi_scale
        self.result_fitness = result_fitness
        self.result_inlier_rmse = result_inlier_rmse
        self.result_transformation = result_transformation


class LocalRegistrationData(BaseLocalRegistrationData):
    max_correspondence: float
    max_iteration: int

    def __init__(self, registration_type, initial_transformation, relative_fitness, relative_rmse,
                 result_fitness, result_inlier_rmse, result_transformation,
                 max_correspondence, max_iteration):
        super().__init__(registration_type, initial_transformation, relative_fitness, relative_rmse, False,
                         result_fitness, result_inlier_rmse, result_transformation)

        self.max_correspondence = max_correspondence
        self.max_iteration = max_iteration


class MultiScaleRegistrationData(BaseLocalRegistrationData):
    voxel_values: list
    iteration_values: list
    used_sparse_clouds: bool
    used_gaussian_mixtures: bool

    def __init__(self, registration_type, initial_transformation, relative_fitness, relative_rmse,
                 result_fitness, result_inlier_rmse, result_transformation, voxel_values, iteration_values,
                 used_sparse_clouds, used_gaussian_mixtures):
        super().__init__(registration_type, initial_transformation, relative_fitness, relative_rmse, True,
                         result_fitness, result_inlier_rmse, result_transformation)

        self.voxel_values = voxel_values
        self.iteration_values = iteration_values
        self.used_sparse_clouds = used_sparse_clouds
        self.used_gaussian_mixtures = used_gaussian_mixtures
