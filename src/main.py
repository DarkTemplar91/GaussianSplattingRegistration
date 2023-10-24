import argparse
import copy

import open3d as o3d

import sys

import qdarkstyle
from PyQt5.QtWidgets import QApplication

from src.gui.windows.main_window import RegistrationMainWindow


def parse_args():
    parser = argparse.ArgumentParser(
        description="Registers and merges two gaussian splatting point clouds.")

    parser.add_argument("--path_input_first", default=r"inputs/point_cloud_input_1_4.ply")
    parser.add_argument("--path_input_second", default=r"inputs/point_cloud_input_4_1.ply")
    parser.add_argument("--path_trained_first",
                        default=r"inputs/point_cloud_output_1_4.ply")
    parser.add_argument("--path_trained_second",
                        default=r"inputs/point_cloud_output_4_1.ply")
    parser.add_argument("--output_path",
                        default=r"D:\Egyetem\Szakdoga\Data\merged\point_cloud\iteration_30000\point_cloud.ply")
    parser.add_argument("--skip_global", type=bool, default=True)
    parser.add_argument("--global_type", default="default", choices=["default", "fast"])

    return parser.parse_args()


def draw_registration_result(source, target, transformation):
    source_temp = copy.deepcopy(source)
    target_temp = copy.deepcopy(target)
    source_temp.paint_uniform_color([1, 0.706, 0])
    target_temp.paint_uniform_color([0, 0.651, 0.929])
    source_temp.transform(transformation)
    o3d.visualization.draw_geometries([source_temp, target_temp],
                                      front=[0.40648211543911156, -0.18065156055133727, -0.89562118303360339],
                                      lookat=[11.006812205225044, -1.5071142478901485, 17.852610647634339],
                                      up=[-0.12362031294752304, -0.98211815580530604, 0.14199276835226923],
                                      zoom=0.25999999999999951)


def get_transformation_via_global_registration(source, target, voxel_size, global_registration_type):
    source_down, source_fpfh = preprocess_point_cloud(source, voxel_size)
    target_down, target_fpfh = preprocess_point_cloud(target, voxel_size)

    if global_registration_type == "default":
        result = execute_global_registration_default(source_down, target_down, source_fpfh, target_fpfh, voxel_size)
    else:
        result = execute_global_registration_fast(source_down, target_down, source_fpfh, target_fpfh, voxel_size)

    print("Global registration done!")
    print(result.transformation)
    return result.transformation


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


def execute_global_registration_default(source_down, target_down, source_fpfh, target_fpfh, voxel_size):
    distance_threshold = voxel_size * 1.5
    print(":: RANSAC registration on downsampled point clouds.")
    print("   Since the downsampling voxel size is %.3f," % voxel_size)
    print("   we use a liberal distance threshold %.3f." % distance_threshold)
    result = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(
        source_down, target_down, source_fpfh, target_fpfh, True,
        distance_threshold,
        o3d.pipelines.registration.TransformationEstimationPointToPoint(False),
        3, [
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnEdgeLength(
                0.9),
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnDistance(
                distance_threshold)
        ], o3d.pipelines.registration.RANSACConvergenceCriteria(100000, 0.999))
    return result


def execute_global_registration_fast(source_down, target_down, source_fpfh, target_fpfh, voxel_size):
    distance_threshold = voxel_size * 0.5
    print(":: Apply fast global registration with distance threshold %.3f"
          % distance_threshold)
    result = o3d.pipelines.registration.registration_fgr_based_on_feature_matching(
        source_down, target_down, source_fpfh, target_fpfh,
        o3d.pipelines.registration.FastGlobalRegistrationOption(
            maximum_correspondence_distance=distance_threshold))
    return result


# Calculates the chamfer distance between two point clouds
def get_distance_between_pcs(pcd1, pcd2, transformation):
    source_temp = copy.deepcopy(pcd1)
    target_temp = copy.deepcopy(pcd2)
    target_temp.transform(transformation)
    distances = source_temp.compute_point_cloud_distance(target_temp)
    distances.extend(target_temp.compute_point_cloud_distance(source_temp))

    chamfer_dist = sum(map(lambda n: n * n, distances))
    return chamfer_dist


# TODO: Lay out the main pipeline in code:
# 1. Read in files
# 2. Convert them to the proper format
# (1-2.) If possible use cached results
# 3. If enabled do registration on input data
# 4. Do registration on output data
# 5. Merge the point clouds


if __name__ == '__main__':
    args = parse_args()
    PC_INPUT_PATH_FIRST = args.path_input_first
    PC_INPUT_PATH_SECOND = args.path_input_second
    PC_TRAINED_PATH_FIRST = args.path_trained_first
    PC_TRAINED_PATH_SECOND = args.path_trained_second
    OUTPUT_PATH = args.output_path
    SKIP_GLOBAL_REGISTRATION = args.skip_global
    GLOBAL_REGISTRATION_TYPE = args.global_type

    app = QApplication([])
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    form = RegistrationMainWindow()
    form.show()
    sys.exit(app.exec())
