from enum import Enum

import plyfile
import os.path

from point_cloud_converter import convert_input_pc_to_open3d_pc, convert_pc_to_open3d_pc

PointCloudType = Enum('PointCloudType', 'input gaussian unknow')


def load_sparse_pc(pc_path):
    if not os.path.isfile(pc_path):
        return None

    point_cloud_plyfile = plyfile.PlyData.read(pc_path)

    pc_type = check_point_cloud_type(point_cloud_plyfile)
    if pc_type is not PointCloudType.input:
        return None

    return convert_input_pc_to_open3d_pc(point_cloud_plyfile)


# TODO: Add tracing
def load_gaussian_pc(pc_path):
    if not os.path.isfile(pc_path):
        return None

    point_cloud_plyfile = plyfile.PlyData.read(pc_path)

    pc_type = check_point_cloud_type(point_cloud_plyfile)
    if pc_type is not PointCloudType.gaussian:
        return None

    return convert_pc_to_open3d_pc(point_cloud_plyfile)


def check_point_cloud_type(point_cloud):
    props = [p.name for p in point_cloud['vertex'].properties]

    if "red" in props:
        return PointCloudType.input

    if "f_dc_0" in props:
        return PointCloudType.gaussian

    return PointCloudType.unkown

