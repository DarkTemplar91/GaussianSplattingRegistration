from datetime import datetime
from enum import Enum

import plyfile
import os.path

from src.utils.point_cloud_converter import convert_input_pc_to_open3d_pc, convert_pc_to_open3d_pc
import open3d as o3d

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
    point_cloud_plyfile = load_plyfile_pc(pc_path)
    if not point_cloud_plyfile:
        return None, None

    return convert_pc_to_open3d_pc(point_cloud_plyfile), point_cloud_plyfile


def load_o3d_pc(pc_path):
    if not os.path.isfile(pc_path):
        return None

    return o3d.io.read_point_cloud(pc_path)


def load_plyfile_pc(pc_path):
    if not os.path.isfile(pc_path):
        return None

    point_cloud_plyfile = plyfile.PlyData.read(pc_path)

    pc_type = check_point_cloud_type(point_cloud_plyfile)
    if pc_type is not PointCloudType.gaussian:
        return None

    return point_cloud_plyfile


def check_point_cloud_type(point_cloud):
    props = [p.name for p in point_cloud['vertex'].properties]

    if "red" in props:
        return PointCloudType.input

    if "f_dc_0" in props:
        return PointCloudType.gaussian

    return PointCloudType.unkown


def is_point_cloud_gaussian(point_cloud):
    return check_point_cloud_type(point_cloud) == PointCloudType.gaussian


def save_point_clouds_to_cache(pc_first, pc_second):
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y%m%d%H%M%S")

    working_dir = os.getcwd()

    pc_path_first = os.path.join(working_dir, "cache\\point_cloud_first_" + formatted_time + ".ply")
    pc_path_second = os.path.join(working_dir, "cache\\point_cloud_second_" + formatted_time + ".ply")

    o3d.io.write_point_cloud(pc_path_first, pc_first)
    o3d.io.write_point_cloud(pc_path_second, pc_second)
    return
