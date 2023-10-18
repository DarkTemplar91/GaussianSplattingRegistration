import argparse
import open3d as o3d
import plyfile
import numpy as np
import copy
from point_cloud_converter import convert_pc_to_open3d_pc, convert_input_pc_to_open3d_pc
import point_cloud_merger


def parse_args():
    parser = argparse.ArgumentParser(
        description="Registers and merges two gaussian splatting point clouds.")

    parser.add_argument("--path_input_first", default=r"inputs/point_cloud_input_1_4.ply")
    parser.add_argument("--path_input_second", default=r"inputs/point_cloud_input_4_1.ply")
    parser.add_argument("--path_trained_first",
                        default=r"inputs/point_cloud_output_1_4.ply")
    parser.add_argument("--path_trained_second",
                        default=r"inputs/lego_full.ply")
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

    # Read in point clouds data with Plyfile
    pc_input_first = plyfile.PlyData.read(PC_INPUT_PATH_FIRST)
    pc_input_second = plyfile.PlyData.read(PC_INPUT_PATH_SECOND)

    # Convert them to open3d point clouds
    o3d_pc_first_input = convert_input_pc_to_open3d_pc(pc_input_first)
    o3d_pc_second_input = convert_input_pc_to_open3d_pc(pc_input_second)

    # Flip one of the point clouds on the vertical axis
    """ flip_matrix = np.array([[-1, 0, 0, -10],
                            [0, 1, 0, 0],
                            [0, 0, -1, -5],
                            [0, 0, 0, 1]])
    R = o3d_pc_first_input.get_rotation_matrix_from_xyz((0, 3 * np.pi / 4, 0))
    rotation_matrix = np.eye(4)
    rotation_matrix[:3, :3] = R
    transform_matrix = rotation_matrix.dot(flip_matrix)
    o3d_pc_first_input.transform(transform_matrix)

    # Display gaussian splatting models as point clouds for debug purposes
    draw_registration_result(o3d_pc_first_input, o3d_pc_second_input, np.identity(4))

    threshold = 5
    voxel_size = 0.5

    # global registration step
    global_transformation = np.identity(4)
    if not SKIP_GLOBAL_REGISTRATION:
        global_transformation = get_transformation_via_global_registration(o3d_pc_first_input, o3d_pc_second_input,
                                                                           voxel_size,
                                                                           GLOBAL_REGISTRATION_TYPE)
    trans_init = global_transformation
    # colored icp
    result_icp = o3d.pipelines.registration.registration_colored_icp(
        o3d_pc_first_input, o3d_pc_second_input, threshold, trans_init,
        o3d.pipelines.registration.TransformationEstimationForColoredICP(),
        o3d.pipelines.registration.ICPConvergenceCriteria(relative_fitness=1e-6,
                                                          relative_rmse=1e-6,
                                                          max_iteration=50))

    print("Transformation is:")
    print(result_icp.transformation)
    dist = get_distance_between_pcs(o3d_pc_first_input, o3d_pc_second_input, result_icp.transformation)
    print("Distance:", dist)

    draw_registration_result(o3d_pc_first_input, o3d_pc_second_input,
                             result_icp.transformation)"""

    ######################################################################################################

    init_trans = np.array([[1, 0, 0, -10],
                           [0, 1, 0, 0],
                           [0, 0, 1, -5],
                           [0, 0, 0, 1]])
    R = np.array([[-0.7071067811865475, 0, 0.7071067811865476],
         [0, 1, 0],
         [-0.7071067811865475, 0, -0.7071067811865475]])
    rotation_matrix = np.eye(4)
    rotation_matrix[:3, :3] = R
    rotation_matrix[3, 3] = 1
    init_trans = np.dot(init_trans, rotation_matrix)
    # Read in point clouds data with Plyfile
    # pc_trained_first = plyfile.PlyData.read(PC_TRAINED_PATH_FIRST)
    pc_trained_second = plyfile.PlyData.read(PC_TRAINED_PATH_SECOND)
    point_cloud_merger.transform_point_cloud(pc_trained_second, R)

    plyfile.PlyData.write(pc_trained_second, OUTPUT_PATH)
    # merge_point_clouds(pc_trained_first, pc_trained_first,OUTPUT_PATH, transform_matrix )
    # o3d_pc_first_trained = convert_pc_to_open3d_pc(pc_trained_first)
    # o3d_pc_second_trained = convert_pc_to_open3d_pc(pc_trained_second)

    # o3d_pc_second_trained.transform(transform_matrix)

    # print("Use transformation of input point cloud: ")
    """draw_registration_result(o3d_pc_first_trained, o3d_pc_second_trained,
                             trans_init)

    # Local registration methods
    # Point-to-Point ICP
    print("Point-to-Point")
    reg_p2p = o3d.pipelines.registration.registration_icp(
        o3d_pc_first_trained, o3d_pc_second_trained, threshold, trans_init,
        o3d.pipelines.registration.TransformationEstimationPointToPoint())

    print("Transformation is:")
    print(reg_p2p.transformation)
    dist = get_distance_between_pcs(o3d_pc_first_trained, o3d_pc_second_trained, reg_p2p.transformation)
    print("Distance:", dist)
    draw_registration_result(o3d_pc_first_trained, o3d_pc_second_trained, reg_p2p.transformation)

    # Point-to-Plane
    print("Point-to-Plane")
    reg_p2l = o3d.pipelines.registration.registration_icp(
        o3d_pc_first_trained, o3d_pc_second_trained, threshold, trans_init,
        o3d.pipelines.registration.TransformationEstimationPointToPlane())
    print("Transformation is:")
    print(reg_p2l.transformation)
    dist = get_distance_between_pcs(o3d_pc_first_trained, o3d_pc_second_trained, reg_p2l.transformation)
    print("Distance:", dist)
    draw_registration_result(o3d_pc_first_trained, o3d_pc_second_trained, reg_p2l.transformation)

    # Point-to-Plane with robust kernel optimization
    print("Point-to-plane with robust kernel")
    sigma = 6  # standard deviation
    loss = o3d.pipelines.registration.TukeyLoss(k=sigma)
    print("Using robust loss:", loss)
    p2l = o3d.pipelines.registration.TransformationEstimationPointToPlane(loss)
    reg_p2l_kernel = o3d.pipelines.registration.registration_icp(o3d_pc_first_trained, o3d_pc_second_trained,
                                                                 threshold, trans_init,
                                                                 p2l)
    print("Transformation is:")
    print(reg_p2l_kernel.transformation)
    dist = get_distance_between_pcs(o3d_pc_first_trained, o3d_pc_second_trained, reg_p2l_kernel.transformation)
    print("Distance:", dist)
    draw_registration_result(o3d_pc_first_trained, o3d_pc_second_trained, reg_p2l_kernel.transformation)

    # colored icp
    print("Colored ICP")
    result_icp = o3d.pipelines.registration.registration_colored_icp(
        o3d_pc_first_trained, o3d_pc_second_trained, threshold, trans_init,
        o3d.pipelines.registration.TransformationEstimationForColoredICP(),
        o3d.pipelines.registration.ICPConvergenceCriteria(relative_fitness=1e-6,
                                                          relative_rmse=1e-6,
                                                          max_iteration=50))

    print("Transformation is:")
    print(result_icp.transformation)
    dist = get_distance_between_pcs(o3d_pc_first_trained, o3d_pc_second_trained, result_icp.transformation)
    print("Distance:", dist)

    draw_registration_result(o3d_pc_first_trained, o3d_pc_second_trained,
                             result_icp.transformation)

    # Generalized icp
    print("Generalized ICP")
    result_icp = o3d.pipelines.registration.registration_generalized_icp(
        o3d_pc_first_trained, o3d_pc_second_trained, threshold, trans_init,
        o3d.pipelines.registration.TransformationEstimationForGeneralizedICP(),
        o3d.pipelines.registration.ICPConvergenceCriteria(relative_fitness=1e-6,
                                                          relative_rmse=1e-6,
                                                          max_iteration=50))

    print("Transformation is:")
    print(result_icp.transformation)
    dist = get_distance_between_pcs(o3d_pc_first_trained, o3d_pc_second_trained, result_icp.transformation)
    print("Distance:", dist)

    draw_registration_result(o3d_pc_first_trained, o3d_pc_second_trained,
                             result_icp.transformation)"""
