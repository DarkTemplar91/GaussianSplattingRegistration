from enum import Enum

import open3d as o3d


class GlobalRegistrationType(Enum):
    def __new__(cls, *args, **kwds):
        value = len(cls.__members__)
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, name):
        self.instance_name = name

    RANSAC = "RANSAC"
    FGR = "Fast global registration"


class RANSACEstimationMethod(Enum):
    def __new__(cls, *args, **kwds):
        value = len(cls.__members__)
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, name):
        self.instance_name = name

    TransformationEstimationPointToPoint = "Point-To-Point"
    TransformationEstimationPointToPlane = "Point-To-Plane"
    TransformationEstimationForGeneralizedICP = "For Generalized ICP"
    TransformationEstimationForColoredICP = "For Colored ICP"


def get_estimation_method_from_enum(estimation_method):
    match estimation_method:
        case RANSACEstimationMethod.TransformationEstimationPointToPoint:
            return o3d.pipelines.registration.TransformationEstimationPointToPoint()
        case RANSACEstimationMethod.TransformationEstimationPointToPlane:
            return o3d.pipelines.registration.TransformationEstimationPointToPlane()
        case RANSACEstimationMethod.TransformationEstimationForGeneralizedICP:
            return o3d.pipelines.registration.TransformationEstimationForColoredICP()
        case RANSACEstimationMethod.TransformationEstimationForColoredICP:
            return o3d.pipelines.registration.TransformationEstimationForGeneralizedICP()


def do_ransac_registration(point_cloud_first, point_cloud_second, voxel_size, mutual_filter, max_correspondence,
                           estimation_method=RANSACEstimationMethod.TransformationEstimationPointToPoint, ransac_n=3,
                           checkers=None, max_iteration=100000, confidence=0.999):
    source_down, source_fpfh = preprocess_point_cloud(point_cloud_first, voxel_size)
    target_down, target_fpfh = preprocess_point_cloud(point_cloud_second, voxel_size)
    real_estimation_method = get_estimation_method_from_enum(estimation_method)
    result = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(
        source_down, target_down, source_fpfh, target_fpfh, mutual_filter,
        max_correspondence,
        real_estimation_method,
        ransac_n,
        checkers, o3d.pipelines.registration.RANSACConvergenceCriteria(max_iteration, confidence))

    return result


def do_fgr_registration(point_cloud_first, point_cloud_second, voxel_size, division_factor=1.4, use_absolute_scale=False,
                        decrease_mu=False, maximum_correspondence=0.025,
                        max_iterations=64, tuple_scale=0.95, max_tuple_count=1000, tuple_test=True):
    source_down, source_fpfh = preprocess_point_cloud(point_cloud_first, voxel_size)
    target_down, target_fpfh = preprocess_point_cloud(point_cloud_second, voxel_size)

    options = o3d.pipelines.registration.FastGlobalRegistrationOption(division_factor, use_absolute_scale,
                                                                      decrease_mu,maximum_correspondence,
                                                                      max_iterations, tuple_scale,
                                                                      max_tuple_count, tuple_test)

    result = o3d.pipelines.registration.registration_fgr_based_on_feature_matching(source_down, target_down,
                                                                                   source_fpfh,
                                                                                   target_fpfh, options)

    return result


def preprocess_point_cloud(pcd, voxel_size):
    print(":: Downsample with a voxel size %.3f." % voxel_size)
    pcd_down = pcd.voxel_down_sample(voxel_size)

    radius_normal = voxel_size * 2
    print(":: Estimate normal with search radius %.3f." % radius_normal)
    pcd_down.estimate_normals(
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, max_nn=30))

    radius_feature = voxel_size * 5
    print(":: Compute FPFH feature with search radius %.3f." % radius_feature)
    pcd_fpfh = o3d.pipelines.registration.compute_fpfh_feature(
        pcd_down,
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_feature, max_nn=100))
    return pcd_down, pcd_fpfh
