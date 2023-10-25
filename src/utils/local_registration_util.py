from enum import Enum

import open3d as o3d


class LocalRegistrationType(Enum):
    def __new__(cls, *args, **kwds):
        value = len(cls.__members__)
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, name):
        self.instance_name = name

    ICP_Point_To_Point = "Point-to-Point ICP"
    ICP_Point_To_Plane = "Point-to-Plane ICP"
    ICP_Color = "Colored ICP"
    ICP_General = "Generalized ICP"


def get_estimation(registration_type):
    match registration_type:
        case LocalRegistrationType.ICP_Point_To_Point:
            return o3d.pipelines.registration.TransformationEstimationPointToPoint()
        case LocalRegistrationType.ICP_Point_To_Plane:
            return o3d.pipelines.registration.TransformationEstimationPointToPlane()
        case LocalRegistrationType.ICP_Color:
            return o3d.pipelines.registration.TransformationEstimationForColoredICP()
        case LocalRegistrationType.ICP_General:
            return o3d.pipelines.registration.TransformationEstimationForGeneralizedICP()


def get_convergence_criteria(relative_fitness, relative_rmse, max_iteration):
    return o3d.pipelines.registration.ICPConvergenceCriteria(relative_fitness, relative_rmse, max_iteration)


def do_icp_registration(point_cloud_first, point_cloud_second, init_transform, registration_type, max_correspondence,
                        relative_fitness, relative_rmse, max_iteration):
    estimation_method = get_estimation(registration_type)
    convergence_criteria = get_convergence_criteria(relative_fitness, relative_rmse, max_iteration)

    match registration_type:
        case LocalRegistrationType.ICP_Point_To_Point | LocalRegistrationType.ICP_Point_To_Plane:
            return o3d.pipelines.registration.registration_icp(point_cloud_first, point_cloud_second,
                                                               max_correspondence, init_transform,
                                                               estimation_method, convergence_criteria)
        case LocalRegistrationType.ICP_Color:
            return o3d.pipelines.registration.registration_colored_icp(point_cloud_first, point_cloud_second,
                                                                       max_correspondence, init_transform,
                                                                       estimation_method, convergence_criteria)
        case LocalRegistrationType.ICP_General:
            return o3d.pipelines.registration.registration_generalized_icp(point_cloud_first, point_cloud_second,
                                                                           max_correspondence, init_transform,
                                                                           estimation_method, convergence_criteria)
        case _:
            return None
