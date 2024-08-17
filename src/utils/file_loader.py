from datetime import datetime
from enum import IntEnum, auto

import plyfile
import os.path

import torch

from src.models.gaussian_model import GaussianModel
from src.utils.point_cloud_converter import convert_input_pc_to_open3d_pc, convert_gs_to_open3d_pc
import open3d as o3d


class PointCloudType(IntEnum):
    GAUSSIAN = auto()
    INPUT = auto()
    UNKNOWN = auto()


def load_sparse_pc(pc_path):
    if not os.path.isfile(pc_path):
        return None

    point_cloud_plyfile = plyfile.PlyData.read(pc_path)

    pc_type = check_point_cloud_type(point_cloud_plyfile)
    if pc_type is not PointCloudType.INPUT:
        return None

    return convert_input_pc_to_open3d_pc(point_cloud_plyfile)


def load_o3d_pc(pc_path):
    if not os.path.isfile(pc_path):
        return None

    return o3d.io.read_point_cloud(pc_path)


def load_plyfile_pc(pc_path):
    if not os.path.isfile(pc_path):
        return None

    point_cloud_plyfile = plyfile.PlyData.read(pc_path)

    pc_type = check_point_cloud_type(point_cloud_plyfile)
    if pc_type is not PointCloudType.GAUSSIAN:
        return None

    return point_cloud_plyfile


def load_gaussian_pc(pc_path):
    torch.cuda.empty_cache()
    plyfile_point_cloud = load_plyfile_pc(pc_path)

    if not is_point_cloud_gaussian(plyfile_point_cloud):
        return None

    gaussian_point_cloud = GaussianModel(device_name="cuda:0")
    gaussian_point_cloud.from_ply(plyfile_point_cloud)
    gaussian_point_cloud.move_to_device("cpu")

    o3d_point_cloud = convert_gs_to_open3d_pc(gaussian_point_cloud)
    torch.cuda.empty_cache()
    return o3d_point_cloud, gaussian_point_cloud


def check_point_cloud_type(point_cloud):
    props = [p.name for p in point_cloud['vertex'].properties]

    if "red" in props:
        return PointCloudType.INPUT

    if "f_dc_0" in props:
        return PointCloudType.GAUSSIAN

    return PointCloudType.UNKNOWN


def is_point_cloud_gaussian(point_cloud):
    if not point_cloud:
        return False

    return check_point_cloud_type(point_cloud) == PointCloudType.GAUSSIAN


def save_point_clouds_to_cache(pc_first, pc_second):
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y%m%d%H%M%S")

    working_dir = os.getcwd()

    pc_path_first = os.path.join(working_dir, "cache\\point_cloud_first_" + formatted_time + ".ply")
    pc_path_second = os.path.join(working_dir, "cache\\point_cloud_second_" + formatted_time + ".ply")

    o3d.io.write_point_cloud(pc_path_first, pc_first)
    o3d.io.write_point_cloud(pc_path_second, pc_second)
    return
